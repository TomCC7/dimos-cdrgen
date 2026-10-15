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

## pstack workflow

`poteto-mode` and its referenced skills are available in `.agents/skills/`.
Use the standalone skill's Codex mappings. Installed helpers are source files,
not services: installation does not run them, install Bun dependencies, poll CI,
create automations, publish packages, or grant permissions for external actions.
Session instructions and explicit approval boundaries take precedence.

Use `deslop` for a behavior-preserving code diff review, and `technical-writing`
with `unslop` for documentation. Use `verify-dimos-cdrgen` for this library's
actual verification recipes. `create-verification-skill` and
`maintain-verification-skill` support creating and maintaining that feature map.

`setup-pstack` detects model choices and asks for confirmation before writing
user-level settings. For Codex its destination is `~/.agents/pstack-models.md`.
Installing the skill does not create this file or approve its model choices.
Do not silently substitute pstack's default model names when unavailable.

## Upstream provenance

The standalone skills are unchanged copies from
[backnotprop/pstack@1f0f9c3](https://github.com/backnotprop/pstack/tree/1f0f9c3bac03c4297f6fc8f7644fa412eda57085).
[The source manifest](.agents/pstack-source.json) records the selected skills,
pinned revision, and every copied file's SHA256. The selection includes
`poteto-mode`, all its principles, referenced workflows, setup, and verification
maintenance. The upstream MIT license remains in
[LICENSE.pstack](.agents/skills/LICENSE.pstack).

`deslop` comes from the separate upstream package that pstack references:
[cursor-team-kit](https://github.com/cursor/plugins/tree/6ce45c59b9301a638c1fe1a7b8dc2a82b650898f/cursor-team-kit).
Its unchanged skill and separate
[MIT license](.agents/skills/LICENSE.cursor-team-kit) are retained locally.
`verify-dimos-cdrgen` is project-specific and is not an upstream file.

Files use the documented Codex project location, `.agents/skills/`. No remote
installer was executed and no skills-CLI lockfile is claimed. To update, review
the pinned standalone source, preserve licenses and local verification recipes,
compare copied hashes, and update the manifest. Do not overwrite standalone
changes with Cursor's original versions. Do not activate copied automation or
shipping helpers as part of an update.
