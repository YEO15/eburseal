## Objet

Besoins / exigences traités : <!-- ex. BF-MED-02, SR-AUZ-02 -->

## Liste de contrôle sécurité (Definition of Done)

- [ ] Les cas d'abus de la fonctionnalité existent et sont testés (SR-TST-04)
- [ ] Chaque nouvel endpoint déclare ses rôles (`@RolesAllowed` / `@PermitAll`) — SR-AUZ-01
- [ ] Contrôle d'appartenance côté serveur sur toute ressource identifiée — SR-AUZ-02
- [ ] Entrées validées (Jakarta Validation), requêtes paramétrées — SR-INT-03/04
- [ ] Aucun secret, mot de passe, jeton ou contenu de message dans les logs — SR-PRV-03
- [ ] Erreurs génériques (RFC 9457), pas de trace de pile — SR-ERR-01
- [ ] Aucun secret ajouté au dépôt — SR-DEP-02
- [ ] CI verte (build, tests, SCA, gitleaks)
- [ ] Recueil des besoins / `docs/exigences.csv` mis à jour si une exigence a changé

## Relecture

Relu par : <!-- l'autre membre du binôme -->
