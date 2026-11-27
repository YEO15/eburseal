package tn.supcom.eburseal.api;

import jakarta.annotation.security.PermitAll;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

import java.util.Map;

/**
 * Ressource publique minimale. Volontairement sans numéro de version
 * (pas de divulgation d'information, cf. SR-ERR-01 / SR-DEP-01).
 */
@Path("/info")
@PermitAll // SR-AUZ-01 : chaque ressource déclare explicitement ses rôles
public class InfoResource {

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, String> info() {
        return Map.of("application", "EburSeal", "status", "up");
    }
}
