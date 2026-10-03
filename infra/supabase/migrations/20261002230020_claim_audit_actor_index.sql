-- Restore the production migration that added the claim-audit actor lookup index.
create index if not exists claim_audit_events_actor_user_idx
  on public.claim_audit_events(actor_user_id);
