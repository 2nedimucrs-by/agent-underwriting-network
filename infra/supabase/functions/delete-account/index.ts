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
    const secretKey = readKeySet(
      "SUPABASE_SECRET_KEYS",
      "SUPABASE_SERVICE_ROLE_KEY",
    );

    const userClient = createClient(supabaseUrl, publishableKey, {
      global: { headers: { Authorization: "Bearer " + jwt } },
    });
    const admin = createClient(supabaseUrl, secretKey);

    const { data, error } = await userClient.auth.getUser();
    if (error || !data.user) return json({ error: "invalid session" }, 401);

    const { error: deleteError } = await admin.auth.admin.deleteUser(data.user.id);
    if (deleteError) throw deleteError;

    return json({ deleted: true }, 200);
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
