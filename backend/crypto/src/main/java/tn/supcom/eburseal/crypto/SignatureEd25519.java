package tn.supcom.eburseal.crypto;

import java.security.GeneralSecurityException;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.Signature;
import java.util.Objects;

/**
 * SR-NRP-01 — Signature Ed25519 (JCA natif de Java) des octets canonisés JCS.
 * La vérification est fail-closed : tout problème donne « non valide ».
 */
public final class SignatureEd25519 {

    private static final String ALGO = "Ed25519";

    /** Signature détachée : le kid de la clé qui a signé + les 64 octets Ed25519. */
    public record Sceau(String kid, byte[] valeur) {
        public Sceau {
            Objects.requireNonNull(kid, "kid");
            Objects.requireNonNull(valeur, "valeur");
        }
    }

    private SignatureEd25519() {}

    public static KeyPair genererPaire() throws GeneralSecurityException {
        return KeyPairGenerator.getInstance(ALGO).generateKeyPair();
    }

    public static Sceau signer(String kid, PrivateKey cle, Object donnees)
            throws GeneralSecurityException {
        Signature s = Signature.getInstance(ALGO);
        s.initSign(cle);
        s.update(Jcs.canoniser(donnees));
        return new Sceau(kid, s.sign());
    }

    public static boolean verifier(String kidAttendu, PublicKey cle, Object donnees, Sceau sceau) {
        if (!kidAttendu.equals(sceau.kid())) {
            return false;                                  // mauvaise version de clé
        }
        try {
            Signature s = Signature.getInstance(ALGO);
            s.initVerify(cle);
            s.update(Jcs.canoniser(donnees));
            return s.verify(sceau.valeur());
        } catch (GeneralSecurityException | IllegalArgumentException e) {
            return false;                                  // fail-closed
        }
    }
}