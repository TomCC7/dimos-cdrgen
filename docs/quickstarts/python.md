# Generate and use a Python message

Create an `acme` message package with a sequence number and a floating-point value.
First [install the generator](../install.md) and keep its virtual environment active.
Run the following commands in a new directory outside the generator checkout.

## Define the message

```sh
mkdir -p interfaces/example_msgs/msg
cat > interfaces/example_msgs/msg/Reading.msg <<'EOF'
int32 sequence
float64 value
EOF
cat > pyproject.toml <<'EOF'
[project]
name = "acme"
version = "0.1.0"

[tool.dimos.messages]
source = "interfaces"
EOF
```

## Generate and install the Python project

```sh
dimos-cdrgen
python -m pip install build/message-source/python
```

Generation writes `build/message-source/message-package.json` and the
`python`, `cpp`, `rust`, and `schemas` directories. Installation makes
`acme.example_msgs.msg.Reading` available in the active environment.
The original `pyproject.toml` configures generation. The generated `python`
directory is the installable project for this walkthrough.

## Encode and decode a value

```sh
python - <<'PY'
from acme.example_msgs.msg import Reading
from dimos_cdrgen.registry import decode, encode

message = Reading(sequence=1, value=21.5)
wire = encode(message)
restored = decode(wire, Reading)
assert restored.sequence == 1
assert restored.value == 21.5
print(restored.value)
PY
```

The command prints `21.5`. `wire` includes a CDR encapsulation header.
The default encoding is little-endian. Numeric array fields use NumPy arrays.
Supply every field when constructing a message.

To use these sources in another language, continue with [C++](cpp.md) or
[Rust](rust.md) from the same project directory.

## Regenerate after a schema change

After editing a `.msg` file, run `dimos-cdrgen` again and reinstall
`build/message-source/python`. Restart Python processes that already imported
messages. The registry rejects changes after initialization.

Generation replaces stale language outputs after a successful run. Failed
generation preserves the previous output. Keep application code outside
`build/message-source` because regeneration replaces generated files.
