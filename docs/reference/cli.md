# CLI reference

## Project command

The installed entry point is `dimos_cdrgen.source_package:main`.

```text
dimos-cdrgen [-h] [project]
```

| Argument | Meaning |
| --- | --- |
| `project` | Project directory. Defaults to the current directory. |
| `-h`, `--help` | Print help and exit. |

The command reads `pyproject.toml`, selects the declared roots and dependencies,
and generates all three languages under `build/message-source`. A successful run
has no required stdout message. Errors terminate the command with a nonzero status.
The command has no `init`, `compile`, `install`, or `publish` subcommand.

## Lower-level generation module

The package also exposes a module command:

```text
python -m dimos_cdrgen.generate --output PATH [options]
```

| Option | Default | Meaning |
| --- | --- | --- |
| `--output PATH` | Required. | Artifact root. |
| `--package-root PATH` | None. | Local schema root. Repeatable. |
| `--type NAME` | All available types. | Root `package/msg/Type`. Repeatable. |
| `--python-module NAME` | `dimos_generated` | Generated module name. |
| `--version VERSION` | `0.1.0` | Package version. |
| `--package` | False. | Explicitly calls the Python distribution writer after generation. Normal all-language generation already writes a Python project. |
| `-h`, `--help` | | Print help and exit. |

This command enables installed schema discovery. It has no option to pass
dependency ownership contracts or select languages. Use the project command or
[Python API](api.md) when ownership reuse matters.

## Parser preparation

Parser preparation runs from the generator checkout before building the tool:

```text
python dimos_cdrgen/prepare_parser.py [-h] [--cache PATH] [--output PATH]
                                     [--archive PATH] [--offline]
```

`--cache` selects the parser source cache, `--output` selects the preparation
directory, `--archive` supplies a pinned source archive, and `--offline` forbids
downloads. The default output is `dimos_cdrgen/.upstream` beside the script.
The source lock and hashes remain authoritative for cached and supplied archives.
