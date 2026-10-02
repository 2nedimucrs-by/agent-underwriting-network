# Supabase deployment

This directory contains the optional user/account backend for the public GitHub Pages product.

## Apply database schema

Run `migrations/001_initial.sql` inside a dedicated Supabase project.

## Deploy Edge Functions

- `verify-github-claim`
- `delete-account`

Required server-side function secrets:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`

Never expose the service-role key to GitHub Pages.

## Claim verification scope

The first automatic proof intentionally supports only the safest simple case:

`GitHub OAuth login == personal repository owner`

Organization repositories and collaborator/maintainer roles remain PENDING until a stronger GitHub App/permission proof or explicit admin review is added.

This avoids falsely labeling an organization member as a repository maintainer.

## Account deletion

`delete-account` requires the authenticated user JWT and deletes only that Auth identity. Database child records configured with `ON DELETE CASCADE` are removed with it.
