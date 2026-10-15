# Message inputs

The project CLI reads `[project]` and `[tool.dimos.messages]` from
`pyproject.toml`. Paths resolve relative to the project and must stay inside it.
The project name and version identify the generated package.

## Configuration fields

| Field | Default | Meaning |
| --- | --- | --- |
| `source` | `"interfaces"` | Existing directory containing `package/msg/Type.msg` files. |
| `module` | Project name with `-` replaced by `_`. | Generated Python module and native package identifier. |
| `roots` | All `.msg` types in `source`. | Explicit root type names such as `example_msgs/msg/Reading`. Dependencies are resolved recursively. |
| `catalog` | None. | JSON file selecting root types with a nonempty reason for each. Mutually exclusive with `roots`. |
| `resources` | `[]` | Existing files copied into the packaged schema provider. Basenames must be unique. |
| `dependencies` | `{}` | Installed message modules mapped to exact package versions. |

Unknown fields fail configuration. `source` must exist and select at least one
root. The module must match `[a-z][a-z0-9_]*` and must not be a Python keyword.
The version must have the form `major.minor.patch` with numeric components.

A catalog has this format:

```json
{
	"format": 1,
	"roots": {
		"example_msgs/msg/Reading": "Public sensor reading"
	}
}
```

## Schema resolution

Input files follow ROS 2 `.msg` syntax and reside under `package/msg`.
The parser preserves constants, defaults, bounds, and the original schema text.
Preservation does not imply codec support for every declaration.
The [compatibility reference](compatibility.md) lists the unsupported semantics.

Definitions resolve from the local source and declared dependencies. Missing
types and recursive message definitions fail resolution. Conflicting definitions
report their sources. Standard ROS types require explicit inputs or a dependency.
ROS 1 shorthand `time` and `duration` are rejected in favor of
`builtin_interfaces/Time` and `builtin_interfaces/Duration`.

The project CLI does not download schemas or infer dependency versions.
The lower-level generation API accepts multiple source roots and optional
installed schema discovery, as described in the [API reference](api.md).
