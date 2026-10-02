import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });

  try {
    const authHeader = req.headers.get("Authorization") ?? "";
    const jwt = authHeader.replace(/^Bearer\s+/i, "");
    if (!jwt) return json({ error: "missing authorization" }, 401);

    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const publishableKey = readKeySet(
      "SUPABASE_PUBLISHABLE_KEYS",
      "SUPABASE_ANON_KEY",
    );

    const client = createClient(supabaseUrl, publishableKey, {
      global: { headers: { Authorization: "Bearer " + jwt } },
    });

    const { data: userData, error: userError } = await client.auth.getUser();
    if (userError || !userData.user) {
      return json({ error: "invalid session" }, 401);
    }

    const userId = userData.user.id;

    const [
      profile,
      claims,
      savedAgents,
      alerts,
      notifications,
      deletionRequests,
    ] = await Promise.all([
      client.from("profiles").select("*").eq("user_id", userId),
      client.from("agent_claims").select("*").eq("user_id", userId),
      client.from("saved_agents").select("*").eq("user_id", userId),
      client.from("agent_alerts").select("*").eq("user_id", userId),
      client.from("user_notifications").select("*").eq("user_id", userId),
      client.from("account_deletion_requests").select("*").eq("user_id", userId),
    ]);

    const firstError = [
      profile,
      claims,
      savedAgents,
      alerts,
      notifications,
      deletionRequests,
    ].find((result) => result.error)?.error;

    if (firstError) throw firstError;

    return json({
      schema_version: "1.0.0",
      exported_at: new Date().toISOString(),
      account: {
        id: userId,
        email: userData.user.email ?? null,
        created_at: userData.user.created_at,
        last_sign_in_at: userData.user.last_sign_in_at ?? null,
      },
      profile: profile.data || [],
      claims: claims.data || [],
      saved_agents: savedAgents.data || [],
      alerts: alerts.data || [],
      notifications: notifications.data || [],
      deletion_requests: deletionRequests.data || [],
      excluded: [
        "platform infrastructure logs",
        "public software-artifact evidence not owned by the account",
        "server-side secrets",
      ],
    }, 200);
  } catch (error) {
    return json({ error: String(error) }, 500);
  }
});

function json(payload: unknown, status: number) {
  return new Response(JSON.stringify(payload, null, 2), {
    status,
    headers: {
      ...cors,
      "Content-Type": "application/json",
      "Content-Disposition": "attachment; filename=\"aun-account-export.json\"",
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
