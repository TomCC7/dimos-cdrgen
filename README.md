# DimOS message generation and CDR

A standalone `.msg` generator and CDR toolkit for Python, C++ and Rust. It does
not depend on the DimOS runtime, a ROS installation, or a running robot.
The package is named `dimos-cdrgen` (import `dimos_cdrgen`). No registry release
is assumed by these instructions.

## Documentation

The [documentation source](docs/index.md) includes installation, Python, C++, and
Rust quickstarts, dependency reuse, and CLI/API references. To build and preview
the MkDocs site locally, follow [the docs maintenance guide](docs/contributing-docs.md).
The site build uses its own locked environment and does not install this package.
The [publishing guide](docs/publishing.md) covers local distribution validation,
the default GitHub dry-run, and approval of registry ownership and OIDC setup.

## Install the tool

From this package directory, prepare the pinned upstream parser and build local
artifacts. The preparation environment needs `requests`; the build environment
needs `build`, setuptools 77 or newer, and wheel.

```sh
python dimos_cdrgen/prepare_parser.py
python -m build --no-isolation
python -m pip install dist/dimos_cdrgen-0.1.0-py3-none-any.whl
```

The wheel and source archive contain the unchanged, hash-verified ROSIDL parser
and its license. Installing either artifact does not download upstream source.
A checkout with no prepared parser fails with an explicit preparation error.
Use `--offline` with a populated cache, or `--archive /path/to/rosidl.tar.gz`.
Normal Python dependencies must also be available for an offline installation.

## Define and generate a message

In a separate directory, create `interfaces/example_msgs/msg/Reading.msg`:

```text
int32 sequence
float64 value
```

Create `pyproject.toml`:

```toml
[project]
name = "acme"
version = "0.1.0"

[tool.dimos.messages]
source = "interfaces"
```

```sh
dimos-cdrgen
python -m pip install build/message-source/python
```

Generation reads the configuration and writes the following artifacts. It does
not invoke a compiler or install a system toolchain.

| Path under `build/message-source` | Artifact |
| --- | --- |
| `python/` | Installable Python project, type stubs and schema provider. |
| `cpp/` | CMake projects and owned `.msg` sources for upstream ROSIDL/FastRTPS. |
| `rust/` | Cargo crate, `.msg` sources and a ros2msg `build.rs`. |
| `schemas/`, `schemas.json` | Complete schema closure, including dependency messages. |
| `message-package.json` | Ownership, exact dependency versions, hashes and ABI. |

### Python

```python
from acme.example_msgs.msg import Reading
from dimos_cdrgen.registry import encode, decode

message = Reading(sequence=1, value=21.5)
assert decode(encode(message), Reading).value == 21.5
```

Runtime values and codecs use rosbags. Python wheels need no native compiler;
there is no pybind extension. Import initializes the type registry without
writing generated files or compiling code. Numeric arrays use NumPy.

### C++

Install the tool's `native` extra and supply CMake plus a C/C++ compiler.
Prepare the generated package explicitly; pinned upstream dependencies are
fetched and verified here, not during Python import or installation.

```python
from pathlib import Path
from dimos_cdrgen.native_build import prepare_cpp, write_cmake_toolchain

prefix = prepare_cpp(Path("build/message-source"))
write_cmake_toolchain(prefix, Path("build/acme-toolchain.cmake"))
```

For an application containing `main.cpp`, use:

```cmake
cmake_minimum_required(VERSION 3.20)
project(reader LANGUAGES CXX)
find_package(acme CONFIG REQUIRED)
add_executable(reader main.cpp)
target_compile_features(reader PRIVATE cxx_std_17)
target_link_libraries(reader PRIVATE acme::messages)
```

```cpp
#include <example_msgs/msg/reading.hpp>
#include <dimos_cdrgen/cdr.hpp>
int main() {
    example_msgs::msg::Reading message;
    message.sequence = 1;
    message.value = 21.5;
    auto wire = dimos::cdr::cdr_encode(message);
    auto decoded = dimos::cdr::cdr_decode<example_msgs::msg::Reading>(wire);
    return decoded.value == 21.5 ? 0 : 1;
}
```

```sh
cmake -S . -B build/app -DCMAKE_TOOLCHAIN_FILE="$PWD/build/acme-toolchain.cmake"
cmake --build build/app
./build/app/reader
```

The prefix contains generated headers, shared libraries and CMake exports.
The CDR helper is supplied by this library, with no DimOS SDK include path.
For offline preparation, use `prepare_cpp(..., offline=True)` with a populated
verified source/build cache. macOS also requires Apple's SDK and command-line tools.

### Rust

In a Cargo application next to `build/`, declare:

```toml
[workspace]
exclude = ["build/message-source/rust"]

[dependencies]
acme-messages = { path = "build/message-source/rust" }
re_cdr = "=0.1.0"
```

```rust
use acme_messages::example_msgs::msg::reading::Reading;
fn main() {
    let message = Reading { sequence: 1, value: 21.5 };
    let body = re_cdr::to_vec::<_, re_cdr::LittleEndian>(&message).unwrap();
    let mut wire = vec![0, 1, 0, 0]; // plain little-endian CDR encapsulation
    wire.extend(body);
    let (decoded, used) =
        re_cdr::from_bytes::<Reading, re_cdr::LittleEndian>(&wire[4..]).unwrap();
    assert_eq!(decoded.value, 21.5);
    assert_eq!(used, wire.len() - 4);
}
```

`cargo run` invokes ros2msg through the generated `build.rs`, writes declarations
into Cargo's `OUT_DIR`, and compiles the crate into the application. Use
`cargo run --offline` with cached dependencies. This does not create a Python
extension or publish a crate.

## Dependency ownership and DimOS integration

Standard ROS message definitions are a separate catalog, not bundled here.
Declare an installed message package in `tool.dimos.messages.dependencies` with
its exact module/version. The generator imports its Python types, links its C++
declarations, and reuses its Rust crate types. It rejects conflicting ownership,
versions and schema hashes. The full schema closure remains available for MCAP
schema registration by consumers; this library itself does not record MCAP.

The DimOS `dimos-build-config` adapter from PR #4461 calls this library's
`package_settings()` to support `pip install .` and editable projects alongside
blueprint declarations. Existing setuptools callers can use `setup_arguments()`.
Both call the same `prepare()` implementation as `dimos-cdrgen`.
Neither requires copying the generator into a DimOS application. Reinstall an
editable message project and restart Python processes after changing `.msg` files.

The codec provides schema/CDR interoperability. It does not implement a ROS 2
node, DDS discovery, topic QoS, or live ROS 2 network interoperability. Unsupported
bounds and declared-default semantics remain explicit in the generated manifest
and the [known limitations](https://github.com/dimensionalOS/dimos/blob/cc/feat/remove-lcm-encoding/docs/development/message-limitations.md).

## Run tests from this package alone

```sh
python -m pip install '.[test,native]'
PYTHONPATH=. python -m dimos_cdrgen.prepare_test_inputs
PYTHONPATH=. python -m pytest dimos_cdrgen
# Explicit compiled Python/C++/Rust exchange (requires native toolchains):
PYTHONPATH=. DIMOS_NATIVE_ACCEPTANCE=1 python -m pytest dimos_cdrgen/test_native_consumer.py
```

Test preparation downloads only pinned public upstream test schemas. Use
`--offline --cache /path/to/verified/archives` to reuse archives. Native acceptance
can use `DIMOS_OFFLINE=1`, `DIMOS_NATIVE_TEST_CACHE`, and `DIMOS_NATIVE_SOURCE_DIRS`
(a JSON map of upstream project names to prepared source directories). Isolated
installation tests require `DIMOS_MESSAGE_WHEELHOUSE` containing the Python build
and runtime dependency wheels. The optional joint DimOS adapter test also needs
`DIMOS_BUILD_CONFIG_SOURCE`; it is not required to use the standalone library.

## Prepare a release; do not publish yet

Use the [publishing guide](docs/publishing.md) for the locked build environment,
standalone consumer checks, and manual `dry-run`, `testpypi`, or `pypi` workflow.
The default `dry-run` never uploads. A real upload requires an approved registry
account and project, Trusted Publisher configuration, and a matching version tag.

1. Confirm the authorized registry account and publishing destination.
   The current `0.1.0` metadata is a development candidate, not an existing release.
2. Prepare the pinned parser, then build the wheel and sdist in a clean directory.
   Retain upstream licenses and source hashes. Do not commit prepared upstream code.
3. Run `python -m twine check dist/*`, install the wheel in a clean environment,
   rebuild from the sdist offline, and run the language/dependency acceptance tests.
4. Choose the supported Python/platform matrix and verify those targets before
   declaring release support. Linux checks alone do not validate macOS.
5. Only after approval of the account and destination, use the registry's
   authorized publishing flow. No upload command is part of build or install.

C++ prefixes and generated Rust crates are separate native build artifacts.
Publishing the Python tool does not publish a standard-message catalog or Cargo
packages. Packaged Rust dependencies use exact versions and need normal Cargo
resolution (local patches/workspaces or separately published dependency crates).
