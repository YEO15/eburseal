/**
 * Squelette de la SPA EburSeal. Règles de sécurité côté client (recueil des besoins) :
 *  - SR-AUT-07 : le jeton d'accès reste en mémoire (jamais localStorage/sessionStorage) ;
 *  - SR-INT-05 : aucun innerHTML / dangerouslySetInnerHTML ;
 *  - SR-CON-05 : le Service Worker ne met jamais en cache les réponses /api/**.
 */
const espaces = [
  { titre: "Vérifier un diplôme", texte: "Déposez un diplôme pour savoir s'il est authentique, intact et émis par l'établissement indiqué." },
  { titre: "Mon portefeuille", texte: "Retrouvez vos diplômes et partagez des copies traçables avec les recruteurs." },
  { titre: "Espace établissement", texte: "Émettez des diplômes infalsifiables, avec double validation." },
];

export default function App() {
  return (
    <main style={{ fontFamily: "system-ui, sans-serif", maxWidth: 880, margin: "0 auto", padding: 16 }}>
      <h1 style={{ color: "#14325C", marginBottom: 4 }}>EburSeal</h1>
      <p style={{ marginTop: 0 }}>Le sceau invisible des diplômes ivoiriens.</p>
      <section style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
        {espaces.map((e) => (
          <article key={e.titre} style={{ border: "1px solid #C5CDD6", borderRadius: 8, padding: 12 }}>
            <h2 style={{ fontSize: 18, margin: "0 0 6px" }}>{e.titre}</h2>
            <p style={{ margin: 0 }}>{e.texte}</p>
          </article>
        ))}
      </section>
    </main>
  );
}
