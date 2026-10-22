# Validate and publish a Python release

Use this guide to validate `dimos-cdrgen` distributions and prepare an approved
upload through `.github/workflows/publish.yml` in `TomCC7/dimos-cdrgen`.
The current `0.1.0` version is a development candidate. This guide does not
establish registry ownership, name availability, or an existing release.

## Validate locally without uploading

Use Python 3.12 on Linux. Run from the repository root in a fresh checkout.
These commands prepare dependencies from PyPI and the pinned upstream parser,
then validate the built artifacts without network access.

```sh
python3.12 -m venv build/publish-venv
build/publish-venv/bin/python -m pip install --require-hashes -r requirements/publish.txt
build/publish-venv/bin/python -m pip wheel --require-hashes --no-build-isolation \
	--wheel-dir build/publish-wheelhouse -r requirements/publish.txt
build/publish-venv/bin/python dimos_cdrgen/prepare_parser.py
build/publish-venv/bin/python -m build --no-isolation
build/publish-venv/bin/python .github/scripts/validate_distributions.py \
	--wheelhouse build/publish-wheelhouse
sha256sum dist/*
```

If `dist/` contains old artifacts, choose a new output directory with
`python -m build --no-isolation --outdir PATH` and pass that path as
`--dist-dir PATH` to the validator. The validator requires exactly one wheel
and one source archive.

For offline parser preparation, supply `--offline --cache PATH` or
`--archive PATH` to `prepare_parser.py`. Populate the dependency wheelhouse
before disconnecting. Archive and parser hashes must match `parser-source.json`.
Keep the upstream license, project `LICENSE`, and `NOTICE` in both distributions.

The validator runs strict Twine metadata checks and rebuilds the tool's source
archive with `PIP_NO_INDEX=1`, using its packaged parser. It checks the rebuilt
wheel too. For each wheel, it creates a fresh virtual environment outside the
checkout, installs offline, generates a message package through `dimos-cdrgen`,
and checks a literal CDR byte sequence and decoded values. It also checks that
the consumer has no `dimos` or `rclpy` package.

These checks cover standalone Python generation on Linux with Python 3.12.
Run the [repository verification recipes](https://github.com/TomCC7/dimos-cdrgen/blob/main/.agents/skills/verify-dimos-cdrgen/SKILL.md)
for any affected native consumers or dependency ownership behavior. Missing
native archives or toolchains block those checks. A distribution dry-run does
not establish C++ or Rust compilation, macOS support, or other Python versions.

## Run the GitHub dry-run

After the workflow reaches the repository's default branch, open
**Actions > Publish distributions > Run workflow**. Select the branch or tag
to validate and leave **destination** set to `dry-run`.

The build job runs the same distribution validator and retains the wheel and
source archive as the `distributions` artifact for 14 days. Its summary records
the destination and SHA256 hashes. Both publisher jobs are skipped. This mode
has no OIDC permission and cannot upload a package.

A local dry-run proves local commands. A successful GitHub dry-run also proves
the hosted workflow's build and artifact upload. Neither proves registry
authentication or upload. Confirm a release only after the chosen publisher
job succeeds and the registry lists the expected files and hashes.

## Configure the approved registry owner

Complete this setup only after the owner approves the account, package name,
destination, and first release. PyPI and TestPyPI use independent accounts,
projects, and publisher registrations. The GitHub owner `TomCC7` does not prove
ownership of a PyPI account or of the `dimos-cdrgen` project.

1. Sign in to the approved account on the chosen registry and complete its
   account verification and two-factor authentication requirements.
2. If you own an existing `dimos-cdrgen` project, open that project's
   **Manage > Publishing** page and add a GitHub Trusted Publisher.
3. If the project does not exist, open the account's publishing page and add a
   pending GitHub publisher for project name `dimos-cdrgen`. A pending publisher
   creates the project on its first successful upload. It does not reserve the
   name. If someone else owns the name, resolve ownership or choose an approved
   new package name before continuing.
4. Enter repository owner `TomCC7`, repository name `dimos-cdrgen`, and workflow
   filename `publish.yml`. Enter environment `pypi` on PyPI, or `testpypi` on
   TestPyPI. The filename field takes `publish.yml`, without the directory path.
5. In the GitHub repository's **Settings > Environments**, create the matching
   environment. Require a trusted reviewer and prevent self-review where the
   repository plan supports it. Restrict deployment branches and tags to
   **Selected branches and tags**, with a tag rule `v*` and no branch rule.
   Use an exact approved tag rule for tighter control. Keep production uploads
   blocked if the required review protection is unavailable.
6. Repeat the setup separately for the other registry if it is also approved.
   Verify that each publisher registration names its matching environment.

The account publishing pages are [PyPI](https://pypi.org/manage/account/publishing/)
and [TestPyPI](https://test.pypi.org/manage/account/publishing/). Follow the
official [existing-project instructions](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)
or [pending-publisher instructions](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
for the selected registry. Configure trust in the registry UI. Do not paste
passwords, recovery codes, API tokens, or OIDC tokens into chat, workflow inputs,
repository files, or GitHub secrets for this workflow. It uses short-lived OIDC
credentials and has no API-token fallback.

## Upload an approved tag

1. Review the package version in `pyproject.toml`, the distribution hashes,
   supported targets, and remaining verification blockers. Approve that exact
   version and destination before creating or pushing its tag.
2. Create the release tag `v<package-version>` on the reviewed commit and push
   it. For the current metadata, the matching tag is `v0.1.2`. A tag push alone
   does not run this workflow or upload a package.
3. Open **Run workflow**, select that tag as the workflow ref, and choose
   `testpypi` for an approved TestPyPI upload or `pypi` for an approved PyPI upload.
   Each run uploads to exactly one registry. A TestPyPI success does not upload
   or promote anything to PyPI.
4. Review the completed build and hashes before approving the environment job.
   The build rejects branch refs and tags that differ from the package version.
5. After the upload succeeds, inspect the selected registry's version page.
   Compare both filenames and SHA256 hashes with the run summary. Record the
   workflow run and registry version URL as publication evidence.

The publisher jobs download only this run's validated distributions. They have
`id-token: write` and no checkout or build step. The build job has only
`contents: read`. All actions use pinned official commits. The workflow creates
no GitHub release and grants no permission to write repository contents.
This separation follows the [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/).

Registry uploads are permanent release actions. If a version or filename
already exists, stop and inspect it. Do not enable `skip-existing` to conceal
an incomplete or conflicting upload. Choose a new approved version when a
replacement is needed. Keep registry setup and upload blocked until the account
and project ownership and Trusted Publisher configuration have been approved.

Publishing this Python tool does not publish a standard-message catalog,
generated message packages, C++ prefixes, or Cargo crates.

## Update build dependencies

Edit `requirements/publish.in`, then regenerate its lock with Python 3.12 and
`pip-tools==7.5.1` in a disposable maintenance environment:

```sh
python -m piptools compile --generate-hashes --strip-extras --allow-unsafe \
	--index-url https://pypi.org/simple \
	--output-file requirements/publish.txt requirements/publish.in
```

Review the versions and hashes, recreate the publish environment from the lock,
and rerun distribution validation. The lock includes runtime dependencies only
to populate isolated consumer environments. `pyproject.toml` owns the package's
runtime requirements.
