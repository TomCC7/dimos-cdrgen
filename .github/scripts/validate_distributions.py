#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Validate built distributions and installed consumers without network access."""

import argparse
from email.parser import BytesParser
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory
import tomllib
import zipfile


def run(command: list[str], cwd: Path, environment: dict[str, str]) -> None:
    print("+", *command, flush=True)
    subprocess.run(command, cwd=cwd, env=environment, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, default=Path("dist"))
    parser.add_argument("--wheelhouse", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    distributions = args.dist_dir.resolve()
    wheelhouse = args.wheelhouse.resolve()
    if not wheelhouse.is_dir():
        parser.error(
            "--wheelhouse must contain prepared build and runtime dependency wheels"
        )
    wheels = list(distributions.glob("*.whl"))
    sdists = list(distributions.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1 or len(list(distributions.iterdir())) != 2:
        parser.error("--dist-dir must contain exactly one wheel and one source archive")
    version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    lock = json.loads((root / "dimos_cdrgen/parser-source.json").read_text())
    environment = {
        key: value for key, value in os.environ.items() if key != "PYTHONPATH"
    }
    environment.update(
        PIP_NO_INDEX="1",
        PIP_FIND_LINKS=str(wheelhouse),
        PIP_DISABLE_PIP_VERSION_CHECK="1",
        PIP_NO_CACHE_DIR="1",
    )
    with TemporaryDirectory(prefix="dimos-cdrgen-distributions-") as temporary:
        scratch = Path(temporary)
        run(
            [
                sys.executable,
                "-m",
                "twine",
                "check",
                "--strict",
                *map(str, wheels + sdists),
            ],
            scratch,
            environment,
        )
        with tarfile.open(sdists[0]) as archive:
            archive.extractall(scratch / "sdist", filter="data")
        (source,) = (scratch / "sdist").iterdir()
        prepared = source / "dimos_cdrgen/.upstream/rosidl_adapter"
        assert (
            sha256((prepared / "parser.py").read_bytes()).hexdigest()
            == lock["parser_sha256"]
        )
        assert b"Apache License" in (prepared / "LICENSE").read_bytes()
        for name in ("LICENSE", "NOTICE"):
            assert (source / name).read_bytes() == (root / name).read_bytes()
        rebuilt = scratch / "rebuilt"
        run(
            [
                sys.executable,
                "-m",
                "build",
                "--wheel",
                "--no-isolation",
                "--outdir",
                str(rebuilt),
                str(source),
            ],
            scratch,
            environment,
        )
        (rebuilt_wheel,) = rebuilt.glob("*.whl")
        run(
            [sys.executable, "-m", "twine", "check", "--strict", str(rebuilt_wheel)],
            scratch,
            environment,
        )
        for number, wheel in enumerate([wheels[0], rebuilt_wheel]):
            with zipfile.ZipFile(wheel) as archive:
                names = archive.namelist()
                (metadata_name,) = (
                    name for name in names if name.endswith(".dist-info/METADATA")
                )
                metadata = BytesParser().parsebytes(archive.read(metadata_name))
                assert metadata["Name"] == "dimos-cdrgen"
                assert metadata["Version"] == version
                assert (
                    sha256(archive.read("rosidl_adapter/parser.py")).hexdigest()
                    == lock["parser_sha256"]
                )
                assert (
                    archive.read("rosidl_adapter/LICENSE")
                    == (prepared / "LICENSE").read_bytes()
                )
                for name in ("LICENSE", "NOTICE"):
                    (license_name,) = (
                        item
                        for item in names
                        if item.endswith(".dist-info/licenses/" + name)
                    )
                    assert archive.read(license_name) == (root / name).read_bytes()
                assert not any("/test_" in name for name in names)
            consumer = scratch / f"consumer-{number}"
            consumer.mkdir()
            venv = consumer / "venv"
            run([sys.executable, "-m", "venv", str(venv)], consumer, environment)
            python = str(venv / "bin/python")
            run(
                [python, "-m", "pip", "install", "setuptools", "wheel", str(wheel)],
                consumer,
                environment,
            )
            run([python, "-m", "pip", "check"], consumer, environment)
            message = consumer / "interfaces/example_msgs/msg/Reading.msg"
            message.parent.mkdir(parents=True)
            message.write_text("int32 sequence\nfloat64 value\n")
            (consumer / "pyproject.toml").write_text(
                '[project]\nname = "cdrgen-release-smoke"\nversion = "0.1.0"\n'
                '[tool.dimos.messages]\nsource = "interfaces"\n'
            )
            run([str(venv / "bin/dimos-cdrgen")], consumer, environment)
            run(
                [
                    python,
                    "-m",
                    "pip",
                    "install",
                    "--no-build-isolation",
                    str(consumer / "build/message-source/python"),
                ],
                consumer,
                environment,
            )
            check = """
from importlib.util import find_spec
from pathlib import Path
import dimos_cdrgen
from cdrgen_release_smoke.example_msgs.msg import Reading
from dimos_cdrgen.registry import decode, encode
assert find_spec('dimos') is None
assert find_spec('rclpy') is None
assert Path(dimos_cdrgen.__file__).resolve().is_relative_to(Path('venv').resolve())
wire = encode(Reading(sequence=1, value=21.5))
assert bytes(wire).hex() == '0001000001000000000000000000000000803540', bytes(wire).hex()
restored = decode(wire, Reading)
assert type(restored) is Reading
assert restored.sequence == 1
assert restored.value == 21.5
print('Installed standalone generation and CDR roundtrip passed')
"""
            run([python, "-I", "-c", check], consumer, environment)
        print(
            "Wheel, offline sdist rebuild, metadata, licenses, parser hash, and both clean consumers passed"
        )


if __name__ == "__main__":
    main()
