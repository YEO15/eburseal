package tn.supcom.eburseal.crypto;

import tn.supcom.eburseal.commun.IssuedDiploma;
import tn.supcom.eburseal.commun.Verdict;

import java.security.PublicKey;
import java.util.Base64;
import java.util.Map;
import java.util.Objects;

/**
 * Verifies a presented diploma against the trusted public keys.
 * Fail-closed: any doubt or error gives FORGED or UNDETERMINED, never AUTHENTIC.
 */
public final class DiplomaVerifier {

    /** A trusted public key and the ONLY institution it is allowed to sign for. */
    public record TrustedKey(String institution, PublicKey publicKey) {
        public TrustedKey {
            Objects.requireNonNull(institution, "institution");
            Objects.requireNonNull(publicKey, "publicKey");
        }
    }

    private final Map<String, TrustedKey> trustedKeys;   // kid -> trusted key

    public DiplomaVerifier(Map<String, TrustedKey> trustedKeys) {
        this.trustedKeys = Map.copyOf(trustedKeys);
    }

    public Verdict verify(IssuedDiploma diploma) {
        if (diploma == null) {
            return Verdict.UNDETERMINED;
        }
        try {
            TrustedKey trusted = trustedKeys.get(diploma.kid());
            if (trusted == null) {
                return Verdict.UNDETERMINED;                 // unknown key
            }
            if (!trusted.institution().equals(diploma.institution())) {
                return Verdict.FORGED;                       // key used for another institution
            }
            byte[] signature = Base64.getUrlDecoder().decode(diploma.signature());
            boolean valid = SignatureEd25519.verifier(diploma.kid(), trusted.publicKey(),
                    diploma.signedPayload(), new SignatureEd25519.Sceau(diploma.kid(), signature));
            return valid ? Verdict.AUTHENTIC : Verdict.FORGED;
        } catch (RuntimeException e) {
            return Verdict.UNDETERMINED;                     // fail-closed
        }
    }
}