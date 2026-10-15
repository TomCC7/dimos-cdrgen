# Build a C++ message consumer

Build an executable that encodes and decodes the `Reading` message from the
[Python quickstart](python.md). Run these commands in that message project's
directory, with the generator environment active.

## Prepare the native libraries

Provide CMake 3.20 or newer and a C++17 compiler with C compiler support.
On macOS, Apple's SDK and command-line tools are also required.
Install the native Python dependencies using the wheel built in the
[installation guide](../install.md). Replace the wheel path below with its
absolute path.

```sh
python -m pip install '/path/to/dimos_cdrgen-0.1.0-py3-none-any.whl[native]'
python - <<'PY'
from pathlib import Path
from dimos_cdrgen.native_build import prepare_cpp, write_cmake_toolchain

prefix = prepare_cpp(Path("build/message-source"))
write_cmake_toolchain(prefix, Path("build/acme-toolchain.cmake"))
print(prefix)
PY
```

This step fetches and verifies pinned upstream sources, compiles the libraries,
and prints the installation prefix. It does not install a system toolchain.
To reuse verified sources and completed builds offline, pass `offline=True`
and a populated `cache=Path(...)` to `prepare_cpp()`.

## Create the executable

Create `CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.20)
project(reader LANGUAGES CXX)
find_package(acme CONFIG REQUIRED)
add_executable(reader main.cpp)
target_compile_features(reader PRIVATE cxx_std_17)
target_link_libraries(reader PRIVATE acme::messages)
```

Create `main.cpp`:

```cpp
#include <example_msgs/msg/reading.hpp>
#include <dimos_cdrgen/cdr.hpp>

int main() {
	example_msgs::msg::Reading message;
	message.sequence = 1;
	message.value = 21.5;
	auto wire = dimos::cdr::cdr_encode(message);
	auto restored = dimos::cdr::cdr_decode<example_msgs::msg::Reading>(wire);
	return restored.sequence == 1 && restored.value == 21.5 ? 0 : 1;
}
```

## Compile and run

```sh
cmake -S . -B build/app -DCMAKE_TOOLCHAIN_FILE="$PWD/build/acme-toolchain.cmake"
cmake --build build/app
./build/app/reader
```

The executable exits with status `0` when the round trip succeeds.
The exported toolchain supplies the package prefixes and saved target settings.
The CDR header comes from this library and needs no DimOS SDK include path.
