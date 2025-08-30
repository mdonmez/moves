# GitHub Actions Workflows

This repository contains three GitHub Actions workflows:

## 1. CI Workflow (`ci.yml`)

**Triggers:**

- Pull requests to `main` or `master` branches
- Pushes to `main` or `master` branches

**What it does:**

- Tests building and installation on Ubuntu, Windows, and macOS
- Uses `uv` for dependency management and building
- Installs the built wheel using `uv tool install`
- Runs `moves --version` to verify the installation works
- Validates that the version output matches the expected version

## 2. Build and Release Workflow (`build-and-release.yml`)

**Triggers:**

- Pushes to `main` or `master` branches
- Pull requests to `main` or `master` branches
- Manual release creation

**What it does:**

- Builds and tests on all three platforms (Ubuntu, Windows, macOS)
- Creates a GitHub release automatically when code is pushed to main/master
- Uploads the wheel file and source distribution to GitHub Releases
- Only creates a release if the version tag doesn't already exist
- Provides installation instructions in the release notes

## 3. Manual Release Workflow (`manual-release.yml`)

**Triggers:**

- Manual workflow dispatch (can be triggered from GitHub's Actions tab)

**What it does:**

- Allows you to create a release manually
- Option to specify a custom version or use the one from `pyproject.toml`
- Option to mark the release as a prerelease
- Same build and test process as the automatic workflow

## Usage

### Automatic Release

1. Update the version in `pyproject.toml`
2. Push to `main` or `master` branch
3. The workflow will automatically create a release

### Manual Release

1. Go to the "Actions" tab in your GitHub repository
2. Select "Manual Release" workflow
3. Click "Run workflow"
4. Optionally specify a custom version or mark as prerelease
5. The workflow will build, test, and create the release

## Installation from Release

Users can install your package directly from GitHub releases:

```bash
# Install the latest release
uv tool install https://github.com/mdonmez/moves/releases/latest/download/moves-{version}-py3-none-any.whl

# Install a specific version
uv tool install https://github.com/mdonmez/moves/releases/download/v0.2.0/moves-0.2.0-py3-none-any.whl
```

## Requirements

These workflows expect:

- Python 3.13 (as specified in your `pyproject.toml`)
- A `pyproject.toml` file with version information
- The main entry point to be accessible via the `moves` command
- The `moves --version` command to work and display version information
