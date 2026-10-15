# Maintain the documentation

Edit Markdown in `docs/` and keep every page in `mkdocs.yml` navigation.
The site uses Material for MkDocs with a small local stylesheet, system fonts,
and light and dark palettes. It needs no separate frontend build. The docs environment is separate from the generator's runtime dependencies.

## Build and preview locally

Use Python 3.12 for the locked docs environment. Run from the repository root:

```sh
python3.12 -m venv .venv-docs
.venv-docs/bin/python -m pip install --require-hashes -r requirements/docs.txt
.venv-docs/bin/python -m mkdocs build --strict
.venv-docs/bin/python -m mkdocs serve
```

Open the local URL printed by MkDocs. `build --strict` creates `site/` and fails
on missing navigation pages, omitted pages, broken local links, and invalid
heading anchors. The build does not validate remote URLs or execute code blocks.
Review the rendered pages at desktop and narrow widths before publication.

The dependency lock was resolved for CPython 3.12 on Linux, matching the workflow.
Keep `site/` and the virtual environment out of version control.
Building the site does not need parser preparation or package installation.

## Update the dependency lock

Edit `requirements/docs.in`, then regenerate the lock in a disposable Python 3.12
environment. `pip-tools` is a maintenance tool, not a site dependency.

```sh
.venv-docs/bin/python -m pip install 'pip-tools==7.5.1'
.venv-docs/bin/python -m piptools compile --generate-hashes --strip-extras \
	--index-url https://pypi.org/simple \
	--output-file requirements/docs.txt requirements/docs.in
.venv-docs/bin/python -m pip install --require-hashes -r requirements/docs.txt
.venv-docs/bin/python -m mkdocs build --strict
```

Review changed versions and hashes. Recreate the environment from the lock to
verify the install independently of maintenance tools.

## Publish through GitHub Pages

The repository workflow builds on pull requests and pushes to `main` that change
docs inputs. Pull requests receive a strict build without deployment permissions.
After a successful build on `main`, the deployment job uploads the generated
site to GitHub Pages. A manual workflow run also builds the site and deploys only
when the selected branch is `main`.

Before the first deployment, the repository owner must select **GitHub Actions**
as the publishing source under **Settings > Pages**. Keep the `github-pages`
environment restricted to the intended deployment branch. No custom domain is
required. Adding the workflow does not prove that Pages is enabled or deployed.

The build job has only `contents: read`. The deployment job has `pages: write`
and `id-token: write`. Action commits are pinned and the deployment job runs
only after the build succeeds. The workflow does not create a PyPI release.

The configured site URL is `https://tomcc7.github.io/dimos-cdrgen/`.
Treat it as the intended destination until a successful deployment and a live
page check confirm it. The deployed `revision.txt` records the source commit
so a page check can confirm the expected revision without polling CI.

These settings follow the [MkDocs validation documentation](https://www.mkdocs.org/user-guide/configuration/#validation)
and [GitHub's Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
