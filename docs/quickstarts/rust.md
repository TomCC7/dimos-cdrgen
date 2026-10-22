# Build a Rust message consumer

Build a Cargo application that encodes and decodes the `Reading` message from
the [Python quickstart](python.md). Run these commands in the same message project.
Provide Rust and Cargo with support for edition 2024, which requires
[Rust 1.85 or newer](https://doc.rust-lang.org/edition-guide/rust-2024/index.html).
Cargo must be able to resolve the generated crate's dependencies.

## Create the application

Create `Cargo.toml` next to `pyproject.toml`:

```toml
[package]
name = "reading-demo"
version = "0.1.0"
edition = "2024"

[workspace]
exclude = ["build/message-source/rust"]

[dependencies]
acme-messages = { path = "build/message-source/rust" }
# Pin the upstream string-allocation fix until it is released.
cdr = { version = "=0.2.4", git = "https://github.com/TomCC7/cdr-rs", rev = "38a4368255d408faf374726653b39d4a4e9735cb" }
```

Create `src/main.rs`:

```rust
use acme_messages::example_msgs::msg::reading::Reading;

fn main() {
	let message = Reading { sequence: 1, value: 21.5 };
	let wire = cdr::serialize::<_, _, cdr::CdrLe>(&message, cdr::Infinite).unwrap();
	let restored: Reading = cdr::deserialize(&wire).unwrap();
	assert_eq!(restored.sequence, 1);
	assert_eq!(restored.value, 21.5);
}
```

## Compile and run

```sh
cargo run
```

The executable exits successfully when its assertions pass. Cargo invokes
`ros2msg` through the generated `build.rs` and compiles declarations in Cargo's
`OUT_DIR`. It does not create a Python extension or publish a crate.

`cdr` encodes and decodes the complete CDR message, including its encapsulation
header. `CdrLe` selects little-endian CDR; use `CdrBe` for big-endian output.

For a machine with cached dependencies, use `cargo run --offline`.
Commit your application's `Cargo.lock` to preserve its resolved dependencies.
If the message package reuses other packages, follow the
[Rust dependency instructions](../guides/dependencies.md#rust-dependency-resolution).
