# Auth + Analytics setup

The codebase is prepared to run with zero auth/analytics configuration. Public discovery remains fully usable when these services are disabled.

## Supabase

Create one dedicated Supabase project.

Run:

`infra/supabase/migrations/001_initial.sql`

Then configure Authentication providers:

- Email magic link
- GitHub OAuth

Add the GitHub Pages site URL and the Supabase callback URL to the relevant redirect allowlists.

Repository variables expected by the Pages workflow:

- `AUN_SUPABASE_URL`
- `AUN_SUPABASE_PUBLISHABLE_KEY`

These values are rendered into the public static runtime config. The Supabase publishable/anon key is intentionally client-side; all authorization is enforced by Row Level Security.

Do **not** place:

- GitHub OAuth client secret
- Supabase service-role key
- database password

in GitHub Pages output or repository variables.

Those server-side secrets belong only inside Supabase/provider secret storage.

## First admin

After signing in once, insert the founder's auth user UUID into:

`public.admin_users(user_id)`

This is a manual bootstrap operation. It should not be automated from a public page.

## Cloudflare Web Analytics

Optional repository variable:

- `AUN_CLOUDFLARE_WEB_ANALYTICS_TOKEN`

If present, the public site loads the Cloudflare beacon.

## Product analytics

Product events are written only after the visitor accepts the optional analytics prompt.

The client sends:

- anonymous session ID
- event type
- optional agent ID
- page path
- referrer
- small event metadata

The product event schema does not include a raw IP field.

Raw analytics events are not publicly readable. Admin dashboard aggregation is exposed only through admin-gated database functions.

## Account deletion

The static frontend can create an account-deletion request. Full deletion of the Supabase Auth identity requires a server-side function using privileged credentials; never expose the service-role key to the browser.
