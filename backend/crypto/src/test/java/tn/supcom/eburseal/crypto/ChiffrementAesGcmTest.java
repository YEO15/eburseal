package tn.supcom.eburseal.crypto;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import javax.crypto.AEADBadTagException;
import javax.crypto.KeyGenerator;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class ChiffrementAesGcmTest {

    private static CleVersionnee cle;
    private static final byte[] CLAIR = "Diplôme EburSeal".getBytes(StandardCharsets.UTF_8);

    @BeforeAll
    static void genererCle() throws Exception {
        KeyGenerator kg = KeyGenerator.getInstance("AES");
        kg.init(256);                              // AES-256
        cle = new CleVersionnee("k1", kg.generateKey());
    }

    @Test
    void allerRetourRendLeClairDOrigine() throws Exception {
        var chiffre = ChiffrementAesGcm.chiffrer(cle, CLAIR, "diplome-42");
        assertArrayEquals(CLAIR, ChiffrementAesGcm.dechiffrer(cle, chiffre, "diplome-42"));
    }

    /** Exigence du prof : 100 000 chiffrements, 0 collision de nonce. */
    @Test
    void centMilleChiffrementsSansCollisionDeNonce() throws Exception {
        Set<String> vus = new HashSet<>();
        for (int i = 0; i < 100_000; i++) {
            var chiffre = ChiffrementAesGcm.chiffrer(cle, CLAIR, "diplome-42");
            assertEquals(ChiffrementAesGcm.TAILLE_NONCE, chiffre.nonce().length);
            assertTrue(vus.add(HexFormat.of().formatHex(chiffre.nonce())),
                    "Nonce réutilisé au chiffrement n° " + i);
        }
    }

    /** Test négatif : un octet modifié dans le chiffré → rejet (SR-TST-04). */
    @Test
    void unOctetModifieEstRejete() throws Exception {
        var chiffre = ChiffrementAesGcm.chiffrer(cle, CLAIR, "diplome-42");
        chiffre.donnees()[0] ^= 0x01;              // on inverse un seul bit
        assertThrows(AEADBadTagException.class,
                () -> ChiffrementAesGcm.dechiffrer(cle, chiffre, "diplome-42"));
    }

    /** Test négatif : chiffré recopié sur un autre objet (AAD différente) → rejet. */
    @Test
    void chiffreDeplaceVersUnAutreObjetEstRejete() throws Exception {
        var chiffre = ChiffrementAesGcm.chiffrer(cle, CLAIR, "diplome-42");
        assertThrows(AEADBadTagException.class,
                () -> ChiffrementAesGcm.dechiffrer(cle, chiffre, "diplome-43"));
    }
}