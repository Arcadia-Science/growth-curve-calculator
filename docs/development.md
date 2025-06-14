## Development

### Environment setup

We use poetry for dependency management and build tooling. You can either install poetry globally or within a virtual environment in order to isolate poetry itself. We recommend the latter. First, create a new conda environment from the `dev.yml` environment file:

```bash
conda env create -n growth-curve-calculator-dev -f envs/dev.yml
conda activate growth-curve-calculator-dev
```

Next, install dependencies, including the development, documentation, and build dependencies:

```bash
poetry install --no-root --with dev,docs,build
```

If you have installed poetry globally, activate the poetry virtual environment:

```bash
poetry shell
```

Poetry detects and respects existing virtual environments, so if you are using poetry within a conda environment, this step is not needed.

Finally, install the package itself in editable mode:

```bash
pip install -e .
```

### Formatting and linting

If you have installed poetry globally, make sure to run `poetry shell` before running the commands below.

To format the code, use the following command:

```bash
make format
```

To run the lint checks and type checking, use the following command:

```bash
make lint
```

### Pre-commit hooks

We use pre-commit to run formatting and lint checks before each commit. To install the pre-commit hooks, use the following command:

```bash
pre-commit install
```

To run the pre-commit checks manually, use the following command:

```bash
make pre-commit
```

### Testing

We use `pytest` for testing. The tests are found in the `growth_curve_calculator/tests/` subpackage. To run the tests, use the following command:

```bash
make test
```

### Managing dependencies

We use poetry to manage dependencies. To add a new dependency, use the following command:

```bash
poetry add some-package
```

To add a new development dependency, use the following command:

```bash
poetry add -G dev some-dev-package
```

To update a dependency, use the following command:

```bash
poetry update some-package
```

Whenever you add or update a dependency, poetry will automatically update both `pyproject.toml` and the `poetry.lock` file. Make sure to commit the changes to these files to the repo.

### Documentation

We use Sphinx for documentation with the [`furo` theme](https://github.com/pradyunsg/furo). We also use some Sphinx extensions (described below) to make the process of writing documentation easier.

To build the docs, first install `pandoc`. On macOS, this can be done using `brew`:

```
brew install pandoc
```

Then, build the docs using the following command:

```bash
make docs
```

Note: the `pandoc` dependency is only required by the `nbsphinx` extension. If this extension is removed, there is no need to install `pandoc`.

#### sphinx-autoapi

This extension generates API docs automatically from the docstrings in the source code. To do so, it requires that docstrings adhere to the Google or Numpy style. This style is described in the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

#### napolean

Rather than writing our docstrings in RST, we use this extension to convert Google and NumPy-style docstrings to RST at build time.

#### myst-parser

RST is complicated to write. This extension lets us write our docs in Markdown and then converts them to RST at build time.

#### nbsphinx

It is often convenient to write examples as Jupyter notebooks. This extension executes Jupyter notebooks and renders the results in the docs at build time. It requires `pandoc`, which can be installed using `brew install pandoc`.

#### Removing unused Sphinx extensions

To remove an unused extension, delete the corresponding line from the `extensions` list in `docs/conf.py` and delete the extension from the `[tool.poetry.group.docs.dependencies]` section in `pyproject.toml`.

## Publishing the package on PyPI

Publishing the package on PyPI requires that you have API tokens for the test and production PyPI servers. You can find these tokens in your PyPI account settings. Create a `.env` file by coping `.env.copy` and add your tokens to this file.

We use git tags to define package versions. When you're ready to release a new version of the package, first create a new git tag. The name of the tag should correspond to the new version number, prepended with a "v". In the example below, the new version number is `0.1.0`, so the git tag is `v0.1.0`. We use semantic versioning of the form `MAJOR.MINOR.PATCH`. See [semver.org](https://semver.org/) for more information.

```bash
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

__Before creating the tag, make sure that your local git repository is on `main`, is up-to-date, and does not contain uncommitted changes!__

If you need to delete a tag you've created, use the following command:

```bash
git tag -d <tagname>
```

If you already pushed the deleted tag to GitHub, you will also need to delete the tag from the remote repository:

```bash
git push origin :refs/tags/<tagname>
```

Once you've created the correct new tag, build the package:
```bash
make build
```

You should see an output that looks like this:
```
Building growth-curve-calculator (0.1.0)
  - Building sdist
  - Built growth-curve-calculator-0.1.0.tar.gz
  - Building wheel
```

The build artifacts are written to the `dist/` directory.

__Make sure that the version number in the output from `make build` matches the one from the git tag that you just created!__

If it does not, first double-check that you created the git tag correctly. If the tag looks correct, there are two specific scenarios to check for:

- If the version number is `0.0.0`, this indicates that Poetry cannot infer the correct version number. Check that you are in the correct conda environment and that you have installed the dev dependencies using `poetry install --no-root --with=dev`.

- If there is additional metadata attached to the version number (_e.g._ `0.1.0.dev1+eb17e9c.dirty`), this means that your local repo is on a commit without a tag and/or that there are uncommitted changes in your local repo. Make sure that you are on the correct commit and commit or stash any uncommitted changes, then try the build command again.

Next, check that you can publish the package to the PyPI test server:

```bash
make build-and-test-publish
```

The `build-and-test-publish` command calls `poetry build` to build the package and then `poetry publish` to upload the build artifacts to the test server.

Check that you can install the new version of the package from the test server:

```bash
pip install --index-url https://test.pypi.org/simple/ growth-curve-calculator==0.1.0
```

If everything looks good, build and publish the package to the prod PyPI server:

```bash
make build-and-publish
```

Finally, check that you can install the new version of the package from the prod PyPI server:

```bash
pip install growth-curve-calculator==0.1.0
```
