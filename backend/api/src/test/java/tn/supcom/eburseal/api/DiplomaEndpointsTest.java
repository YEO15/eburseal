package tn.supcom.eburseal.api;

import jakarta.annotation.security.PermitAll;
import jakarta.annotation.security.RolesAllowed;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import tn.supcom.eburseal.commun.IssueRequest;
import tn.supcom.eburseal.commun.IssuedDiploma;
import tn.supcom.eburseal.security.Roles;

import java.util.Map;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class DiplomaEndpointsTest {

    private DiplomaKeys keys;
    private VerifyResource verify;

    @BeforeEach
    void setUp() {
        keys = new DiplomaKeys();
        keys.init();
        verify = new VerifyResource();
        verify.keys = keys;
    }

    private IssuedDiploma issue() throws Exception {
        return keys.issuer().issue(new IssueRequest("ab".repeat(32), "Licence", 2026));
    }

    @Test
    void issuanceIsReservedToIssuers() {
        RolesAllowed roles = DiplomaResource.class.getAnnotation(RolesAllowed.class);
        assertNotNull(roles);
        assertArrayEquals(new String[] {Roles.ISSUER}, roles.value());
        assertFalse(DiplomaResource.class.isAnnotationPresent(PermitAll.class));
    }

    @Test
    void verificationIsPublic() {
        assertTrue(VerifyResource.class.isAnnotationPresent(PermitAll.class));
    }

    @Test
    void genuineDiplomaIsAuthentic() throws Exception {
        assertEquals("AUTHENTIC", verify.verify(issue()).get("verdict"));
    }

    @Test
    void tamperedDiplomaIsForged() throws Exception {
        IssuedDiploma d = issue();
        IssuedDiploma forged = new IssuedDiploma(d.diplomaId(), d.institution(), d.holderRef(),
                "Master", d.year(), d.kid(), d.signature());
        assertEquals("FORGED", verify.verify(forged).get("verdict"));
    }

    @Test
    void emptyBodyIsUndetermined() {
        assertEquals("UNDETERMINED", verify.verify(null).get("verdict"));
    }

    /** Minimisation: the answer never echoes diploma data. */
    @Test
    void answerContainsOnlyTheVerdict() throws Exception {
        Map<String, String> answer = verify.verify(issue());
        assertEquals(Set.of("verdict"), answer.keySet());
    }

    /** After a restart (new keys), old diplomas are no longer recognised. */
    @Test
    void diplomaFromPreviousKeysIsNotAuthentic() throws Exception {
        IssuedDiploma old = issue();
        DiplomaKeys restarted = new DiplomaKeys();
        restarted.init();
        verify.keys = restarted;
        assertNotEquals("AUTHENTIC", verify.verify(old).get("verdict"));
    }
}