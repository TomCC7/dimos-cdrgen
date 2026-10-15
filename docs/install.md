# Install the generator

Build a local wheel from this repository. Python 3.10 or newer is required.
The commands below use an isolated environment and run from the repository root.

## Prepare and build the wheel

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install 'requests>=2.31' build 'setuptools>=77' wheel
python dimos_cdrgen/prepare_parser.py
python -m build --no-isolation
python -m pip install dist/dimos_cdrgen-0.1.0-py3-none-any.whl
dimos-cdrgen --help
```

The help output lists one optional positional argument, `project`.
The preparation command downloads the pinned ROSIDL parser source and verifies
its hash. The wheel and source archive include the prepared parser and its
license. Installing either artifact does not fetch upstream parser source.

A checkout without the prepared parser fails during build or installation.
Run preparation before `python -m pip install .` as well.

## Use cached parser sources

To prepare without network access, use a cache populated by a previous successful
preparation:

```sh
python dimos_cdrgen/prepare_parser.py --offline --cache /path/to/parser-cache
```

To use a downloaded archive, supply its path:

```sh
python dimos_cdrgen/prepare_parser.py --offline --archive /path/to/rosidl.tar.gz
```

The archive must match the pinned hash in `dimos_cdrgen/parser-source.json`.
Offline Python installation also needs a wheelhouse containing the normal build
and runtime dependencies. A parser cache does not supply those dependencies.

## Choose the next step

[Generate a Python message](quickstarts/python.md) with the installed tool.
Install the `native` extra only when you need [C++ compilation](quickstarts/cpp.md).
Rust compilation uses Cargo and the generated crate's dependencies.

The [documentation environment](contributing-docs.md) is separate. Building this
website does not install the generator, prepare the parser, or build messages.
