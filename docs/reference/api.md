# Python API reference

These are the functions used by the project command, package hooks, and native
consumers. Paths are `pathlib.Path` values. Imports below identify their modules.

## Project generation and package hooks

`dimos_cdrgen.source_package` exposes these functions:

| Function | Result |
| --- | --- |
| `configuration(project)` | Parsed configuration dictionary with resolved paths and loaded `Dependency` values. |
| `prepare(project, output=None)` | Generates all languages with dependency ownership enabled. Returns the generated `python` directory. The default artifact root is `project / "build/message-source"`. |
| `setup_arguments(project)` | Generates sources and returns setuptools settings, including schema data, a provider entry point, and the source-distribution hook. |
| `package_settings(project)` | Generates sources and returns `wheel` package mappings and `sdist` includes for an external build adapter. |

The hooks generate sources. They do not install toolchains, fetch native sources,
or invoke CMake or Cargo. `package_settings()` is a settings API, not a standalone
PEP 517 build backend. The external `dimos-build-config` integration is separate
from this repository.

A setuptools consumer can call the shared hook from its `setup.py`:

```python
from pathlib import Path
from setuptools import setup
from dimos_cdrgen.source_package import setup_arguments

setup(**setup_arguments(Path(__file__).resolve().parent))
```

That consumer's build environment must already provide `dimos-cdrgen` and its
message dependencies. Source files and `pyproject.toml` must be included in its
source archive. Local artifacts or an explicit wheelhouse can supply development
versions without a registry release.

## Direct generation

`dimos_cdrgen.generate.generate` has this signature:

```python
generate(
	roots: list[Path],
	output: Path,
	names: list[str] | None = None,
	module: str = "dimos_generated",
	*,
	installed: bool = False,
	version: str = "0.1.0",
	dependencies: tuple[Dependency, ...] = (),
	shared: bool = False,
	languages: tuple[str, ...] = ("python", "cpp", "rust"),
) -> tuple[str, ...]
```

The result contains resolved type names. `installed=True` adds schema roots from
installed providers. It does not declare ownership by itself.
`dependencies` supplies ownership contracts loaded by
`dimos_cdrgen.ownership.Dependency.load(package_root)`.
`shared=True` marks a package for dependency reuse and C++ preparation.
The project command sets `shared=True` automatically.

`languages` selects any nonempty subset of `python`, `cpp`, and `rust`.
Selecting only Python can generate sources for schemas that native generation
rejects. It does not make unsupported Python codec semantics available.

## Python registry and codecs

`dimos_cdrgen.registry` exposes the following functions:

| Function | Result or behavior |
| --- | --- |
| `encode(value, *, little_endian=True)` | CDR bytes including the encapsulation header. Requires a value class owned by the frozen registry. |
| `decode(data, name)` | Decoded native value. `name` is a generated class or a `package/msg/Type` string. Malformed CDR errors caught by the codec become `ValueError`. |
| `schema(name)` | Original schema text with its dependency closure. |
| `message_types()` | Copy of the type-name-to-class mapping. |
| `initialize(roots=(), *, discover=True)` | Initializes the rosbags typestore. `roots` is a tuple of source-package paths. Discovery loads installed `dimos.messages` providers. |
| `providers()` | Tuple of installed schema provider modules. |
| `schema_roots()` | Tuple of provider schema directories. |

The registry checks ABI, package versions, schema hashes, and unique ownership.
It freezes once initialized. A later changed package raises `RuntimeError` and
requires a process restart. Unsupported bounds raise `NotImplementedError` on
encoding or decoding.

## Native preparation

`dimos_cdrgen.native_build` exposes the functions used in the C++ quickstart:

```python
prepare_cpp(
	root: Path,
	*,
	cache: Path | None = None,
	offline: bool = False,
	source_dirs: dict[str, Path] | None = None,
) -> Path

write_cmake_toolchain(prefix: Path, destination: Path) -> Path
```

`root` is the artifact root containing `message-package.json` and `schemas`.
The default cache is `$XDG_CACHE_HOME/dimos/native`, or `~/.cache/dimos/native`
when the environment variable is unset. `source_dirs` maps pinned upstream
project names to prepared source directories. Offline mode requires the verified
sources and build prerequisites to exist already.

Preparation builds the package and its dependency-owned C++ types.
The returned prefix carries installed headers, libraries, exports, and target
settings. The exported toolchain preserves those settings for consumer builds.
