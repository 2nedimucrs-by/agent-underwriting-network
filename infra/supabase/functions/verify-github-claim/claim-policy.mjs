export const CLAIM_STATUS = {
  PENDING: "PENDING_GITHUB_VERIFICATION",
  VERIFIED: "VERIFIED_MAINTAINER",
};

export function classifyClaimStatus(status) {
  if (status === CLAIM_STATUS.VERIFIED) return "replay_denied";
  if (status === CLAIM_STATUS.PENDING) return "pending";
  return "terminal";
}

export function isChallengeProofValid({
  claimId,
  challengeToken,
  expiresAt,
  proof,
  now = Date.now(),
}) {
  const expiry = typeof expiresAt === "string" ? Date.parse(expiresAt) : NaN;
  return Boolean(
    challengeToken &&
    Number.isFinite(expiry) &&
    expiry > now &&
    proof &&
    proof.claim_id === claimId &&
    proof.challenge === challengeToken
  );
}
