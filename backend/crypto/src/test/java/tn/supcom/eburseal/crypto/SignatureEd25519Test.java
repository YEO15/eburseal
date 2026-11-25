package tn.supcom.eburseal.crypto;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.security.KeyPair;
import java.util.LinkedHashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class SignatureEd25519Test {

    private static KeyPair paire;
    // Aucune donnée nominative en clair : le titulaire est une empreinte (SR-CON-04)
    private static final Map<String, Object> DIPLOME =
            Map.of("id", "diplome-42", "titulaire", "empreinte-ab12", "annee", 2026);

    @BeforeAll
    static void genererCles() throws Exception {
        paire = SignatureEd25519.genererPaire();
    }

    @Test
    void allerRetourSignatureValide() throws Exception {
        var sceau = SignatureEd25519.signer("k1", paire.getPrivate(), DIPLOME);
        assertEquals(64, sceau.valeur().length);
        assertTrue(SignatureEd25519.verifier("k1", paire.getPublic(), DIPLOME, sceau));
    }

    /** Grâce à JCS, l'ordre des champs ne change pas la signature. */
    @Test
    void ordreDesChampsSansEffet() throws Exception {
        var sceau = SignatureEd25519.signer("k1", paire.getPrivate(), DIPLOME);
        Map<String, Object> autreOrdre = new LinkedHashMap<>();
        autreOrdre.put("annee", 2026);
        autreOrdre.put("titulaire", "empreinte-ab12");
        autreOrdre.put("id", "diplome-42");
        assertTrue(SignatureEd25519.verifier("k1", paire.getPublic(), autreOrdre, sceau));
    }

    /** SR-TST-04 : une donnée modifiée → rejet. */
    @Test
    void donneeModifieeEstRejetee() throws Exception {
        var sceau = SignatureEd25519.signer("k1", paire.getPrivate(), DIPLOME);
        var falsifie = Map.<String, Object>of("id", "diplome-42", "titulaire", "empreinte-ab12", "annee", 2025);
        assertFalse(SignatureEd25519.verifier("k1", paire.getPublic(), falsifie, sceau));
    }

    /** SR-TST-04 : un octet modifié dans le sceau → rejet. */
    @Test
    void octetDuSceauModifieEstRejete() throws Exception {
        var sceau = SignatureEd25519.signer("k1", paire.getPrivate(), DIPLOME);
        byte[] altere = sceau.valeur().clone();
        altere[0] ^= 0x01;
        var faux = new SignatureEd25519.Sceau("k1", altere);
        assertFalse(SignatureEd25519.verifier("k1", paire.getPublic(), DIPLOME, faux));
    }

    @Test
    void signatureDUneAutreCleEstRejetee() throws Exception {
        var autre = SignatureEd25519.genererPaire();
        var sceau = SignatureEd25519.signer("k1", autre.getPrivate(), DIPLOME);
        assertFalse(SignatureEd25519.verifier("k1", paire.getPublic(), DIPLOME, sceau));
    }

    @Test
    void mauvaisKidEstRejete() throws Exception {
        var sceau = SignatureEd25519.signer("k1", paire.getPrivate(), DIPLOME);
        assertFalse(SignatureEd25519.verifier("k2", paire.getPublic(), DIPLOME, sceau));
    }
}