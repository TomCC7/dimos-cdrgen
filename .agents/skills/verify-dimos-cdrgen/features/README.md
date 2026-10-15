# dimos-cdrgen verification map

Run the parent skill's launch and doctor steps first. Each recipe uses the
current checkout and its existing tests. Evidence goes into `$RUN_DIR/evidence`;
only `$RUN_DIR/scratch` is disposable. Read each feature's prerequisites before
running it. A skipped test never proves its entry point.

- [Generation and recovery](generation.md): fast configuration, CLI rename, and rollback.
- [Installed Python packages](installation.md): full isolated source, wheel, sdist, editable, and dependency identity.
- [Native consumers and CDR](native.md): full CMake/Cargo consumers and three-language exchange.

The map covers library users, not ROS nodes or robot operations. Test node IDs
are part of the recipe: update them when tests move, and verify collection.
