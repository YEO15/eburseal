package tn.supcom.eburseal.crypto;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import tn.supcom.eburseal.commun.IssueRequest;
import tn.supcom.eburseal.commun.IssuedDiploma;

import java.security.KeyPair;
import java.security.PublicKey;
import java.util.Base64;

import static org.junit.jupiter.api.Assertions.*;

class DiplomaIssuerTest {

    private static final String KID = "supcom-2026-01";
    private static final IssueRequest REQUEST =
            new IssueRequest("ab".repeat(32), "Ingénieur en télécommunications", 2026);

    private static KeyPair supcomKeys;
    private static DiplomaIssuer issuer;

    @BeforeAll
    static void setUp() throws Exception {
        supcomKeys = SignatureEd25519.genererPaire();
        issuer = new DiplomaIssuer("supcom", KID, supcomKeys.getPrivate());
    }

    /** Helper: checks a diploma's signature against a public key. */
    private static boolean verify(IssuedDiploma d, PublicKey key) {
        byte[] sig = Base64.getUrlDecoder().decode(d.signature());
        return SignatureEd25519.verifier(KID, key, d.signedPayload(),
                new SignatureEd25519.Sceau(d.kid(), sig));
    }

    @Test
    void issuedDiplomaHasValidSignature() throws Exception {
        assertTrue(verify(issuer.issue(REQUEST), supcomKeys.getPublic()));
    }

    /** The institution comes from the issuer (authenticated user), never from the request. */
    @Test
    void institutionComesFromIssuer() throws Exception {
        assertEquals("supcom", issuer.issue(REQUEST).institution());
    }

    /** Every diploma gets a fresh random id, even for the same data. */
    @Test
    void twoIssuancesHaveDifferentIds() throws Exception {
        assertNotEquals(issuer.issue(REQUEST).diplomaId(), issuer.issue(REQUEST).diplomaId());
    }

    /** Impersonation: another institution's key does not validate a SUP'COM diploma. */
    @Test
    void anotherInstitutionKeyDoesNotVerify() throws Exception {
        PublicKey otherKey = SignatureEd25519.genererPaire().getPublic();
        assertFalse(verify(issuer.issue(REQUEST), otherKey));
    }

    /** Forgery: "Ingénieur" changed into "Master", original signature kept. */
    @Test
    void tamperedTitleBreaksSignature() throws Exception {
        IssuedDiploma real = issuer.issue(REQUEST);
        IssuedDiploma forged = new IssuedDiploma(real.diplomaId(), real.institution(),
                real.holderRef(), "Master", real.year(), real.kid(), real.signature());
        assertFalse(verify(forged, supcomKeys.getPublic()));
    }

    /** Forgery: the year is changed, original signature kept. */
    @Test
    void tamperedYearBreaksSignature() throws Exception {
        IssuedDiploma real = issuer.issue(REQUEST);
        IssuedDiploma forged = new IssuedDiploma(real.diplomaId(), real.institution(),
                real.holderRef(), real.title(), 2020, real.kid(), real.signature());
        assertFalse(verify(forged, supcomKeys.getPublic()));
    }

    @Test
    void missingKeyIsRejected() {
        assertThrows(NullPointerException.class, () -> new DiplomaIssuer("supcom", KID, null));
    }

    @Test
    void missingRequestIsRejected() {
        assertThrows(NullPointerException.class, () -> issuer.issue(null));
    }
}