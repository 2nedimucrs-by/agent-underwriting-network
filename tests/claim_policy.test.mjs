import test from "node:test";
import assert from "node:assert/strict";
import {
  CLAIM_STATUS,
  classifyClaimStatus,
  isChallengeProofValid,
} from "../infra/supabase/functions/verify-github-claim/claim-policy.mjs";

test("only pending claims can enter verification; terminal states stay closed", () => {
  assert.equal(classifyClaimStatus(CLAIM_STATUS.PENDING), "pending");
  assert.equal(classifyClaimStatus(CLAIM_STATUS.VERIFIED), "already_verified");
  assert.equal(classifyClaimStatus("REJECTED"), "terminal");
  assert.equal(classifyClaimStatus("REVOKED"), "terminal");
  assert.equal(classifyClaimStatus("UNKNOWN"), "terminal");
});

const base = {
  claimId: "claim-123",
  challengeToken: "token-abc",
  expiresAt: "2026-10-03T17:00:00.000Z",
  proof: { claim_id: "claim-123", challenge: "token-abc" },
  now: Date.parse("2026-10-03T16:00:00.000Z"),
};

test("accepts an exact, unexpired challenge proof", () => {
  assert.equal(isChallengeProofValid(base), true);
});

test("rejects expired, malformed, or missing expiry", () => {
  assert.equal(isChallengeProofValid({ ...base, now: Date.parse(base.expiresAt) }), false);
  assert.equal(isChallengeProofValid({ ...base, expiresAt: "not-a-date" }), false);
  assert.equal(isChallengeProofValid({ ...base, expiresAt: null }), false);
});

test("rejects a wrong challenge token or claim id", () => {
  assert.equal(isChallengeProofValid({
    ...base,
    proof: { ...base.proof, challenge: "wrong-token" },
  }), false);
  assert.equal(isChallengeProofValid({
    ...base,
    proof: { ...base.proof, claim_id: "another-claim" },
  }), false);
});

test("rejects absent proof or challenge token", () => {
  assert.equal(isChallengeProofValid({ ...base, proof: null }), false);
  assert.equal(isChallengeProofValid({ ...base, challengeToken: "" }), false);
});
