import assert from "node:assert/strict";
import test from "node:test";
import { parseCanHireJson } from "./request_validation.mjs";

const valid = {
  agent_id: "github:browser-use/browser-use",
  task_type: "browser_read",
  limits: { write_access: false, max_spend_usd: 0 },
};

test("accepts a well-formed underwriting request without coercing values", () => {
  const result = parseCanHireJson(JSON.stringify(valid));
  assert.equal(result.ok, true);
  assert.deepEqual(result.value, valid);
});

test("defaults omitted limits to an empty object", () => {
  const result = parseCanHireJson(JSON.stringify({
    agent_id: "github:owner/repo",
    task_type: "custom_task",
  }));
  assert.equal(result.ok, true);
  assert.deepEqual(result.value.limits, {});
});

test("rejects malformed JSON", () => {
  assert.deepEqual(parseCanHireJson("{"), {
    ok: false, status: 400, error: "invalid JSON body",
  });
});

test("rejects null, arrays, missing identifiers, and malformed identifiers", () => {
  for (const body of [null, [], {}, { ...valid, agent_id: "repo" }]) {
    assert.equal(parseCanHireJson(JSON.stringify(body)).ok, false);
  }
});

test("rejects unknown top-level and nested properties", () => {
  assert.equal(parseCanHireJson(JSON.stringify({ ...valid, extra: true })).ok, false);
  assert.equal(parseCanHireJson(JSON.stringify({
    ...valid, limits: { ...valid.limits, extra: true },
  })).ok, false);
});

test("rejects string booleans and numeric strings instead of coercing", () => {
  assert.equal(parseCanHireJson(JSON.stringify({
    ...valid, limits: { write_access: "false" },
  })).ok, false);
  assert.equal(parseCanHireJson(JSON.stringify({
    ...valid, limits: { max_spend_usd: "1" },
  })).ok, false);
});

test("rejects non-finite and negative spend values", () => {
  for (const spend of [Number.NaN, Number.POSITIVE_INFINITY, Number.NEGATIVE_INFINITY, -1]) {
    assert.equal(parseCanHireJson(JSON.stringify(valid)).ok, true);
    const direct = JSON.stringify({ ...valid, limits: { max_spend_usd: spend } });
    if (Number.isFinite(spend)) assert.equal(parseCanHireJson(direct).ok, false);
  }
  for (const token of ["NaN", "Infinity", "-Infinity"]) {
    const nonFiniteText = `{"agent_id":"github:owner/repo","task_type":"browser_read","limits":{"max_spend_usd":${token}}}`;
    assert.equal(parseCanHireJson(nonFiniteText).ok, false);
  }
});

test("rejects unknown tasks only at policy evaluation, not schema parsing", () => {
  assert.equal(parseCanHireJson(JSON.stringify({
    agent_id: "github:owner/repo",
    task_type: "unknown_task",
  })).ok, true);
});

test("rejects oversized bodies with 413", () => {
  const raw = JSON.stringify(valid).padEnd(8193, " ");
  assert.equal(parseCanHireJson(raw).status, 413);
});
