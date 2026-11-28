package tn.supcom.eburseal.crypto;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import tn.supcom.eburseal.commun.IssueRequest;
import tn.supcom.eburseal.commun.IssuedDiploma;
import tn.supcom.eburseal.commun.Verdict;

import java.security.KeyPair;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class DiplomaVerifierTest {

    private static final String SUPCOM_KID = "supcom-2026-01";
    private static final String ESATIC_KID = "esatic-2026-01";
    private static final IssueRequest REQUEST =
            new IssueRequest("ab".repeat(32), "Licence", 2026);

    private static KeyPair supcomKeys;
    private static KeyPair esaticKeys;
    private static DiplomaVerifier verifier;

    @BeforeAll
    static void setUp() throws Exception {
        supcomKeys = SignatureEd25519.genererPaire();
        esaticKeys = SignatureEd25519.genererPaire();
        verifier = new DiplomaVerifier(Map.of(
                SUPCOM_KID, new DiplomaVerifier.TrustedKey("supcom", supcomKeys.getPublic()),
                ESATIC_KID, new DiplomaVerifier.TrustedKey("esatic", esaticKeys.getPublic())));
    }

    private static IssuedDiploma supcomDiploma() throws Exception {
        return new DiplomaIssuer("supcom", SUPCOM_KID, supcomKeys.getPrivate()).issue(REQUEST);
    }

    /** Copy of a diploma with another title, original signature kept. */
    private static IssuedDiploma withTitle(IssuedDiploma d, String title) {
        return new IssuedDiploma(d.diplomaId(), d.institution(), d.holderRef(),
                title, d.year(), d.kid(), d.signature());
    }

    @Test
    void genuineDiplomaIsAuthentic() throws Exception {
        assertEquals(Verdict.AUTHENTIC, verifier.verify(supcomDiploma()));
    }

    @Test
    void modifiedTitleIsForged() throws Exception {
        assertEquals(Verdict.FORGED, verifier.verify(withTitle(supcomDiploma(), "Master")));
    }

    /** Impersonation: ESATIC signs a diploma claiming to come from SUP'COM. */
    @Test
    void keyUsedForAnotherInstitutionIsForged() throws Exception {
        IssuedDiploma fake = new DiplomaIssuer("supcom", ESATIC_KID, esaticKeys.getPrivate())
                .issue(REQUEST);
        assertEquals(Verdict.FORGED, verifier.verify(fake));
    }

    /** Attacker signs with his own key under the SUP'COM kid. */
    @Test
    void attackerKeyUnderGenuineKidIsForged() throws Exception {
        KeyPair attacker = SignatureEd25519.genererPaire();
        IssuedDiploma fake = new DiplomaIssuer("supcom", SUPCOM_KID, attacker.getPrivate())
                .issue(REQUEST);
        assertEquals(Verdict.FORGED, verifier.verify(fake));
    }

    /** Unknown key: we cannot prove anything, so never AUTHENTIC. */
    @Test
    void unknownKidIsUndetermined() throws Exception {
        IssuedDiploma unknown = new DiplomaIssuer("supcom", "supcom-1999-01", supcomKeys.getPrivate())
                .issue(REQUEST);
        assertEquals(Verdict.UNDETERMINED, verifier.verify(unknown));
    }

    @Test
    void wellFormedButFakeSignatureIsForged() throws Exception {
        IssuedDiploma d = supcomDiploma();
        IssuedDiploma fake = new IssuedDiploma(d.diplomaId(), d.institution(), d.holderRef(),
                d.title(), d.year(), d.kid(), "A".repeat(86));
        assertEquals(Verdict.FORGED, verifier.verify(fake));
    }

    @Test
    void missingDiplomaIsUndetermined() {
        assertEquals(Verdict.UNDETERMINED, verifier.verify(null));
    }

    /** The key directory cannot be modified after creation. */
    @Test
    void trustedKeysCannotBeAddedLater() throws Exception {
        var keys = new java.util.HashMap<String, DiplomaVerifier.TrustedKey>();
        keys.put(SUPCOM_KID, new DiplomaVerifier.TrustedKey("supcom", supcomKeys.getPublic()));
        var v = new DiplomaVerifier(keys);
        keys.put(ESATIC_KID, new DiplomaVerifier.TrustedKey("esatic", esaticKeys.getPublic()));
        IssuedDiploma esatic = new DiplomaIssuer("esatic", ESATIC_KID, esaticKeys.getPrivate())
                .issue(REQUEST);
        assertEquals(Verdict.UNDETERMINED, v.verify(esatic));
    }
}