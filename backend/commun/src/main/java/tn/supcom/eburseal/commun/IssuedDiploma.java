package tn.supcom.eburseal.commun;

import java.util.Map;
import java.util.Objects;
import java.util.regex.Pattern;

/**
 * A diploma signed by its issuing institution.
 * The signed payload is defined in one place only (payload), so issuing and
 * verifying always sign and check exactly the same fields.
 */
public record IssuedDiploma(String diplomaId, String institution, String holderRef,
                            String title, int year, String kid, String signature) {

    /** Domain separation: a signature made for another kind of object can never be replayed here. */
    public static final String TYPE = "eburseal.diploma.v1";

    private static final Pattern UUID_V4 =
            Pattern.compile("[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}");
    private static final Pattern INSTITUTION = Pattern.compile("[a-z0-9-]{2,40}");
    private static final Pattern KID = Pattern.compile("[A-Za-z0-9._-]{1,64}");
    /** Ed25519 signature = 64 bytes = 86 base64url characters without padding. */
    private static final Pattern SIGNATURE = Pattern.compile("[A-Za-z0-9_-]{86}");

    public IssuedDiploma {
        Objects.requireNonNull(diplomaId, "diplomaId");
        Objects.requireNonNull(institution, "institution");
        Objects.requireNonNull(kid, "kid");
        Objects.requireNonNull(signature, "signature");
        new IssueRequest(holderRef, title, year);   // same rules as at issuance
        if (!UUID_V4.matcher(diplomaId).matches()) {
            throw new IllegalArgumentException("diplomaId must be a lowercase UUID v4");
        }
        if (!INSTITUTION.matcher(institution).matches()) {
            throw new IllegalArgumentException("institution has an invalid format");
        }
        if (!KID.matcher(kid).matches()) {
            throw new IllegalArgumentException("kid has an invalid format");
        }
        if (!SIGNATURE.matcher(signature).matches()) {
            throw new IllegalArgumentException("signature must be 86 base64url characters");
        }
    }

    /** The exact data covered by the signature (canonicalized with JCS before signing). */
    public static Map<String, Object> payload(String diplomaId, String institution,
                                              String kid, IssueRequest request) {
        return Map.of(
                "type", TYPE,
                "diplomaId", diplomaId,
                "institution", institution,
                "kid", kid,
                "holderRef", request.holderRef(),
                "title", request.title(),
                "year", request.year());
    }

    /** Payload of this diploma, used at verification time. */
    public Map<String, Object> signedPayload() {
        return payload(diplomaId, institution, kid, new IssueRequest(holderRef, title, year));
    }
}