# Coding in dimos-cdrgen

This is a standalone Python/C++/Rust message generator. Keep runtime and
transport dependencies outside this library.

## Repository-local skills

Read the relevant skill before its matching task:

- [Boundary discipline](.agents/skills/principle-boundary-discipline/SKILL.md):
  CLI/config parsing, schema input, package hooks, and native tool invocation.
- [Idempotent operations](.agents/skills/principle-make-operations-idempotent/SKILL.md):
  regeneration, cache invalidation, deletion/rename, and recovery from failed builds.
- [Behavior tests](.agents/skills/principle-test-behavior-not-implementation/SKILL.md):
  test installed consumers and observable CDR results, not generator internals alone.
- [Real verification](.agents/skills/principle-prove-it-works/SKILL.md):
  verify the actual wheel, source install, generated native consumer, or codec
  affected by a change; report missing toolchains and untested platforms explicitly.

Apply these principles to the library's public contract: exposing generated
message values and CDR codecs is intentional. A skill is not authority to
remove a supported API, install dependencies, publish, merge, or alter globals.
Use the current session's tools and permissions; no Cursor slash commands,
model overrides, subagent setup, or global plugin installation are required.
Read README.md for the existing build and verification commands. Do not invent
commands or treat documentation-only changes as requiring native rebuilds.

## Upstream provenance

The four SKILL.md files are unchanged copies from Lauren Tan's pstack
v0.15.25, pinned to:

https://github.com/cursor/plugins/tree/6ce45c59b9301a638c1fe1a7b8dc2a82b650898f/pstack

Their MIT license is retained at [.agents/skills/LICENSE.pstack](.agents/skills/LICENSE.pstack).
This is a selected repo-local import, not a full pstack plugin installation.
Upstream's `/add-plugin pstack` and `/setup-pstack` workflow targets Cursor;
`setup-pstack` writes `~/.cursor/rules/pstack-models.mdc`, so it is deliberately
not run here. The skill index above supplies explicit local routing for agents
that do not support Cursor's skill invocation metadata.

To update, review the corresponding four upstream files at a new pinned commit,
preserve the license, update this provenance, and inspect the diff. Do not copy
unrelated plugin automations, executables, or model configuration.
