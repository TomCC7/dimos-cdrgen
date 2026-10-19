---
name: verify-dimos-cdrgen
description: Verify dimos-cdrgen through installed Python packages, explicit C++/Rust consumers, cross-package CDR exchange, and generation recovery. Use after generator, packaging, codec, or native-build changes.
---

# Verify dimos-cdrgen

Read [the feature map](features/README.md) and select the affected paths. This is
an agent recipe using existing tests, not a new test framework. Run from the
repository root in Bash or Zsh with `set -euo pipefail`. Never count skips as proof.

## Launch

There is no service or port. Use a disposable virtual environment with Python
3.10 or newer. The tested local environment is Linux x86_64, Python 3.12.
Install the dependencies declared in `pyproject.toml` for `test`, `prepare`, and
`native`, plus `build`, setuptools >=77, and wheel. Use an existing provisioned
environment when available. No system or global installs are part of this recipe.

Prepare the parser before installing the checkout. The README documents online
preparation; prefer verified cached archives when working offline:

```sh
python dimos_cdrgen/prepare_parser.py --offline --cache "$PARSER_CACHE"
python -m pip install --no-build-isolation '.[test,native]'
```

`PARSER_CACHE` is a prepared archive directory, not an arbitrary extracted parser.
For offline pip operations provide a compatible wheelhouse and set
`PIP_NO_INDEX=1` and `PIP_FIND_LINKS` to that directory. A missing archive or wheel
is a failed prerequisite, not permission to download or bypass verification.

Create a fresh run directory; do not share it with another verification:

```sh
mkdir -p build
RUN_DIR=$(mktemp -d "$PWD/build/verify.XXXXXX")
mkdir -p "$RUN_DIR/evidence" "$RUN_DIR/scratch"
export PYTHONPATH="$PWD"
git rev-parse HEAD > "$RUN_DIR/evidence/head.txt"
git diff --binary > "$RUN_DIR/evidence/working-tree.patch"
python --version > "$RUN_DIR/evidence/python.txt"
```

Record non-default environment variable paths
in the evidence. Do not record secrets. Tests create their own temporary projects.

## Doctor

Before running a journey, check the interpreter and imported checkout:

```sh
python -c 'import pathlib, pytest, dimos_cdrgen; assert pathlib.Path(dimos_cdrgen.__file__).resolve().parent == pathlib.Path("dimos_cdrgen").resolve(); print("checkout and pytest OK")'
python -m pytest --collect-only -q dimos_cdrgen/test_generation_transaction.py dimos_cdrgen/test_source_package.py
```

For native checks also run `cmake --version`, `c++ --version`, `cargo --version`,
and `rustc --version`. Record them. Compilation requires CMake >=3.20, a C++17
compiler, Rust/Cargo, the Python native dependencies, and pinned upstream sources.
A tool's presence is not a successful consumer build.

## Drive

Fast path, with no native compiler or schema downloads:

```sh
python -m pytest dimos_cdrgen/test_generation_transaction.py dimos_cdrgen/test_source_package.py \
  -k 'not generic_cold' -q --basetemp="$RUN_DIR/scratch/fast" \
  --junitxml="$RUN_DIR/evidence/fast.xml" 2>&1 | tee "$RUN_DIR/evidence/fast.log"
```

Require eight passing tests. This covers configuration errors, explicit CLI
regeneration after a rename, and preservation of output after failed generation.

Full checks are the installation and native recipes in the feature map. Run
both for a packaging/native ownership change. For broader regression coverage,
prepare test schemas with the command below, then run `python -m pytest
dimos_cdrgen` with the same acceptance variables and separate log/JUnit paths.
Inspect every skip and expected failure rather than treating exit zero as full
acceptance. Known unsupported bounds remain explicit expected failures.

## Evidence

Keep command lines, stdout/stderr, JUnit results, tested Git HEAD and dirty diff.
Native proof also includes `input.cdr`, `cpp.cdr`, and `rust.cdr`. Tests assert
literal results and type identity; timestamps or successful compilation alone
are not sufficient. For installation, the test drives pip in a fresh venv and
uses isolated Python subprocesses outside the source checkout.

Report each feature as passed, failed, blocked by a named prerequisite, or not
run. This recipe does not establish macOS/Windows support, other Python versions,
live ROS/DDS behavior, hardware operation, registry publication, or the external
DimOS adapter. Do not infer those results from local Linux tests.

## Cleanup

After success or failure, remove only this run's scratch directory. Tests use
short-lived subprocesses; no daemon is expected. Never kill processes by name.
Preserve shared dependency caches, prepared inputs, and all evidence:

```sh
python -c 'import pathlib, shutil, sys; p=pathlib.Path(sys.argv[1]); assert p.name.startswith("verify.") and p.parent.resolve()==pathlib.Path("build").resolve(); shutil.rmtree(p/"scratch", ignore_errors=True); assert (p/"evidence").is_dir()' "$RUN_DIR"
```

Confirm the log and JUnit files still exist after cleanup. Do not commit generated
packages, archives, caches, or raw run output. Keep a short result note when useful.

## Helpers and maintenance

No new executable helper is needed. The existing pytest tests are the drivers.
When behavior changes, update the affected feature recipe and execute it again.
Upstream `maintain-verification-skill` provides an optional audit workflow; it is
not installed or required to run this verifier.

Created using `create-verification-skill` and its feature-map template from
[backnotprop/pstack@1f0f9c3](https://github.com/backnotprop/pstack/tree/1f0f9c3bac03c4297f6fc8f7644fa412eda57085/skills/create-verification-skill).
The upstream MIT notice is retained in [LICENSE.pstack](../LICENSE.pstack).
