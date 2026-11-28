package tn.supcom.eburseal.crypto;

import tn.supcom.eburseal.commun.IssueRequest;
import tn.supcom.eburseal.commun.IssuedDiploma;

import java.security.GeneralSecurityException;
import java.security.PrivateKey;
import java.util.Base64;
import java.util.Objects;
import java.util.UUID;

/**
 * Issues diplomas for ONE institution, with ONE signing key.
 * The institution is fixed here (from the authenticated issuer), never taken from the request.
 */
public final class DiplomaIssuer {

    private final String institution;
    private final String kid;
    private final PrivateKey signingKey;

    public DiplomaIssuer(String institution, String kid, PrivateKey signingKey) {
        this.institution = Objects.requireNonNull(institution, "institution");
        this.kid = Objects.requireNonNull(kid, "kid");
        this.signingKey = Objects.requireNonNull(signingKey, "signingKey");
    }

    public IssuedDiploma issue(IssueRequest request) throws GeneralSecurityException {
        Objects.requireNonNull(request, "request");
        String diplomaId = UUID.randomUUID().toString();
        var payload = IssuedDiploma.payload(diplomaId, institution, kid, request);
        var seal = SignatureEd25519.signer(kid, signingKey, payload);
        String signature = Base64.getUrlEncoder().withoutPadding().encodeToString(seal.valeur());
        return new IssuedDiploma(diplomaId, institution, request.holderRef(),
                request.title(), request.year(), kid, signature);
    }
}