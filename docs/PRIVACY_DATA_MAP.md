# Privacy and data map

## Public GitHub Pages data

Public artifact metadata:
- repository identity
- source URL
- commit/version pin
- public description/topics/language/license
- public evidence records
- Trust Card projection

This data is about public software artifacts, not registered user accounts.

## Supabase user data — only after backend activation

profiles:
- auth user UUID
- email from auth provider
- GitHub login/avatar when supplied
- marketing opt-in
- timestamps

agent_claims:
- user UUID
- agent ID/repository
- GitHub login
- claim verification state
- review notes

saved_agents / agent_alerts:
- user UUID
- selected agent IDs
- alert preference

analytics_events — optional and consented:
- anonymous session ID
- optional authenticated user ID
- event type
- agent ID when relevant
- page path
- referrer
- small event metadata
- timestamp

The product-event schema intentionally has no raw IP-address field.

account_deletion_requests:
- user UUID
- request state/timestamps

outreach_suppression:
- contact key
- suppression reason
- timestamp

## Secrets that must never reach GitHub Pages

- GitHub OAuth client secret
- Supabase service-role key
- database password
- privileged API credentials
- private agent credentials

## External processing

Potential processors after activation:
- GitHub: repository source + OAuth
- Supabase: authentication/database
- Cloudflare Web Analytics: optional aggregate traffic analytics
- GitHub Pages: static site hosting

Before commercial launch, processor agreements, retention windows and jurisdiction-specific disclosures must be reviewed.
