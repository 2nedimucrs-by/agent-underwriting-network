import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { classifyClaimStatus, isChallengeProofValid } from "./claim-policy.mjs";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const CLAIM_FILE_PATH = ".github/agent-underwriting-claim.json";
const CHALLENGE_TTL_MS = 24 * 60 * 60 * 1000;

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });

  try {
    const authHeader = req.headers.get("Authorization") ?? "";
    const jwt = authHeader.replace(/^Bearer\\s+/i, "");
    if (!jwt) return json({ error: "missing authorization" }, 401);

    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const publishableKey = readKeySet(
      "SUPABASE_PUBLISHABLE_KEYS",
      "SUPABASE_ANON_KEY",
    );
    const secretKey = readKeySet(
      "SUPABASE_SECRET_KEYS",
      "SUPABASE_SERVICE_ROLE_KEY",
    );

    const userClient = createClient(supabaseUrl, publishableKey, {
      global: { headers: { Authorization: "Bearer " + jwt } },
    });
    const service = createClient(supabaseUrl, secretKey);

    const { data: userData, error: userError } = await userClient.auth.getUser();
    if (userError || !userData.user) {
      return json({ error: "invalid session" }, 401);
    }

    const body = await req.json();
    const claimId = String(body.claim_id || "").trim();
    if (!claimId) return json({ error: "claim_id is required" }, 400);

    const { data: claim, error: claimError } = await service
      .from("agent_claims")
      .select(
        "id,user_id,agent_id,repository,status,challenge_token,challenge_expires_at"
      )
      .eq("id", claimId)
      .single();

    if (claimError || !claim) return json({ error: "claim not found" }, 404);
    if (claim.user_id !== userData.user.id) {
      return json({ error: "claim does not belong to user" }, 403);
    }

    const claimDisposition = classifyClaimStatus(claim.status);
    if (claimDisposition === "already_verified") {
      return json({ status: claim.status, proof: "already_verified" }, 200);
    }
    if (claimDisposition === "terminal") {
      return json({
        error: "claim is not pending verification",
        status: claim.status,
      }, 409);
    }

    const { data: profile, error: profileError } = await service
      .from("profiles")
      .select("github_login")
      .eq("user_id", userData.user.id)
      .single();

    if (profileError) throw profileError;

    const githubLogin = profile?.github_login?.toLowerCase() ?? null;
    const repository = String(claim.repository || "").trim();

    if (!githubLogin || !repository.includes("/")) {
      return json({
        status: "PENDING_GITHUB_VERIFICATION",
        reason: "GitHub identity or repository is unavailable",
      }, 409);
    }

    const [owner, repoName] = repository.split("/");
    if (!owner || !repoName) {
      return json({
        status: "PENDING_GITHUB_VERIFICATION",
        reason: "Repository identity is malformed",
      }, 409);
    }

    if (owner.toLowerCase() === githubLogin) {
      const verifiedAt = new Date().toISOString();
      const notes = {
        proof: "github_oauth_login_equals_repository_owner",
        github_login: githubLogin,
        repository,
        verified_at: verifiedAt,
      };

      const updated = await updatePendingClaim(service, claim.id, {
        status: "VERIFIED_MAINTAINER",
        verification_method: "github_oauth_owner",
        verified_at: verifiedAt,
        verification_notes: notes,
      });
      if (!updated) {
        return json({ error: "claim state changed during verification" }, 409);
      }

      await writeAudit(service, {
        claim_id: claim.id,
        actor_user_id: userData.user.id,
        event_type: "AUTO_VERIFIED_PERSONAL_OWNER",
        metadata: notes,
      });

      return json({
        status: "VERIFIED_MAINTAINER",
        proof: notes.proof,
      }, 200);
    }

    const now = Date.now();
    const existingExpiresAt = claim.challenge_expires_at
      ? Date.parse(claim.challenge_expires_at)
      : 0;
    let challengeToken = String(claim.challenge_token || "");

    if (challengeToken && existingExpiresAt > now) {
      const proof = await readPublicChallenge(repository);

      if (isChallengeProofValid({
        claimId: claim.id,
        challengeToken,
        expiresAt: claim.challenge_expires_at,
        proof,
        now,
      })) {
        const verifiedAt = new Date().toISOString();
        const notes = {
          proof: "public_repository_challenge_file",
          repository,
          file_path: CLAIM_FILE_PATH,
          verified_at: verifiedAt,
        };

        const updated = await updatePendingClaim(service, claim.id, {
          status: "VERIFIED_MAINTAINER",
          verification_method: "public_repository_challenge",
          verified_at: verifiedAt,
          verification_notes: notes,
        });
        if (!updated) {
          return json({ error: "claim state changed during verification" }, 409);
        }

        await writeAudit(service, {
          claim_id: claim.id,
          actor_user_id: userData.user.id,
          event_type: "CHALLENGE_VERIFIED",
          metadata: notes,
        });

        return json({
          status: "VERIFIED_MAINTAINER",
          proof: notes.proof,
        }, 200);
      }
    }

    let expiresAtIso = claim.challenge_expires_at;

    if (!challengeToken || existingExpiresAt <= now) {
      challengeToken = crypto.randomUUID();
      const issuedAt = new Date();
      const expiresAt = new Date(issuedAt.getTime() + CHALLENGE_TTL_MS);
      expiresAtIso = expiresAt.toISOString();

      const challengeNotes = {
        proof: "public_repository_challenge_pending",
        repository,
        file_path: CLAIM_FILE_PATH,
        issued_at: issuedAt.toISOString(),
        expires_at: expiresAtIso,
      };

      const issued = await updatePendingClaim(service, claim.id, {
        verification_method: "public_repository_challenge",
        challenge_token: challengeToken,
        challenge_issued_at: issuedAt.toISOString(),
        challenge_expires_at: expiresAtIso,
        verification_notes: challengeNotes,
      });
      if (!issued) {
        return json({ error: "claim state changed during verification" }, 409);
      }

      await writeAudit(service, {
        claim_id: claim.id,
        actor_user_id: userData.user.id,
        event_type: "CHALLENGE_ISSUED",
        metadata: {
          repository,
          file_path: CLAIM_FILE_PATH,
          expires_at: expiresAtIso,
        },
      });
    }

    return json({
      status: "PENDING_GITHUB_VERIFICATION",
      reason:
        "Add the challenge document to the public repository, then verify again.",
      challenge_file_path: CLAIM_FILE_PATH,
      challenge_document: {
        claim_id: claim.id,
        challenge: challengeToken,
      },
      challenge_expires_at: expiresAtIso,
    }, 202);
  } catch (error) {
    return json({ error: String(error) }, 500);
  }
});

async function readPublicChallenge(
  repository: string,
): Promise<{ claim_id?: string; challenge?: string } | null> {
  const [owner, name] = repository.split("/");
  if (!owner || !name) return null;

  const path = CLAIM_FILE_PATH
    .split("/")
    .map(encodeURIComponent)
    .join("/");

  const url =
    "https://api.github.com/repos/" +
    encodeURIComponent(owner) +
    "/" +
    encodeURIComponent(name) +
    "/contents/" +
    path;

  const response = await fetch(url, {
    headers: {
      "Accept": "application/vnd.github+json",
      "Cache-Control": "no-cache",
      "User-Agent": "agent-underwriting-network/0.6",
      "X-GitHub-Api-Version": "2022-11-28",
    },
  });

  if (!response.ok) return null;

  const payload = await response.json();
  if (payload?.type !== "file" || typeof payload?.content !== "string") {
    return null;
  }

  try {
    const compact = payload.content.replace(/\\s/g, "");
    const decoded = atob(compact);
    const bytes = Uint8Array.from(decoded, (char) => char.charCodeAt(0));
    return JSON.parse(new TextDecoder().decode(bytes));
  } catch (_) {
    return null;
  }
}

async function updatePendingClaim(
  service: any,
  claimId: string,
  patch: Record<string, unknown>,
): Promise<boolean> {
  const { data, error } = await service
    .from("agent_claims")
    .update(patch)
    .eq("id", claimId)
    .eq("status", "PENDING_GITHUB_VERIFICATION")
    .select("id")
    .maybeSingle();

  if (error) throw error;
  return Boolean(data?.id);
}

async function writeAudit(
  service: any,
  event: {
    claim_id: string;
    actor_user_id: string;
    event_type: string;
    metadata: Record<string, unknown>;
  },
) {
  const { error } = await service
    .from("claim_audit_events")
    .insert(event);

  if (error) throw error;
}

function json(payload: unknown, status: number) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      ...cors,
      "Content-Type": "application/json",
      "Cache-Control": "no-store",
    },
  });
}

function readKeySet(currentName: string, legacyName: string): string {
  const current = Deno.env.get(currentName);
  if (current) {
    try {
      const parsed = JSON.parse(current);
      if (typeof parsed?.default === "string" && parsed.default.trim()) {
        return parsed.default.trim();
      }
    } catch (_) {
      if (current.trim()) return current.trim();
    }
  }

  const legacy = Deno.env.get(legacyName);
  if (legacy?.trim()) return legacy.trim();

  throw new Error("required Supabase API key is unavailable");
}
