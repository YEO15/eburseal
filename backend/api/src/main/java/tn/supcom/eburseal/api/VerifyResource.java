package tn.supcom.eburseal.api;

import jakarta.annotation.security.PermitAll;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import tn.supcom.eburseal.commun.IssuedDiploma;
import tn.supcom.eburseal.commun.Verdict;

import java.util.Map;

/**
 * Public diploma verification (recruiters, universities): no account needed.
 * Data minimisation: the answer contains the verdict only, never the diploma data.
 */
@Path("/verify")
@PermitAll
public class VerifyResource {

    @Inject
    DiplomaKeys keys;

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, String> verify(IssuedDiploma diploma) {
        Verdict verdict = keys.verifier().verify(diploma);
        return Map.of("verdict", verdict.name());
    }
}