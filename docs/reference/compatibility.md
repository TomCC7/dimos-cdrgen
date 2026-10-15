# Compatibility and limits

## Message semantics

The generated `message-package.json` records unsupported semantics for each
language and the types with declared defaults. Limits apply to a message's
dependency closure as well as its own fields.

| Declaration or behavior | Current contract |
| --- | --- |
| Bounded strings or bounded sequences in Python. | Schemas retain bounds, but rosbags does not enforce them. `encode()` and `decode()` reject affected types. |
| Bounded strings in C++. | Generation rejects them because upstream FastRTPS does not enforce the declared bound. |
| Bounded strings in Rust. | Generation rejects them because native semantics are not validated. |
| `wstring` in Rust. | Generation rejects it because the `re_cdr` mapping is not validated. |
| Declared defaults in Python. | Construction requires explicit fields. Preserved schema defaults do not become implicit constructor defaults. |
| Declared defaults in Rust. | Construction requires explicit fields. Upstream `Default` generation is unsupported. |
| C++ default construction. | Uses upstream-generated constructors. |
| Noncanonical bytes in bool arrays. | Rejection remains a known expected-failure case in `test_definitions.py`. Do not rely on strict validation of every malformed wire value. |

The project command generates every language. A Rust or C++ restriction can
therefore stop project generation even when Python source generation is possible.
The [direct API](api.md#direct-generation) can select languages explicitly.

## Dependencies and lifecycle

The tool pins rosbags to `0.11.0` and records a codec ABI in each message package.
Dependencies must agree on exact versions, ownership, and schema hashes.
Rust requires one owner crate per ROS message package. A new message cannot share
a dependency-owned ROS package, and dependencies cannot split that package across
crates. The project command includes Rust; use the direct API with
`languages=("python",)` when only Python generation is needed.

Changing a schema requires regeneration, package reinstallation, and a restart
of processes that initialized the registry.

The Python tool does not bundle a standard ROS message catalog.
Generated Cargo package copies need explicit dependency resolution, as described
in [dependency reuse](../guides/dependencies.md#rust-dependency-resolution).

## Platforms and verification

The package metadata requires Python 3.10 or newer. The repository verification
recipe identifies Linux x86_64 with Python 3.12 as its tested local environment.
That is not a completed release matrix for every declared Python version.

The native code includes macOS SDK and target handling. Those code paths and
simulated platform tests do not establish a successful macOS consumer build.
Windows native support is not established by these docs. Validate the actual
compiler, architecture, SDK, and dependency closure for your deployment.

The existing native acceptance test compiles separate Python, C++, and Rust
consumers, checks shared dependency types, and exchanges CDR artifacts.
It requires explicit opt-in and prepared inputs. Its presence is not a claim
that a particular checkout has passed it. See the repository's
[verification recipes](https://github.com/TomCC7/dimos-cdrgen/blob/main/.agents/skills/verify-dimos-cdrgen/SKILL.md).

## Transport scope

CDR and schema interoperability do not implement ROS 2 nodes, discovery,
transport delivery, QoS, or a DDS participant. This package does not run hardware
or record MCAP. Those concerns belong to consumers of its values and schemas.
