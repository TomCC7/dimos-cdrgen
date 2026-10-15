# Install and use Python message packages

Authors and consumers install generated packages without C++ or Rust compilation.

## Sub-features

- `source`: build from a source project in an isolated pip environment.
- `archives`: rebuild/install an sdist and install its wheel.
- `editable`: reinstall after a message changes and observe the new schema.
- `identity`: preserve dependency types across construction, decoding, and pickle.

## How to get to it (user POV)

Use `pip install .`, install an application wheel or sdist, or use `pip install -e .`
with the setuptools integration described by `setup_arguments()`.

## Driving it with pytest

Preconditions: a compatible wheelhouse containing all Python build/runtime
dependencies, including NumPy and rosbags, and the prepared parser. Set
`DIMOS_MESSAGE_WHEELHOUSE` to its absolute directory. No registry is used.

```sh
DIMOS_MESSAGE_INSTALL_REQUIRED=1 python -m pytest \
  'dimos_cdrgen/test_source_package.py::test_generic_cold_source_wheel_sdist_editable_and_dependency_identity[setuptools]' \
  -q --basetemp="$RUN_DIR/scratch/install" \
  --junitxml="$RUN_DIR/evidence/install.xml" 2>&1 | tee "$RUN_DIR/evidence/install.log"
```

Require one pass and no skips. The test builds the current tool wheel, inspects
its packaged license/header and absence of standard messages, blocks native
compilers, and uses a clean venv. Isolated consumers assert shared `Stamp` type
identity, CDR/pickle round trips, full dependency schema, and changed editable
schema after reinstallation. Both archive installation paths must complete.

## Gotchas

This tests generated application source/sdist/wheel installation using the tool
wheel. It does not independently prove rebuilding the tool's own sdist. Use the
README release checks for that extra gate. The scikit parameter is not claimed:
the current test overwrites its `backend` selector with a wheel Path before later
branches, so its name alone is not evidence of the external adapter path.
