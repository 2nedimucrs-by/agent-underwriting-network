const MAX_BODY_BYTES = 8192;

/**
 * Parse and validate a POST /can-hire JSON body without coercing caller values.
 * @param {string} raw
 * @returns {{ ok: true, value: { agent_id: string, task_type: string, limits: { write_access?: boolean, max_spend_usd?: number } } } | { ok: false, status: number, error: string }}
 */
export function parseCanHireJson(raw) {
  if (typeof raw !== "string") {
    return { ok: false, status: 400, error: "request body must be JSON" };
  }
  if (new TextEncoder().encode(raw).byteLength > MAX_BODY_BYTES) {
    return { ok: false, status: 413, error: "request body is too large" };
  }

  let body;
  try {
    body = JSON.parse(raw);
  } catch {
    return { ok: false, status: 400, error: "invalid JSON body" };
  }

  if (body === null || typeof body !== "object" || Array.isArray(body)) {
    return { ok: false, status: 400, error: "request body must be an object" };
  }
  const keys = Object.keys(body);
  if (keys.some((key) => !["agent_id", "task_type", "version_commit_sha", "limits"].includes(key))) {
    return { ok: false, status: 400, error: "request body contains an unknown field" };
  }

  if (
    typeof body.agent_id !== "string" ||
    body.agent_id !== body.agent_id.trim() ||
    body.agent_id.length > 256 ||
    !/^github:[A-Za-z0-9-]+\/[A-Za-z0-9._-]+$/.test(body.agent_id)
  ) {
    return { ok: false, status: 400, error: "agent_id is invalid" };
  }
  if (
    typeof body.version_commit_sha !== "string" ||
    !/^[a-fA-F0-9]{40}$/.test(body.version_commit_sha)
  ) {
    return { ok: false, status: 400, error: "version_commit_sha must be a 40-character commit SHA" };
  }
  if (
    typeof body.task_type !== "string" ||
    body.task_type !== body.task_type.trim() ||
    !/^[a-z][a-z0-9_]{1,79}$/.test(body.task_type)
  ) {
    return { ok: false, status: 400, error: "task_type is invalid" };
  }

  const limits = body.limits === undefined ? {} : body.limits;
  if (limits === null || typeof limits !== "object" || Array.isArray(limits)) {
    return { ok: false, status: 400, error: "limits must be an object" };
  }
  if (Object.keys(limits).some((key) => !["write_access", "max_spend_usd"].includes(key))) {
    return { ok: false, status: 400, error: "limits contains an unknown field" };
  }
  if (limits.write_access !== undefined && typeof limits.write_access !== "boolean") {
    return { ok: false, status: 400, error: "write_access must be a boolean" };
  }
  if (
    limits.max_spend_usd !== undefined &&
    (typeof limits.max_spend_usd !== "number" ||
      !Number.isFinite(limits.max_spend_usd) ||
      limits.max_spend_usd < 0)
  ) {
    return { ok: false, status: 400, error: "max_spend_usd must be a finite non-negative number" };
  }

  return {
    ok: true,
    value: {
      agent_id: body.agent_id,
      task_type: body.task_type,
      version_commit_sha: body.version_commit_sha.toLowerCase(),
      limits: {
        ...(limits.write_access === undefined ? {} : { write_access: limits.write_access }),
        ...(limits.max_spend_usd === undefined ? {} : { max_spend_usd: limits.max_spend_usd }),
      },
    },
  };
}


/**
 * Ensure a decision is bound to the requested repository and immutable commit.
 * @param {string} agentId
 * @param {string} versionCommitSha
 * @param {{ agent_id?: unknown, version?: { commit_sha?: unknown } }} card
 * @returns {boolean}
 */
export function matchesPinnedCard(agentId, versionCommitSha, card) {
  return (
    typeof agentId === "string" &&
    typeof versionCommitSha === "string" &&
    /^[a-f0-9]{40}$/.test(versionCommitSha) &&
    card?.agent_id === agentId &&
    typeof card.version?.commit_sha === "string" &&
    card.version.commit_sha.toLowerCase() === versionCommitSha
  );
}
