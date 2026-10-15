<div class="cdrgen-lead" markdown>

# Message generation and CDR

Generate Python, C++, and Rust message packages from ROS 2 `.msg` definitions.
Encode and decode CDR without a ROS installation, the DimOS runtime, or a running
robot.

[Install the generator](install.md){ .md-button .md-button--primary }
[Read the compatibility limits](reference/compatibility.md){ .md-button }

</div>

## Start with a message

```text title="interfaces/example_msgs/msg/Reading.msg"
int32 sequence
float64 value
```

The [Python quickstart](quickstarts/python.md) generates this message and checks
a CDR round trip. The C++ and Rust quickstarts use the same project and fields.

<div class="grid cards cdrgen-languages" markdown>

-   ### [Python](quickstarts/python.md)

    Install the generated package. Import typed messages and use the Python CDR
    codec.

-   ### [C++](quickstarts/cpp.md)

    Prepare native libraries. Build a CMake consumer with the supplied CDR header.

-   ### [Rust](quickstarts/rust.md)

    Compile the generated crate with Cargo. Encode and decode with `re_cdr`.

</div>

## Generation and compilation

`dimos-cdrgen` reads local message definitions and the configuration in your
project's `pyproject.toml`. It writes installable Python sources, CMake sources,
a Cargo crate, and schema metadata. Generation does not run a native compiler.

The Python message package exposes native rosbags classes and typed imports.
Installing the generated Python project does not build a native extension.
Python import initializes a process-wide type registry without generating files.

C++ applications call `prepare_cpp()` explicitly to build pinned upstream
dependencies and message libraries. Rust applications compile their generated
crate with Cargo. These are separate steps from generation and Python installation.

The [artifact reference](reference/artifacts.md) describes each output and its
consumer. [Dependency reuse](guides/dependencies.md) explains how separate packages
share a message type without generating duplicate declarations.

## Scope

This library provides schemas, message values, and CDR encoding and decoding.
It does not provide ROS 2 nodes, DDS discovery, topic QoS, robot transports, or
MCAP recording. Schema and wire-format compatibility does not establish live
ROS 2 network interoperability.

The package metadata currently declares an alpha development version, `0.1.0`.
These instructions use local source and wheel installation. They do not assume
a PyPI release or a published standard-message catalog.

Read the [compatibility limits](reference/compatibility.md) before choosing
bounded fields, declared defaults, or a deployment platform.
