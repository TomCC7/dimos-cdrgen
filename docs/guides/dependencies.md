# Reuse another package's message types

Use an installed message package when a field belongs to that package.
The generator checks its version, ABI, ownership, and schema hashes.
It emits declarations only for messages owned by the new package.

## Declare an installed dependency

First complete the [Python quickstart](../quickstarts/python.md), which installs
the local `acme` package. Keep that environment active. In a second project,
create `interfaces/app_msgs/msg/Sample.msg`:

```text
example_msgs/Reading reading
string sensor
```

Create `pyproject.toml`:

```toml
[project]
name = "sample-app"
version = "0.1.0"

[tool.dimos.messages]
source = "interfaces"

[tool.dimos.messages.dependencies]
acme = "0.1.0"
```

The dependency key is the Python module name, and its value is an exact version.
The installed package must expose `acme_schemas/package`, which the generator
uses to load the manifest and native sources.

```sh
dimos-cdrgen
python -m pip install build/message-source/python
python - <<'PY'
from acme.example_msgs.msg import Reading
from sample_app.app_msgs.msg import Sample
from dimos_cdrgen.registry import decode, encode

sample = Sample(reading=Reading(sequence=1, value=21.5), sensor="left")
restored = decode(encode(sample), Sample)
assert type(restored.reading) is Reading
print(restored.reading.value)
PY
```

The command prints `21.5` and verifies that the nested value uses `acme`'s
`Reading` class. Declare every transitive owner required by your dependency
closure. A missing owner, duplicate owner, version conflict, or changed schema
fails generation.

## Reuse C++ declarations

Call `prepare_cpp()` on the new `build/message-source` root as in the
[C++ quickstart](../quickstarts/cpp.md). Preparation finds the installed
dependency's source package and builds the dependency closure. Link the new
project with `sample_app::messages`. Its exports include dependency prefixes.
The new package does not generate a second `example_msgs::msg::Reading`.

## Rust dependency resolution

The generated `rust/Cargo.toml` refers to dependency crates with exact versions
and local paths into their installed source packages. Keep those packages present
while compiling directly from that generated directory.

The copy of the crate embedded in a generated Python package removes local Cargo
paths. A consumer of that copy must supply dependency crates through local
workspace patches or separately published crates with the exact required versions.
Publishing a Python wheel does not publish its Cargo dependencies.

Rust requires one owner crate per ROS message package. For example, if `acme`
owns `example_msgs/Reading`, put new messages in `app_msgs`, as this guide does.
Adding `example_msgs/Sample` in a second owner package fails Rust generation.
Splitting one ROS package across dependency crates also fails.

The project command always generates Rust, so this restriction applies to that
command even if you only plan to use Python. The [direct generation API](../reference/api.md#direct-generation)
can select `languages=("python",)` for a Python-only package.

## Keep catalogs separate

Standard ROS definitions are not bundled in `dimos-cdrgen`. Supply a separately
prepared catalog or an installed message package that owns those definitions.
The test schema downloader prepares fixtures, not a supported catalog release.
The full schema closure remains in the generated artifacts for consumers that
need schema registration.
