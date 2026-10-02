import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });

  try {
    const authHeader = req.headers.get("Authorization") ?? "";
    const jwt = authHeader.replace(/^Bearer\\s+/i, "");
    if (!jwt) return json({ error: "missing authorization" }, 401);

    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const anonKey = Deno.env.get("SUPABASE_ANON_KEY")!;
    const serviceRole = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

    const userClient = createClient(supabaseUrl, anonKey, {
      global: { headers: { Authorization: "Bearer " + jwt } },
    });
    const service = createClient(supabaseUrl, serviceRole);

    const { data: userData, error: userError } = await userClient.auth.getUser();
    if (userError || !userData.user) return json({ error: "invalid session" }, 401);

    const body = await req.json();
    const claimId = body.claim_id;
    if (!claimId) return json({ error: "claim_id is required" }, 400);

    const { data: claim, error: claimError } = await service
      .from("agent_claims")
      .select("id,user_id,agent_id,repository,status")
      .eq("id", claimId)
      .single();

    if (claimError || !claim) return json({ error: "claim not found" }, 404);
    if (claim.user_id !== userData.user.id) return json({ error: "claim does not belong to user" }, 403);

    const { data: profile } = await service
      .from("profiles")
      .select("github_login")
      .eq("user_id", userData.user.id)
      .single();

    const githubLogin = profile?.github_login?.toLowerCase() ?? null;
    const repository = claim.repository ?? "";

    if (!githubLogin || !repository.includes("/")) {
      return json({
        status: "PENDING_GITHUB_VERIFICATION",
        reason: "GitHub identity or repository is unavailable",
      }, 409);
    }

    const owner = repository.split("/")[0].toLowerCase();

    if (owner === githubLogin) {
      const notes = {
        proof: "github_oauth_login_equals_repository_owner",
        github_login: githubLogin,
        repository,
        verified_at: new Date().toISOString(),
      };

      const { error: updateError } = await service
        .from("agent_claims")
        .update({
          status: "VERIFIED_MAINTAINER",
          verified_at: new Date().toISOString(),
          verification_notes: notes,
        })
        .eq("id", claim.id);

      if (updateError) throw updateError;
      return json({ status: "VERIFIED_MAINTAINER", proof: notes.proof }, 200);
    }

    await service
      .from("agent_claims")
      .update({
        verification_notes: {
          proof: "manual_or_org_repository_proof_required",
          github_login: githubLogin,
          repository,
          checked_at: new Date().toISOString(),
        },
      })
      .eq("id", claim.id);

    return json({
      status: "PENDING_GITHUB_VERIFICATION",
      reason: "Organization/collaborator claims require stronger proof or manual review",
    }, 202);
  } catch (error) {
    return json({ error: String(error) }, 500);
  }
});

function json(payload: unknown, status: number) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { ...cors, "Content-Type": "application/json" },
  });
}
