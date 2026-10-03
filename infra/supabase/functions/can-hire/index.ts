import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const PUBLIC_BASE =
  "https://2nedimucrs-by.github.io/agent-underwriting-network";

const policies: Record<string, {
  required: string[];
  allowsWrite: boolean;
  maxSpendUsd: number;
}> = {
  browser_read: {
    required: ["identity", "provenance", "security", "permissions", "capability", "reliability", "freshness"],
    allowsWrite: false,
    maxSpendUsd: 0,
  },
  repository_read: {
    required: ["identity", "provenance", "security", "permissions", "capability", "reliability", "freshness"],
    allowsWrite: false,
    maxSpendUsd: 0,
  },
  structured_extraction: {
    required: ["identity", "provenance", "capability", "reliability", "freshness"],
    allowsWrite: false,
    maxSpendUsd: 0,
  },
  mcp_tool_invocation: {
    required: ["identity", "provenance", "security", "permissions", "capability", "reliability", "freshness"],
    allowsWrite: false,
    maxSpendUsd: 0,
  },
  code_change: {
    required: ["identity", "provenance", "security", "permissions", "capability", "reliability", "freshness"],
    allowsWrite: true,
    maxSpendUsd: 5,
  },
  crm_write: {
    required: ["identity", "provenance", "security", "permissions", "capability", "reliability", "economics", "freshness"],
    allowsWrite: true,
    maxSpendUsd: 2,
  },
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

    const client = createClient(supabaseUrl, publishableKey, {
      global: { headers: { Authorization: "Bearer " + jwt } },
    });

    const { data: userData, error: userError } = await client.auth.getUser();
    if (userError || !userData.user) {
      return json({ error: "invalid session" }, 401);
    }

    const service = createClient(supabaseUrl, secretKey);
    const body = await req.json();
    const agentId = String(body.agent_id || "");
    const taskType = String(body.task_type || "");
    const requested = body.limits || {};

    const { data: rateLimit, error: rateLimitError } = await service.rpc(
      "consume_underwriting_rate_limit",
      {
        p_user_id: userData.user.id,
        p_agent_id: agentId.slice(0, 256) || null,
        p_task_type: taskType.slice(0, 80) || null,
      },
    );

    // Rate limiting is fail-closed: a database error or malformed response
    // must never allow the underwriting request to continue.
    if (rateLimitError) {
      throw new Error("underwriting rate limit check failed");
    }
    if (!rateLimit || typeof rateLimit.allowed !== "boolean") {
      throw new Error("underwriting rate limit response is invalid");
    }
    if (rateLimit.allowed === false) {
      return json({
        error: "rate limit exceeded",
        retry_after_seconds: rateLimit.retry_after_seconds,
      }, 429);
    }

    const policy = policies[taskType];
    if (!policy) {
      return json({
        schema_version: "1.0.0",
        decision: "REVIEW_REQUIRED",
        agent_id: agentId,
        task_type: taskType,
        reasons: ["no underwriting policy exists for this task"],
        limits: {},
        evidence_ids: [],
      }, 200);
    }

    const slug = slugForAgent(agentId);
    if (!slug) return json({ error: "unsupported agent_id" }, 400);

    const trustResponse = await fetch(
      PUBLIC_BASE + "/trust-cards/" + slug + ".json",
      { headers: { "Cache-Control": "no-cache" } },
    );
    if (!trustResponse.ok) {
      return json({ error: "Trust Card not found" }, 404);
    }

    const card = await trustResponse.json();
    const dimensions = card.evidence_dimensions || {};
    const evidenceIds = card.evidence_ids || [];

    if (card.status === "BLOCKED") {
      return decision(
        "DENY",
        agentId,
        taskType,
        ["agent status is BLOCKED"],
        {},
        evidenceIds,
      );
    }

    const writeAccess = Boolean(requested.write_access);
    const spend = Math.max(0, Number(requested.max_spend_usd || 0));

    if (writeAccess && !policy.allowsWrite) {
      return decision(
        "DENY",
        agentId,
        taskType,
        ["task policy forbids write access"],
        { write_access: false, max_spend_usd: policy.maxSpendUsd },
        evidenceIds,
      );
    }

    const missing = policy.required.filter(
      (dimension) => dimensions[dimension] !== "VERIFIED",
    );

    const limits = {
      write_access: writeAccess && policy.allowsWrite,
      max_spend_usd: Math.min(spend, policy.maxSpendUsd),
    };

    if (missing.length) {
      return decision(
        "INSUFFICIENT_EVIDENCE",
        agentId,
        taskType,
        ["required VERIFIED evidence is missing for: " + missing.join(", ")],
        limits,
        evidenceIds,
        missing,
      );
    }

    if (card.status !== "VERIFIED_FOR_TASK") {
      return decision(
        "REVIEW_REQUIRED",
        agentId,
        taskType,
        ["dimensions are VERIFIED but the Trust Card is not VERIFIED_FOR_TASK"],
        limits,
        evidenceIds,
      );
    }

    if (spend > policy.maxSpendUsd) {
      return decision(
        "ALLOW_WITH_LIMITS",
        agentId,
        taskType,
        ["requested spend exceeds policy maximum"],
        limits,
        evidenceIds,
      );
    }

    return decision(
      "ALLOW",
      agentId,
      taskType,
      ["task-specific evidence and requested limits satisfy policy"],
      limits,
      evidenceIds,
    );
  } catch (error) {
    return json({ error: String(error) }, 500);
  }
});

function slugForAgent(agentId: string): string | null {
  if (!agentId.startsWith("github:")) return null;
  return agentId
    .slice("github:".length)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function decision(
  value: string,
  agentId: string,
  taskType: string,
  reasons: string[],
  limits: Record<string, unknown>,
  evidenceIds: string[],
  missingDimensions: string[] = [],
) {
  return json({
    schema_version: "1.0.0",
    decision: value,
    agent_id: agentId,
    task_type: taskType,
    reasons,
    limits,
    evidence_ids: evidenceIds,
    missing_dimensions: missingDimensions,
  }, 200);
}

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
