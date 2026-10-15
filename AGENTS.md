# Coding in dimos-cdrgen

This is a standalone Python/C++/Rust message generator. Keep runtime and
transport dependencies outside this library.

## Repository-local skills

Read the relevant skill before its matching task:

- [verify-dimos-cdrgen](.agents/skills/verify-dimos-cdrgen/SKILL.md): run the
  project-specific fast or full verification recipes after affected changes.

- [Technical writing](.agents/skills/technical-writing/SKILL.md) and its required
  [unslop](.agents/skills/unslop/SKILL.md) companion: README, API documentation,
  tutorials, PR descriptions, and commit messages. Use real commands and short,
  runnable examples; distinguish generation from compilation and installation.

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

These six SKILL.md files are unchanged copies from the user-selected standalone
[backnotprop/pstack](https://github.com/backnotprop/pstack/tree/1f0f9c3bac03c4297f6fc8f7644fa412eda57085),
pinned to `1f0f9c3bac03c4297f6fc8f7644fa412eda57085`.
The repository is a standalone mirror of Lauren Tan's pstack with changes for
Codex and other agents. The four existing principles also match this revision,
so their files remain unchanged. The MIT license is retained at
[.agents/skills/LICENSE.pstack](.agents/skills/LICENSE.pstack).

The standalone README documents installation through `npx skills add
backnotprop/pstack`. The skills CLI supports `--agent codex`, `--skill`, and
`--copy`; its project-local Codex destination is `.agents/skills/`.
This checkout contains reviewed, pinned file copies in that documented location.
No remote installer was executed and no CLI-managed lockfile is claimed.

Six upstream skills and one project-specific verifier are installed. `technical-writing`'s `unslop`
dependency is included. These skills need no model setup. The standalone
`setup-pstack` writes `~/.agents/pstack-models.md` for Codex, so it is outside
this repo-local setup and has not been run.

To update, compare these six files against a reviewed commit of
`backnotprop/pstack`, preserve its license, update the pin above, and inspect
the diff. Use the standalone source rather than copying Cursor's original
over it, which could discard changes made for other agents.
