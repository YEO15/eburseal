package tn.supcom.eburseal.commun;

import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class IssuedDiplomaTest {

    private static final String ID = "3f2b8c1e-9a4d-4c7b-8e2f-1a2b3c4d5e6f";
    private static final String REF = "ab".repeat(32);
    private static final String KID = "supcom-2026-01";
    private static final String SIG = "A".repeat(86);

    private static IssuedDiploma diploma(String id, String sig) {
        return new IssuedDiploma(id, "supcom", REF, "Licence", 2026, KID, sig);
    }

    @Test
    void validDiplomaIsAccepted() {
        assertEquals("supcom", diploma(ID, SIG).institution());
    }

    /** Anti-IDOR: a guessable sequential id is refused. */
    @Test
    void sequentialIdIsRejected() {
        assertThrows(IllegalArgumentException.class, () -> diploma("1", SIG));
    }

    /** Only UUID version 4 (random) is accepted; here version 1 (time-based). */
    @Test
    void nonRandomUuidIsRejected() {
        assertThrows(IllegalArgumentException.class,
                () -> diploma("3f2b8c1e-9a4d-1c7b-8e2f-1a2b3c4d5e6f", SIG));
    }

    @Test
    void truncatedSignatureIsRejected() {
        assertThrows(IllegalArgumentException.class, () -> diploma(ID, "A".repeat(85)));
    }

    /** Right length but padding characters: still refused. */
    @Test
    void paddedSignatureIsRejected() {
        assertThrows(IllegalArgumentException.class, () -> diploma(ID, "A".repeat(84) + "=="));
    }

    /** Same rules as IssueRequest: a name in clear text is refused here too. */
    @Test
    void nameAsHolderIsRejected() {
        assertThrows(IllegalArgumentException.class,
                () -> new IssuedDiploma(ID, "supcom", "Kouassi Jean", "Licence", 2026, KID, SIG));
    }

    @Test
    void payloadCarriesDomainSeparationType() {
        assertEquals(IssuedDiploma.TYPE, diploma(ID, SIG).signedPayload().get("type"));
    }

    /** A signature cannot sign itself: it is never part of the payload. */
    @Test
    void payloadDoesNotContainSignature() {
        assertFalse(diploma(ID, SIG).signedPayload().containsKey("signature"));
    }

    /** Issuing and verifying must sign/check exactly the same data. */
    @Test
    void payloadIsIdenticalAtIssueAndVerify() {
        Map<String, Object> atIssue = IssuedDiploma.payload(ID, "supcom", KID,
                new IssueRequest(REF, "Licence", 2026));
        assertEquals(atIssue, diploma(ID, SIG).signedPayload());
    }

    /** A modified title gives a different payload, so the signature will no longer match. */
    @Test
    void modifiedTitleChangesPayload() {
        var original = diploma(ID, SIG);
        var forged = new IssuedDiploma(ID, "supcom", REF, "Master", 2026, KID, SIG);
        assertNotEquals(original.signedPayload(), forged.signedPayload());
    }
}