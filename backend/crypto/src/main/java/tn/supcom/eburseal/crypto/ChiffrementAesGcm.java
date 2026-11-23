package tn.supcom.eburseal.crypto;

import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.SecureRandom;

/**
 * SR-CON-02 — Documents chiffrés au repos en AES-256-GCM.
 * Nonce aléatoire de 96 bits à chaque chiffrement ; AAD = identifiant de l'objet.
 */
public final class ChiffrementAesGcm {

    public static final int TAILLE_NONCE = 12;          // 12 octets = 96 bits
    private static final int TAILLE_TAG_BITS = 128;     // étiquette d'authenticité
    private static final String ALGO = "AES/GCM/NoPadding";
    private static final SecureRandom ALEA = new SecureRandom();

    /** Ce qu'on stocke : le kid, le nonce et le chiffré (étiquette incluse). */
    public record Chiffre(String kid, byte[] nonce, byte[] donnees) {}

    private ChiffrementAesGcm() {}

    public static Chiffre chiffrer(CleVersionnee cle, byte[] clair, String idObjet)
            throws GeneralSecurityException {
        byte[] nonce = new byte[TAILLE_NONCE];
        ALEA.nextBytes(nonce);

        Cipher c = Cipher.getInstance(ALGO);
        c.init(Cipher.ENCRYPT_MODE, cle.cle(), new GCMParameterSpec(TAILLE_TAG_BITS, nonce));
        c.updateAAD(idObjet.getBytes(StandardCharsets.UTF_8));
        return new Chiffre(cle.kid(), nonce, c.doFinal(clair));
    }

    public static byte[] dechiffrer(CleVersionnee cle, Chiffre chiffre, String idObjet)
            throws GeneralSecurityException {
        if (!cle.kid().equals(chiffre.kid())) {
            throw new GeneralSecurityException("Clé inattendue pour ce chiffré");
        }
        Cipher c = Cipher.getInstance(ALGO);
        c.init(Cipher.DECRYPT_MODE, cle.cle(), new GCMParameterSpec(TAILLE_TAG_BITS, chiffre.nonce()));
        c.updateAAD(idObjet.getBytes(StandardCharsets.UTF_8));
        return c.doFinal(chiffre.donnees());   // AEADBadTagException si altéré
    }
}