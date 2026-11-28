package tn.supcom.eburseal.commun;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class IssueRequestTest {

    private static final String VALID_REF = "ab".repeat(32);   // 64 hex characters

    @Test
    void validRequestIsAccepted() {
        var request = new IssueRequest(VALID_REF, "Ingénieur en télécommunications", 2026);
        assertEquals(2026, request.year());
    }

    /** Privacy: a name can never replace the pseudonymous fingerprint. */
    @Test
    void nameInsteadOfFingerprintIsRejected() {
        assertThrows(IllegalArgumentException.class,
                () -> new IssueRequest("Kouassi Jean", "Licence", 2026));
    }

    @Test
    void scriptInTitleIsRejected() {
        assertThrows(IllegalArgumentException.class,
                () -> new IssueRequest(VALID_REF, "<script>alert(1)</script>", 2026));
    }

    /** Log injection (CRLF): line breaks are refused. */
    @Test
    void lineBreakInTitleIsRejected() {
        assertThrows(IllegalArgumentException.class,
                () -> new IssueRequest(VALID_REF, "Licence\r\nFAKE LOG ENTRY", 2026));
    }

    @Test
    void tooLongTitleIsRejected() {
        assertThrows(IllegalArgumentException.class,
                () -> new IssueRequest(VALID_REF, "a".repeat(121), 2026));
    }

    @Test
    void yearOutOfRangeIsRejected() {
        assertThrows(IllegalArgumentException.class,
                () -> new IssueRequest(VALID_REF, "Licence", 3000));
    }

    @Test
    void missingFieldIsRejected() {
        assertThrows(NullPointerException.class,
                () -> new IssueRequest(null, "Licence", 2026));
    }

    /** Error messages never echo the hostile input. */
    @Test
    void errorMessageDoesNotEchoInput() {
        var e = assertThrows(IllegalArgumentException.class,
                () -> new IssueRequest(VALID_REF, "<script>", 2026));
        assertFalse(e.getMessage().contains("<script>"));
    }
}