# External benchmark execution

This directory contains bounded adapters that execute AUN fixtures against
version-pinned third-party software.

## PydanticAI structured-extraction receipt

The first adapter targets `pydantic-ai-slim==2.53.0`.

The workflow:

1. downloads the exact PyPI wheel,
2. records its SHA-256,
3. installs only binary distributions,
4. disables real model requests,
5. runs the AUN structured-extraction fixture through a real
   `pydantic_ai.Agent` using PydanticAI's documented procedural
   `TestModel`,
6. emits a canonical AUN benchmark receipt as a GitHub Actions artifact.

### Evidence boundary

This is **framework execution evidence**, not LLM intelligence evidence.

PydanticAI's `TestModel` is procedural testing code. A passing receipt shows
that the exact package artifact can execute the bounded Agent/TestModel path
and return the fixture output through the framework. It does not prove that a
production model can perform the task, that arbitrary tools are safe, or that
the package is globally capable or secure.

No repository secrets, Supabase keys, provider API keys or persistent GitHub
credentials are exposed to the third-party package during this workflow.
