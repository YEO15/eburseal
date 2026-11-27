package tn.supcom.eburseal.security;

import jakarta.annotation.security.DenyAll;
import jakarta.annotation.security.PermitAll;
import jakarta.annotation.security.RolesAllowed;
import jakarta.ws.rs.DELETE;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.HEAD;
import jakarta.ws.rs.PATCH;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.PUT;
import jakarta.ws.rs.Path;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.lang.annotation.Annotation;
import java.lang.reflect.AnnotatedElement;
import java.lang.reflect.Method;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * SR-AUZ-01 — refus par défaut : le build échoue si une méthode de ressource
 * Jakarta REST ne déclare ni @RolesAllowed, ni @PermitAll, ni @DenyAll
 * (sur la méthode ou sur sa classe).
 */
class AccessControlDeclarationTest {

    private static final String BASE_PACKAGE = "tn.supcom.eburseal";
    private static final List<Class<? extends Annotation>> HTTP_METHODS =
            List.of(GET.class, POST.class, PUT.class, DELETE.class, PATCH.class, HEAD.class);

    @Test
    void chaqueMethodeDeRessourceDeclareSesRoles() throws Exception {
        List<String> fautifs = new ArrayList<>();
        List<Class<?>> ressources = ressourcesRest();
        assertFalse(ressources.isEmpty(), "Aucune ressource REST trouvée : le test ne vérifierait rien");

        for (Class<?> c : ressources) {
            for (Method m : c.getDeclaredMethods()) {
                boolean estEndpoint = HTTP_METHODS.stream().anyMatch(m::isAnnotationPresent);
                if (estEndpoint && !declareRoles(m) && !declareRoles(c)) {
                    fautifs.add(c.getSimpleName() + "#" + m.getName());
                }
            }
        }
        assertTrue(fautifs.isEmpty(), "Endpoints sans déclaration de rôles (SR-AUZ-01) : " + fautifs);
    }

    private static boolean declareRoles(AnnotatedElement e) {
        return e.isAnnotationPresent(RolesAllowed.class)
                || e.isAnnotationPresent(PermitAll.class)
                || e.isAnnotationPresent(DenyAll.class);
    }

    /** Parcourt target/classes et retient les classes annotées @Path. */
    private static List<Class<?>> ressourcesRest() throws IOException, ClassNotFoundException {
        java.nio.file.Path racine = java.nio.file.Path.of("target", "classes");
        List<Class<?>> out = new ArrayList<>();
        try (Stream<java.nio.file.Path> fichiers = Files.walk(racine)) {
            for (java.nio.file.Path p : (Iterable<java.nio.file.Path>) fichiers::iterator) {
                String nom = racine.relativize(p).toString();
                if (!nom.endsWith(".class") || nom.contains("$")) continue;
                String fqcn = nom.substring(0, nom.length() - 6).replace(java.io.File.separatorChar, '.');
                if (!fqcn.startsWith(BASE_PACKAGE)) continue;
                Class<?> c = Class.forName(fqcn);
                if (c.isAnnotationPresent(Path.class)) out.add(c);
            }
        }
        return out;
    }
}
