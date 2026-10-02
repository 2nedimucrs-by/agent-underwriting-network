# Bootstrap evidence

Date: 2026-10-02

## Repository

Owner: 2nedimucrs-by

Repository: agent-underwriting-network

Visibility: public

## CI

Latest verified foundation CI run:

- run: 37049565904
- head: 3e7229e71c0f54f020cb4c3b5b50d22dd66d74f0
- conclusion: SUCCESS

The run executed package installation, unittest discovery and static-site integrity validation.

## Public Pages deployment

The first Pages attempts failed because GitHub Pages had not yet been enabled for the repository and the connected integration could not create the Pages site itself.

The repository owner then enabled:

Settings -> Pages -> Build and deployment -> Source -> GitHub Actions

The previously failed Pages run was re-run.

Verified deployment evidence:

- workflow run: 37049565699
- run attempt: 2
- build job: SUCCESS
- GitHub discovery refresh: SUCCESS
- generated-site validation: SUCCESS
- Configure Pages: SUCCESS
- Pages artifact upload: SUCCESS
- deploy job: SUCCESS
- Deploy to GitHub Pages: SUCCESS

Expected public site:

https://2nedimucrs-by.github.io/agent-underwriting-network/

The site is now considered deployment-proven by GitHub Actions evidence. Public web reachability from every external network is a separate availability check and should not be inferred from deployment success alone.
