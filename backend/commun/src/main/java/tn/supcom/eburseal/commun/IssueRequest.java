package tn.supcom.eburseal.commun;

import java.util.Objects;
import java.util.regex.Pattern;

/**
 * Data sent by an issuer to issue a diploma.
 * The holder is identified only by a pseudonymous fingerprint (no name in clear text).
 * The issuing institution is NOT part of the request: it is taken from the authenticated user.
 */
public record IssueRequest(String holderRef, String title, int year) {

    private static final Pattern HOLDER_REF = Pattern.compile("[0-9a-f]{64}");
    private static final Pattern TITLE = Pattern.compile("[\\p{L}\\p{N} .,'()-]{1,120}");
    public static final int MIN_YEAR = 1950;
    public static final int MAX_YEAR = 2100;

    public IssueRequest {
        Objects.requireNonNull(holderRef, "holderRef");
        Objects.requireNonNull(title, "title");
        if (!HOLDER_REF.matcher(holderRef).matches()) {
            throw new IllegalArgumentException("holderRef must be a SHA-256 fingerprint (64 lowercase hex characters)");
        }
        if (!TITLE.matcher(title).matches()) {
            throw new IllegalArgumentException("title has invalid characters or length");
        }
        if (year < MIN_YEAR || year > MAX_YEAR) {
            throw new IllegalArgumentException("year out of range");
        }
    }
}