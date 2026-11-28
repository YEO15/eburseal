package tn.supcom.eburseal.api;

import jakarta.annotation.PostConstruct;
import jakarta.enterprise.context.ApplicationScoped;
import tn.supcom.eburseal.crypto.DiplomaIssuer;
import tn.supcom.eburseal.crypto.DiplomaVerifier;
import tn.supcom.eburseal.crypto.SignatureEd25519;

import java.security.GeneralSecurityException;
import java.security.KeyPair;
import java.util.Map;

/**
 * Provides the issuer and the verifier to the REST resources.
 * TEMPORARY (until task A3): the signing key is generated in memory at startup.
 * It is never written to disk, never logged, never committed; it is lost at restart.
 */
@ApplicationScoped
public class DiplomaKeys {

    static final String INSTITUTION = "supcom";
    static final String KID = "supcom-dev-01";

    private DiplomaIssuer issuer;
    private DiplomaVerifier verifier;

    @PostConstruct
    void init() {
        try {
            KeyPair pair = SignatureEd25519.genererPaire();
            issuer = new DiplomaIssuer(INSTITUTION, KID, pair.getPrivate());
            verifier = new DiplomaVerifier(Map.of(
                    KID, new DiplomaVerifier.TrustedKey(INSTITUTION, pair.getPublic())));
        } catch (GeneralSecurityException e) {
            throw new IllegalStateException("Cannot create the signing key", e);
        }
    }

    public DiplomaIssuer issuer() {
        return issuer;
    }

    public DiplomaVerifier verifier() {
        return verifier;
    }
}