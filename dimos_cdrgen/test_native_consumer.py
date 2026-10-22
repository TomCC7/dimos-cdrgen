# Copyright 2026 Dimensional Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from dimos_cdrgen.generate import generate
from dimos_cdrgen.native_build import prepare_cpp, write_cmake_toolchain
from dimos_cdrgen.ownership import Dependency
from dimos_cdrgen.prepare_test_inputs import OUTPUT as TEST_INPUTS


@pytest.fixture(autouse=True)
def restore_reference_types_module():
    # Independent oracle stores own a process-global module. Restore it so they
    # do not invalidate the canonical registry's native class pickle identities.
    previous = sys.modules.get("rosbags.usertypes")
    try:
        yield
    finally:
        if previous is None:
            sys.modules.pop("rosbags.usertypes", None)
        else:
            sys.modules["rosbags.usertypes"] = previous


@pytest.mark.parametrize("little_endian", [False, True], ids=["be", "le"])
@pytest.mark.parametrize("nested", [False, True], ids=["flat", "nested"])
def test_separate_packages_share_types_and_exchange_cdr(
    tmp_path, monkeypatch, nested, little_endian
):
    if os.environ.get("DIMOS_NATIVE_ACCEPTANCE") != "1":
        pytest.skip(
            "Set DIMOS_NATIVE_ACCEPTANCE=1 to run the compiled ownership contract"
        )
    source = tmp_path / "interfaces/custom_msgs/msg/Reading.msg"
    source.parent.mkdir(parents=True)
    source.write_text(
        "std_msgs/Header header\nfloat64 value\nfloat64[36] covariance\nstring label\nuint8[] pixels\nfloat32[] points\nint32[] empty\nsensor_msgs/Image image\nsensor_msgs/PointCloud2 cloud\n"
    )
    base, custom = tmp_path / "base", tmp_path / "custom"
    base_python = "robot.base" if nested else "ownership_base"
    custom_python = "robot.custom" if nested else "ownership_custom"
    generate(
        [TEST_INPUTS],
        base,
        ["std_msgs/msg/Header", "sensor_msgs/msg/Image", "sensor_msgs/msg/PointCloud2"],
        "ownership_base",
        shared=True,
        python_module=base_python,
    )
    generate(
        [source.parents[2]],
        custom,
        ["custom_msgs/msg/Reading"],
        "ownership_custom",
        python_module=custom_python,
        dependencies=(Dependency.load(base),),
        shared=True,
    )
    monkeypatch.syspath_prepend(str(base / "python"))
    sources = {
        name: Path(path)
        for name, path in json.loads(
            os.environ.get("DIMOS_NATIVE_SOURCE_DIRS", "{}")
        ).items()
    }
    cache = os.environ.get("DIMOS_NATIVE_TEST_CACHE")
    prefix = prepare_cpp(
        custom,
        cache=Path(cache) if cache else None,
        offline=os.environ.get("DIMOS_OFFLINE") == "1",
        source_dirs=sources or None,
    )
    toolchain = write_cmake_toolchain(prefix, tmp_path / "toolchain.cmake")
    (tmp_path / "dimos_cdrgen").symlink_to(
        Path(__file__).parent, target_is_directory=True
    )
    env = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(
            [str(tmp_path), str(base / "python"), str(custom / "python")]
        ),
    }
    bootstrap = """
from pathlib import Path
from dimos_cdrgen import registry
registry.providers = lambda: ()
registry.initialize((Path("base"), Path("custom")), discover=False)
"""
    python = """
import numpy as np
from ownership_base.std_msgs.msg import Header
from ownership_base.builtin_interfaces.msg import Time
from ownership_custom.custom_msgs.msg import Reading
from ownership_base.sensor_msgs.msg import Image, PointCloud2, PointField
from pathlib import Path
h = Header(stamp=Time(sec=0, nanosec=0), frame_id='map')
h.stamp.sec = 1700000000
h.stamp.nanosec = 123456789
msg = Reading(header=h, value=20.5, covariance=np.arange(36, dtype=np.float64), label='相机/café', pixels=np.array([0, 1, 127, 255], dtype=np.uint8), points=np.array([1.25, -2.5], dtype=np.float32), empty=np.array([], dtype=np.int32), image=Image(h, 1, 1, 'rgb8', 0, 3, np.array([255, 0, 1], dtype=np.uint8)), cloud=PointCloud2(h, 1, 1, [PointField('x', 0, 7, 1)], False, 4, 4, np.array([1.25], dtype='<f4').view(np.uint8), True))
assert type(msg.header) is Header
msg.header = h
assert type(registry.decode(registry.encode(msg), Reading).header) is Header
Path('input.cdr').write_bytes(registry.encode(msg, little_endian=LITTLE_ENDIAN))
""".replace("LITTLE_ENDIAN", repr(little_endian))
    python = python.replace("ownership_base.", base_python + ".").replace(
        "ownership_custom.", custom_python + "."
    )
    subprocess.run(
        [sys.executable, "-c", bootstrap + python], env=env, cwd=tmp_path, check=True
    )
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    (consumer / "CMakeLists.txt").write_text("""cmake_minimum_required(VERSION 3.20)
project(ownership_consumer LANGUAGES CXX)
find_package(ownership_custom CONFIG REQUIRED)
add_executable(consumer main.cpp)
target_compile_features(consumer PRIVATE cxx_std_17)
target_link_libraries(consumer PRIVATE ownership_custom::messages)
""")
    (consumer / "main.cpp").write_text(
        """#include <std_msgs/msg/header.hpp>
#include <custom_msgs/msg/reading.hpp>
#include <dimos_cdrgen/cdr.hpp>
#include <fstream>
#include <iterator>
#include <type_traits>
static_assert(std::is_same_v<decltype(custom_msgs::msg::Reading{}.header), std_msgs::msg::Header>);
int main(int argc, char** argv) {
 if (argc != 3) return 2;
 std::ifstream in(argv[1], std::ios::binary);
 std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(in)), {});
 auto msg = dimos::cdr::cdr_decode<custom_msgs::msg::Reading>(bytes);
 std_msgs::msg::Header header = msg.header; msg.header = header;
 msg.value += 1;
 auto out = dimos::cdr::cdr_encode(msg, LITTLE_ENDIAN);
 std::ofstream file(argv[2], std::ios::binary);
 file.write(reinterpret_cast<const char*>(out.data()), out.size());
 return file ? 0 : 1;
}
""".replace("LITTLE_ENDIAN", str(little_endian).lower())
    )
    subprocess.run(
        [
            "cmake",
            "-S",
            str(consumer),
            "-B",
            str(consumer / "build"),
            f"-DCMAKE_TOOLCHAIN_FILE={toolchain}",
        ],
        check=True,
    )
    subprocess.run(["cmake", "--build", str(consumer / "build"), "-j", "2"], check=True)
    subprocess.run(
        [str(consumer / "build/consumer"), "input.cdr", "cpp.cdr"],
        cwd=tmp_path,
        check=True,
    )
    (custom / "rust/src/bin").mkdir()
    (custom / "rust/src/bin/check.rs").write_text(
        """use ownership_custom_messages::custom_msgs::msg::reading::Reading;
use ownership_base_messages::std_msgs::msg::header::Header;
fn main() {
 let paths: Vec<_> = std::env::args().skip(1).collect();
 assert_eq!(paths.len(), 2);
 let wire = std::fs::read(&paths[0]).unwrap();
 let mut msg: Reading = cdr::deserialize(&wire).unwrap();
 assert_eq!(msg.header.stamp.sec, 1700000000);
 assert_eq!(msg.header.stamp.nanosec, 123456789);
 assert_eq!(msg.covariance[35], 35.0);
 assert_eq!(msg.label, "相机/café");
 assert_eq!(msg.pixels, vec![0, 1, 127, 255]);
 assert_eq!(msg.image.encoding, "rgb8");
 assert_eq!(msg.image.data, vec![255, 0, 1]);
 assert_eq!(msg.cloud.fields[0].name, "x");
 assert_eq!(msg.cloud.data, vec![0, 0, 160, 63]);
 assert_eq!(msg.points, vec![1.25, -2.5]);
 assert!(msg.empty.is_empty());
 let header: Header = msg.header; msg.header = header;
 msg.value += 1.0;
 let wire = cdr::serialize::<_, _, cdr::WIRE_ENDIAN>(&msg, cdr::Infinite).unwrap();
 std::fs::write(&paths[1], wire).unwrap();
}
""".replace("WIRE_ENDIAN", "CdrLe" if little_endian else "CdrBe")
    )
    subprocess.run(
        [
            "cargo",
            "run",
            *(["--offline"] if os.environ.get("DIMOS_OFFLINE") == "1" else []),
            "--manifest-path",
            str(custom / "rust/Cargo.toml"),
            "--bin",
            "check",
            "--",
            "cpp.cdr",
            "rust.cdr",
        ],
        cwd=tmp_path,
        check=True,
    )
    # Exchange in the other order as well: Python -> Rust -> C++ -> Python.
    subprocess.run(
        [
            "cargo",
            "run",
            *(["--offline"] if os.environ.get("DIMOS_OFFLINE") == "1" else []),
            "--manifest-path",
            str(custom / "rust/Cargo.toml"),
            "--bin",
            "check",
            "--",
            "input.cdr",
            "rust-first.cdr",
        ],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        [str(consumer / "build/consumer"), "rust-first.cdr", "reverse.cdr"],
        cwd=tmp_path,
        check=True,
    )
    verify = (
        bootstrap
        + """
from ownership_base.std_msgs.msg import Header
from ownership_custom.custom_msgs.msg import Reading
from pathlib import Path
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
import sys
msg = registry.decode(Path(sys.argv[1]).read_bytes(), Reading)
assert type(msg.header) is Header
assert (msg.value, msg.header.frame_id, msg.header.stamp.sec, msg.header.stamp.nanosec) == (22.5, 'map', 1700000000, 123456789)
assert msg.covariance.tolist() == list(range(36))
assert msg.label == '相机/café'
assert msg.pixels.tolist() == [0, 1, 127, 255]
assert msg.image.encoding == 'rgb8' and msg.image.data.tolist() == [255, 0, 1]
assert msg.cloud.fields[0].name == 'x' and msg.cloud.data.tolist() == [0, 0, 160, 63]
assert msg.points.tolist() == [1.25, -2.5]
assert msg.empty.tolist() == []
reference = get_typestore(Stores.ROS2_JAZZY)
reference.register(get_types_from_msg(registry.schema(Reading.__msgtype__), Reading.__msgtype__))
assert reference.deserialize_cdr(registry.encode(msg), Reading.__msgtype__).value == 22.5
"""
    )
    verify = verify.replace("ownership_base.", base_python + ".").replace(
        "ownership_custom.", custom_python + "."
    )
    for result in ("rust.cdr", "reverse.cdr"):
        subprocess.run(
            [sys.executable, "-c", verify, result],
            cwd=tmp_path,
            env=env,
            check=True,
        )
    # Public source manifests are validated before classes are exposed.
    manifest_path = base / "message-package.json"
    installed_manifest = (
        base
        / "python"
        / (base_python.replace(".", "/") + "_schemas/package/message-package.json")
    )
    original = manifest_path.read_text()
    for key, value, error in (
        ("version", "99.0.0", "Dependency version mismatch"),
        ("schemas", {}, "Message schema digest mismatch"),
    ):
        changed = json.loads(original)
        changed[key] = value
        manifest_path.write_text(json.dumps(changed))
        installed_manifest.write_text(json.dumps(changed))
        try:
            result = subprocess.run(
                [sys.executable, "-c", bootstrap],
                env=env,
                cwd=tmp_path,
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode != 0
            assert error in result.stderr
        finally:
            manifest_path.write_text(original)
            installed_manifest.write_text(original)

    destination = os.environ.get("DIMOS_OWNERSHIP_EVIDENCE")
    if destination:
        evidence = (
            Path(destination)
            / ("nested" if nested else "flat")
            / ("le" if little_endian else "be")
        )
        evidence.mkdir(parents=True, exist_ok=True)
        for name in (
            "input.cdr",
            "cpp.cdr",
            "rust.cdr",
            "rust-first.cdr",
            "reverse.cdr",
        ):
            shutil.copy2(tmp_path / name, evidence / name)
        shutil.copytree(
            custom / "cpp/custom_msgs", evidence / "custom_msgs", dirs_exist_ok=True
        )
