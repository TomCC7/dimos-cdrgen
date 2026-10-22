# Generate messages and recover from failure

Authors generate package sources from project configuration without compiling them.

## Sub-features

- `config`: reject missing inputs and paths outside the project.
- `rename`: replace the old type after renaming a message and regenerating.
- `rollback`: preserve the previous output after generation or installation failure.

## How to get to it (user POV)

Run `dimos-cdrgen` in a configured message project, or call `generate()`.

## Driving it with pytest

Preconditions: the parent skill's prepared Python environment and fresh run directory.

Run the parent skill's fast command. Require eight passes. The CLI test changes
`Stamp.msg` to `Clock.msg` and asserts only the new export remains. The transaction
test compares all prior output bytes after unsupported input, emitter failure,
and replacement failure, then checks that stale schemas and language output
are removed after a successful generation.

The namespace tests regenerate a flat Python package under `robot.messages`,
verify that old Python output disappears, and compare C++/Rust sources byte for
byte. Invalid namespace configurations preserve the previous output.

## Gotchas

The rollback tests inject failures deliberately. They do not prove crash recovery
at every instruction, concurrent generation, or all cache invalidation behavior.
Native cache portability tests are separate regression tests, not this CLI journey.
