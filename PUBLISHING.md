# Publishing to PyPI

This project uses GitHub Actions to automatically build and publish to PyPI when you create a version tag.

## Setup

### 1. Create a PyPI API Token

1. Go to [PyPI](https://pypi.org) and log in to your account
2. Navigate to Account Settings → API tokens
3. Click "Add API token"
4. Name it something like "temporal-worker-sdk-ci"
5. Scope: "Entire account"
6. Copy the token (starts with `pypi-`)

### 2. Add the Secret to GitHub

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `PYPI_API_TOKEN`
5. Value: Paste the token from step 1
6. Click "Add secret"

## Publishing a Release

### 1. Update the Version

Update the version in `pyproject.toml`:

```toml
[project]
version = "0.2.0"
```

Also update `sdk/__init__.py`:

```python
__version__ = "0.2.0"
```

### 2. Commit and Tag

```bash
git add pyproject.toml sdk/__init__.py
git commit -m "Bump version to 0.2.0"
git tag v0.2.0
git push origin main
git push origin v0.2.0
```

### 3. GitHub Actions Builds and Publishes

The workflow will:
1. Trigger on the `v0.2.0` tag
2. Build the distribution (wheel + source)
3. Verify the distribution with `twine check`
4. Upload to PyPI using the `PYPI_API_TOKEN` secret

Check the Actions tab to see the build progress.

### 4. Verify on PyPI

Once published, verify at: https://pypi.org/project/temporal-worker-sdk/

## Troubleshooting

### "Invalid distribution" error

Run locally to debug:

```bash
python -m build
twine check dist/*
```

### "Invalid credentials" error

Verify the `PYPI_API_TOKEN` secret is set correctly in GitHub Settings.

### "Version already exists" error

PyPI doesn't allow re-uploading the same version. Increment the version and try again.

## Local Testing

To test the build locally:

```bash
pip install build twine
python -m build
twine check dist/*
```

To test upload to TestPyPI:

```bash
twine upload --repository testpypi dist/*
```

(Requires a TestPyPI account and token)
