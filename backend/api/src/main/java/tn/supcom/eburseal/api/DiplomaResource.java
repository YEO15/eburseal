package tn.supcom.eburseal.api;

import jakarta.annotation.security.RolesAllowed;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import tn.supcom.eburseal.commun.IssueRequest;
import tn.supcom.eburseal.commun.IssuedDiploma;
import tn.supcom.eburseal.security.Roles;

import java.security.GeneralSecurityException;

/** Diploma issuance: reserved to authenticated institution staff (ISSUER). */
@Path("/diplomas")
@RolesAllowed(Roles.ISSUER)
public class DiplomaResource {

    @Inject
    DiplomaKeys keys;

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response issue(IssueRequest request) {
        if (request == null) {
            return Response.status(Response.Status.BAD_REQUEST).build();
        }
        try {
            IssuedDiploma diploma = keys.issuer().issue(request);
            return Response.status(Response.Status.CREATED).entity(diploma).build();
        } catch (GeneralSecurityException e) {
            return Response.serverError().build();      // no technical detail leaked
        }
    }
}