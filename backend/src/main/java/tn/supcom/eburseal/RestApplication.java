package tn.supcom.eburseal;

import jakarta.ws.rs.ApplicationPath;
import jakarta.ws.rs.core.Application;

/** Point d'entrée de l'API REST : toutes les ressources sont servies sous /api. */
@ApplicationPath("/api")
public class RestApplication extends Application {
}
