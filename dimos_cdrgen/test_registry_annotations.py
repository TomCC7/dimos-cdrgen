# Copyright 2026 Dimensional Inc.
# SPDX-License-Identifier: Apache-2.0

"""Configuration and codecs must share the registry's canonical nested classes."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

import pytest

from dimos_cdrgen.registry import ABI


def _package(root, name, schemas, owned, dependencies):
    module = root / (name + "_schemas")
    module.mkdir()
    (module / "__init__.py").write_text("")
    (module / "provider.py").write_text(
        "from pathlib import Path\ndef package_root(): return str(Path(__file__).parent / 'package')\n"
    )
    package = module / "package"
    package.mkdir()
    (package / "schemas.json").write_text(json.dumps(schemas))
    (package / "message-package.json").write_text(
        json.dumps(
            {
                "abi": ABI,
                "module": name,
                "version": "1.0.0",
                "dependencies": dependencies,
                "owned": owned,
                "schemas": {
                    name: sha256(value.encode()).hexdigest()
                    for name, value in schemas.items()
                },
            }
        )
    )
    values = root / name
    values.mkdir()
    (values / "__init__.py").write_text("")
    (values / "_types.py").write_text(
        "from pathlib import Path\nfrom dimos_cdrgen.registry import initialize\n"
        f"from {name}_schemas.provider import package_root\n"
        "store = initialize((Path(package_root()),))\n"
    )
    fields = {key.rsplit("/", 1)[-1]: key for key in owned}
    (values / "msg.py").write_text(
        "from ._types import store\n"
        + "".join(
            f"{short} = store.types[{full!r}]\n" for short, full in fields.items()
        )
    )


@pytest.mark.parametrize("first", ["external_messages", "base_messages"])
def test_nested_configuration_and_codec_types_are_canonical(tmp_path, first):
    base = {
        "builtin_interfaces/msg/Time": "int32 sec\nuint32 nanosec\n",
        "builtin_interfaces/msg/Duration": "int32 sec\nuint32 nanosec\n",
        "std_msgs/msg/Header": "builtin_interfaces/Time stamp\nstring frame_id\n",
    }
    custom = {
        **base,
        "custom_msgs/msg/Reading": (
            "std_msgs/Header header\nbuiltin_interfaces/Duration age\n"
            "builtin_interfaces/Time[] samples\nfloat64 value\n"
        ),
        "custom_msgs/msg/VectorReading": "std_msgs/Header header\nfloat64[] values\n",
    }
    _package(tmp_path, "base_messages", base, list(base), {})
    _package(
        tmp_path,
        "external_messages",
        custom,
        ["custom_msgs/msg/Reading", "custom_msgs/msg/VectorReading"],
        {"base_messages": "1.0.0"},
    )
    script = r"""
import sys, importlib, dataclasses, struct, typing
from pathlib import Path
sys.path[:0] = [sys.argv[1], sys.argv[2]]
from dimos_cdrgen import registry
assert Path(registry.__file__).resolve().parent.parent == Path(sys.argv[1]).resolve()
# Keep the fixture independent of unrelated message providers installed on the runner.
registry.providers = lambda: tuple(
    importlib.import_module(name + '_schemas.provider')
    for name in ('base_messages', 'external_messages')
)
importlib.import_module(sys.argv[3] + '.msg')
from external_messages.msg import Reading, VectorReading
from base_messages.msg import Header, Time, Duration
import numpy as np
from pydantic import BaseModel, ConfigDict
assert registry.message_types()['builtin_interfaces/msg/Time'] is Time
class ArrayConfiguration(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    reading: VectorReading
array_source = VectorReading(Header(Time(3, 4), 'array'), np.array([1.5, 2.5]))
array_value = ArrayConfiguration(reading=array_source).reading
assert array_value is array_source
for little_endian in (True, False):
    array_decoded = registry.decode(registry.encode(array_value, little_endian=little_endian), VectorReading)
    assert type(array_decoded.header.stamp) is Time
    np.testing.assert_array_equal(array_decoded.values, [1.5, 2.5])
class Configuration(BaseModel):
    reading: Reading
source = Reading(Header(Time(12, 34), 'sensor'), Duration(5, 6), [Time(8, 9)], 2.5)
restored = Configuration.model_validate_json(Configuration(reading=source).model_dump_json()).reading
assert type(restored.header) is Header
assert type(restored.header.stamp) is Time
assert type(restored.age) is Duration
assert type(restored.samples[0]) is Time
assert restored == source
assert typing.get_type_hints(Header)['stamp'] is Time
assert next(field for field in dataclasses.fields(Header) if field.name == 'stamp').type is Time
assert typing.get_args(typing.get_type_hints(Reading)['samples'])[0] is Time
for little_endian in (True, False):
    endian = '<' if little_endian else '>'
    expected = (b'\x00\x01\x00\x00' if little_endian else b'\x00\x00\x00\x00')
    expected += struct.pack(endian + 'iiI', 12, 34, 7) + b'sensor\0' + b'\0'
    expected += struct.pack(endian + 'iiIiid', 5, 6, 1, 8, 9, 2.5)
    payload = registry.encode(restored, little_endian=little_endian)
    assert payload == expected, (payload.hex(), expected.hex())
    decoded = registry.decode(payload, Reading)
    assert decoded == source
    assert type(decoded.header.stamp) is Time
    assert type(decoded.age) is Duration
    assert type(decoded.samples[0]) is Time
    assert type(registry.decode(registry.encode(Time(3, 4), little_endian=little_endian), Time)) is Time
"""
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            script,
            str(Path(__file__).resolve().parents[1]),
            str(tmp_path),
            first,
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
