# Generated artifacts

The project CLI writes `build/message-source` under the input project.
The directory contains source artifacts and metadata. Generation does not compile
C++ libraries or Rust crates.

| Path | Contents | Consumer |
| --- | --- | --- |
| `python/` | Installable Python project with runtime aliases, type stubs, and a schema provider. | `python -m pip install build/message-source/python` |
| `cpp/` | CMake projects and owned `.msg` definitions for upstream ROSIDL and FastRTPS generation. | Explicit `prepare_cpp()` call. |
| `rust/` | Cargo crate, owned `.msg` definitions, and a `ros2msg` build script. | Cargo. |
| `schemas/` | Resolved `.msg` closure and supplied schema licenses. | Schema consumers and native preparation. |
| `schemas.json` | Type names mapped to schema text with dependency closure. | Registry and schema consumers. |
| `message-package.json` | Package identity, ownership, ABI, exact dependencies, schema hashes, and unsupported semantics. | Generator, registry, and native preparation. |

## Python distribution

The generated project contains a value module such as `acme` and a schema module
such as `acme_schemas`. Its `dimos.messages` entry point exposes the schema provider.
The provider carries schemas and a source-package copy with native inputs.

Runtime message classes come from one rosbags typestore. Stub files describe
their typed imports without generating duplicate runtime classes. Installation
does not compile native libraries. Import does not rewrite the generated files.

## Native build results

`prepare_cpp()` returns a cache prefix containing generated headers, shared
libraries, and CMake exports. `write_cmake_toolchain()` writes a consumer
toolchain file using the saved prefixes and target settings. Those outputs are
separate from the source generation directory.

Cargo builds the generated Rust crate into its own target directory. The generated
`build.rs` writes Rust declarations to `OUT_DIR` during compilation.

## Regeneration

A successful generation removes stale message files and unselected language
directories. A failure preserves the previous output. Generated directories are
not application source directories and are not an appropriate place for manual
edits.
