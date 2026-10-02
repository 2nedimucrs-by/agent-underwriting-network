# Architecture

## Design goal

Start with a zero-fixed-cost public evidence network that can grow into an underwriting API and, only after sufficient evidence history exists, a verified agent labor exchange.

## Control plane

The Underwriting Chief coordinates bounded workers through explicit inputs and outputs. The Chief does not invent missing evidence and does not allow one subsystem to overwrite another subsystem's authority.

## Data plane

Public sources -> discovery -> version fingerprint -> evidence records -> Trust Card projection -> task-specific underwriting decision -> public/API projection.

## Initial infrastructure

- GitHub repository: source of code, schemas and public configuration
- GitHub Actions: scheduled discovery and CI
- GitHub Pages: public index
- JSON: bootstrap public registry
- Python standard library: discovery and underwriting core

No database, queue, paid cloud service, wallet, marketplace, vector database or autonomous mail sender is required for V0.

## Evidence authority

A scanner can produce evidence but cannot declare an agent globally safe.

A benchmark can prove a capability fixture but cannot authorize access to a customer's production system.

A maintainer can claim a profile but cannot remove negative evidence.

## Growth path

V0: public discovery index

V1: evidence adapters + version drift + capability fixtures

V2: maintainer claim + badge + continuous monitoring

V3: underwriting API + private registries

V4: task router

V5: verified labor exchange
