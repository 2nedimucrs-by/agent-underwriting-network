import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const PUBLIC_INDEX =
  "https://2nedimucrs-by.github.io/agent-underwriting-network/data/agents.json";

Deno.serve(async (req) => {
  try {
    const expectedToken = Deno.env.get("AUN_CRON_TOKEN");
    const suppliedToken = req.headers.get("x-aun-cron-token");

    if (!expectedToken || suppliedToken !== expectedToken) {
      return json({ error: "unauthorized" }, 401);
    }

    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const secretKey = readKeySet(
      "SUPABASE_SECRET_KEYS",
      "SUPABASE_SERVICE_ROLE_KEY",
    );
    const admin = createClient(supabaseUrl, secretKey);

    const response = await fetch(PUBLIC_INDEX, {
      headers: { "Cache-Control": "no-cache" },
    });
    if (!response.ok) {
      return json({ error: "public agent index unavailable" }, 502);
    }

    const index = await response.json();
    const agents = Array.isArray(index.agents) ? index.agents : [];

    const { data: snapshotRows, error: snapshotError } = await admin
      .from("agent_version_snapshots")
      .select("agent_id,version_hash,observed_at")
      .order("observed_at", { ascending: false });

    if (snapshotError) throw snapshotError;

    const latest = new Map<string, string>();
    for (const row of snapshotRows || []) {
      if (!latest.has(row.agent_id)) {
        latest.set(row.agent_id, row.version_hash);
      }
    }

    const snapshotInserts: Array<Record<string, unknown>> = [];
    const driftInserts: Array<Record<string, unknown>> = [];
    const changed: Array<{
      agent_id: string;
      previous_hash: string | null;
      current_hash: string;
    }> = [];

    for (const agent of agents) {
      const agentId = String(agent.agent_id || "");
      const currentHash = String(agent.version?.commit_sha || "");
      const sourceUrl = String(agent.source?.url || "");

      if (!agentId || !currentHash) continue;

      const previousHash = latest.get(agentId) || null;

      if (!previousHash) {
        snapshotInserts.push({
          agent_id: agentId,
          version_hash: currentHash,
          source_url: sourceUrl,
          observed_at: new Date().toISOString(),
        });
        continue;
      }

      if (previousHash === currentHash) continue;

      snapshotInserts.push({
        agent_id: agentId,
        version_hash: currentHash,
        source_url: sourceUrl,
        observed_at: new Date().toISOString(),
      });

      driftInserts.push({
        agent_id: agentId,
        previous_hash: previousHash,
        current_hash: currentHash,
        detected_at: new Date().toISOString(),
        metadata: { source_url: sourceUrl },
      });

      changed.push({
        agent_id: agentId,
        previous_hash: previousHash,
        current_hash: currentHash,
      });
    }

    if (snapshotInserts.length) {
      const { error } = await admin
        .from("agent_version_snapshots")
        .upsert(snapshotInserts, {
          onConflict: "agent_id,version_hash",
          ignoreDuplicates: true,
        });
      if (error) throw error;
    }

    if (driftInserts.length) {
      const { error } = await admin
        .from("version_drift_events")
        .upsert(driftInserts, {
          onConflict: "agent_id,current_hash",
          ignoreDuplicates: true,
        });
      if (error) throw error;
    }

    let notificationsCreated = 0;

    if (changed.length) {
      const changedIds = changed.map((item) => item.agent_id);
      const { data: alerts, error: alertsError } = await admin
        .from("agent_alerts")
        .select("user_id,agent_id,alert_type")
        .eq("enabled", true)
        .eq("alert_type", "VERSION_DRIFT")
        .in("agent_id", changedIds);

      if (alertsError) throw alertsError;

      const byAgent = new Map(changed.map((item) => [item.agent_id, item]));
      const notifications = (alerts || []).map((alert) => {
        const drift = byAgent.get(alert.agent_id)!;
        const shortHash = drift.current_hash.slice(0, 12);

        return {
          user_id: alert.user_id,
          event_type: "VERSION_DRIFT",
          agent_id: alert.agent_id,
          title: "Agent version changed",
          body:
            alert.agent_id +
            " moved to version " +
            shortHash +
            ". Existing version-bound evidence may need re-evaluation.",
          metadata: drift,
          dedup_key:
            "version-drift:" +
            alert.agent_id +
            ":" +
            drift.current_hash,
        };
      });

      if (notifications.length) {
        const { data, error } = await admin
          .from("user_notifications")
          .upsert(notifications, {
            onConflict: "user_id,dedup_key",
            ignoreDuplicates: true,
          })
          .select("id");

        if (error) throw error;
        notificationsCreated = (data || []).length;
      }
    }

    return json({
      scanned_agents: agents.length,
      new_snapshots: snapshotInserts.length,
      version_drifts: changed.length,
      notifications_created: notificationsCreated,
    }, 200);
  } catch (error) {
    return json({ error: String(error) }, 500);
  }
});

function json(payload: unknown, status: number) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" },
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
