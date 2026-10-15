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
re_cdr = "=0.1.0"
```

Create `src/main.rs`:

```rust
use acme_messages::example_msgs::msg::reading::Reading;

fn main() {
	let message = Reading { sequence: 1, value: 21.5 };
	let body = re_cdr::to_vec::<_, re_cdr::LittleEndian>(&message).unwrap();
	let mut wire = vec![0, 1, 0, 0];
	wire.extend(body);
	let (restored, used) =
		re_cdr::from_bytes::<Reading, re_cdr::LittleEndian>(&wire[4..]).unwrap();
	assert_eq!(restored.sequence, 1);
	assert_eq!(restored.value, 21.5);
	assert_eq!(used, wire.len() - 4);
}
```

## Compile and run

```sh
cargo run
```

The executable exits successfully when its assertions pass. Cargo invokes
`ros2msg` through the generated `build.rs` and compiles declarations in Cargo's
`OUT_DIR`. It does not create a Python extension or publish a crate.

`re_cdr` encodes the CDR body. The four bytes added above are the plain
little-endian CDR encapsulation header used by this example. The decoder receives
the body after that header.

For a machine with cached dependencies, use `cargo run --offline`.
Commit your application's `Cargo.lock` to preserve its resolved dependencies.
If the message package reuses other packages, follow the
[Rust dependency instructions](../guides/dependencies.md#rust-dependency-resolution).
