package tn.supcom.eburseal.crypto;

import javax.crypto.SecretKey;
import java.util.Objects;

/** Clé AES-256 identifiée par un kid (prépare la rotation des clés). */
public record CleVersionnee(String kid, SecretKey cle) {

    public CleVersionnee {
        Objects.requireNonNull(kid, "kid");
        Objects.requireNonNull(cle, "cle");
        if (!"AES".equals(cle.getAlgorithm())) {
            throw new IllegalArgumentException("Clé AES attendue");
        }
    }
}