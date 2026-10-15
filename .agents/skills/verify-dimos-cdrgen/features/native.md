# Compile consumers and exchange CDR

Separate packages share one dependency type in Python, C++, and Rust.

## Sub-features

- `cpp`: find the generated CMake package and link its exported target.
- `rust`: compile generated crates and assign the dependency-owned Header type.
- `exchange`: Python to C++ to Rust to Python with schema/version validation.

## How to get to it (user POV)

Call `prepare_cpp()` and `write_cmake_toolchain()`, then use CMake
`find_package` and link `<module>::messages`. Use the generated Cargo crate as a
dependency and run Cargo. Python consumers use `registry.encode` and `decode`.

## Driving it with pytest

Preconditions: native toolchains from Doctor, a populated Cargo cache, and
verified upstream native sources/cache. Set `DIMOS_NATIVE_TEST_CACHE` to an
explicit writable cache. If needed, set `DIMOS_NATIVE_SOURCE_DIRS` to a JSON map
of pinned source names to prepared directories. Do not silently fetch replacements.

Prepare the schema fixture closure first, using its pinned hashes:

```sh
python -m dimos_cdrgen.prepare_test_inputs --offline --cache "$SCHEMA_CACHE"
DIMOS_OFFLINE=1 DIMOS_NATIVE_ACCEPTANCE=1 \
DIMOS_OWNERSHIP_EVIDENCE="$RUN_DIR/evidence/cdr" \
python -m pytest dimos_cdrgen/test_native_consumer.py -q \
  --basetemp="$RUN_DIR/scratch/native" \
  --junitxml="$RUN_DIR/evidence/native.xml" 2>&1 | tee "$RUN_DIR/evidence/native.log"
```

Require one pass without skips and three CDR files in the evidence directory.
The consumer compiles actual C++ and Rust code. Python starts value `20.5`, C++
and Rust each increment it, and Python asserts `22.5`, frame `map`, and nanoseconds
`123456789`. Python identity, C++ static type equality, Rust assignment, independent
rosbags decoding, and rejection of changed schema hashes/versions must all pass.

## Gotchas

Missing schema archives, native source caches, or Cargo crates block offline
acceptance. Record the exact missing input; do not disable offline mode merely
to make the check pass. This is a local codec exchange, not live ROS 2 networking.
