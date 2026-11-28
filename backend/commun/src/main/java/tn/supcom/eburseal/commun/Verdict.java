package tn.supcom.eburseal.commun;

/**
 * Outcome of a diploma verification.
 * Fail-closed: anything that cannot be proven authentic is never reported as AUTHENTIC.
 */
public enum Verdict {

    /** The signature is valid for the presented data and a known issuer key. */
    AUTHENTIC,

    /** The data or the signature was altered: the signature does not match. */
    FORGED,

    /** The verification could not be completed (unreadable input, unknown key, ...). */
    UNDETERMINED
}