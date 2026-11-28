package tn.supcom.eburseal.security;

/** Rôles applicatifs (cahier des charges § 5, matrice des droits). */
public final class Roles {
    public static final String UTILISATEUR = "UTILISATEUR";
    public static final String ADMINISTRATEUR = "ADMINISTRATEUR";
    public static final String AUDITEUR = "AUDITEUR";
  /** Institution staff allowed to issue diplomas. */
    public static final String ISSUER = "ISSUER";
    private Roles() {
    }
}
