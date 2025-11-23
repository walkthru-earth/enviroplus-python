# Publishing enviroplus-community to PyPI

This guide explains how to publish `enviroplus-community` to PyPI using **Trusted Publishers** (the modern, recommended method).

## 📚 Official Documentation

- **PyPI Trusted Publishers**: https://docs.pypi.org/trusted-publishers/
- **Using a Publisher**: https://docs.pypi.org/trusted-publishers/using-a-publisher/
- **Adding to Existing Project**: https://docs.pypi.org/trusted-publishers/adding-a-publisher/
- **Python Packaging Guide**: https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/
- **PyPA GitHub Action**: https://github.com/pypa/gh-action-pypi-publish

## 🔐 What is Trusted Publishing?

Trusted Publishing uses **OpenID Connect (OIDC)** to securely publish packages to PyPI **without using API tokens or passwords**. It's:

- ✅ **More secure** - No long-lived tokens to leak
- ✅ **Easier** - No manual token management
- ✅ **Automatic attestations** - PEP 740 digital signatures generated automatically
- ✅ **Industry standard** - Over 25% of PyPI uploads use this method (as of Oct 2025)

---

## 🚀 One-Time Setup (Do This First!)

### Step 1: Create Account on PyPI

1. Go to https://pypi.org/ (for production)
2. Create an account or log in
3. **Enable 2FA** (required for publishing)

### Step 2: Create Account on TestPyPI (Optional but Recommended)

1. Go to https://test.pypi.org/ (for testing)
2. Create a separate account (TestPyPI is independent from PyPI)
3. **Enable 2FA**

> **Note**: TestPyPI and PyPI are separate. You need accounts on both.

### Step 3: Add Trusted Publisher on PyPI

#### For a New Package (First Time Publishing):

1. Go to https://pypi.org/manage/account/publishing/
2. Scroll to **"Add a new pending publisher"**
3. Fill in the form:
   - **PyPI Project Name**: `enviroplus-community`
   - **Owner**: `walkthru-earth` (your GitHub organization)
   - **Repository name**: `enviroplus-python`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
4. Click **"Add"**

#### For TestPyPI (Optional):

1. Go to https://test.pypi.org/manage/account/publishing/
2. Same process, but use environment name: `testpypi`

#### For an Existing Package:

1. Go to https://pypi.org/manage/project/enviroplus-community/settings/publishing/
2. Click **"Add a new publisher"**
3. Fill in the same details as above

### Step 4: Configure GitHub Environments

1. Go to your GitHub repository: https://github.com/walkthru-earth/enviroplus-python
2. Click **Settings** → **Environments**
3. Create two environments:

#### Environment: `pypi`
- **Name**: `pypi`
- **Protection rules** (recommended):
  - ✅ Required reviewers: Add yourself or team members
  - ✅ Wait timer: 0 minutes (or add delay for safety)
  - ✅ Deployment branches: Only `main` or tags matching `v*`

#### Environment: `testpypi`
- **Name**: `testpypi`
- **Protection rules**: (less strict, for testing)
  - Can leave open or add same rules

> **Why environments?** They provide extra security and allow you to control when/where publishing happens.

---

## 📦 Publishing Workflow

### Method 1: Automatic Publishing (Recommended)

**Publish to PyPI on Git Tag:**

```bash
# 1. Make sure everything is committed
git status

# 2. Update version in enviroplus/__init__.py
# Edit: __version__ = "1.0.3"

# 3. Commit the version bump
git add enviroplus/__init__.py
git commit -m "chore: bump version to 1.0.3"

# 4. Create and push a version tag
git tag v1.0.3
git push origin main
git push origin v1.0.3

# 5. GitHub Actions will automatically:
#    - Build the package
#    - Publish to PyPI
#    - Create a GitHub Release
```

**The workflow triggers on tags matching `v*` pattern.**

### Method 2: Manual Publishing

**Using GitHub UI:**

1. Go to **Actions** tab in GitHub
2. Click **"Publish to PyPI 📦"** workflow
3. Click **"Run workflow"** button
4. Choose:
   - **Branch**: `main`
   - **Target**: `testpypi` or `pypi`
5. Click **"Run workflow"**

### Method 3: Test on TestPyPI First

```bash
# 1. Manually trigger workflow for TestPyPI
# (Use GitHub UI, select "testpypi" target)

# 2. Verify it worked
uv pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    enviroplus-community

# 3. If good, publish to production PyPI
git tag v1.0.3
git push origin v1.0.3
```

---

## 🔍 Verification After Publishing

### 1. Check PyPI Page

Visit: https://pypi.org/project/enviroplus-community/

Verify:
- ✅ Version number is correct
- ✅ Description looks good
- ✅ Dependencies are listed
- ✅ Links work (GitHub, homepage, etc.)

### 2. Test Installation

```bash
# Create fresh environment
uv venv test-install
source test-install/bin/activate

# Install from PyPI
uv pip install enviroplus-community

# Verify commands work
enviroplus-examples
enviroplus-setup --check

# Try importing (should work with Python 3.9-3.13)
python -c "import enviroplus; print(enviroplus.__version__)"
```

### 3. Check GitHub Release

Visit: https://github.com/walkthru-earth/enviroplus-python/releases

Verify:
- ✅ Release was created automatically
- ✅ Distribution files are attached (.tar.gz and .whl)
- ✅ Release notes are generated

### 4. Verify Attestations (NEW in 2025!)

PyPI now generates **digital attestations** for all files published via Trusted Publishing.

View attestations:
1. Go to: https://pypi.org/project/enviroplus-community/#files
2. Click on a file (e.g., the .whl file)
3. Look for **"Attestations"** section
4. You should see provenance attestations with GitHub Actions workflow info

---

## 🛠️ Troubleshooting

### Error: "Publishing to a repository using a username and password is disabled"

**Solution**: You're trying to use old-style authentication. Make sure:
- You've configured Trusted Publishing on PyPI (see Step 3 above)
- Your workflow has `permissions: id-token: write`
- You're **not** using `password:` or `user:` in the workflow

### Error: "Trusted publishing exchange failure"

**Causes**:
1. **Environment name mismatch**: Workflow uses `environment: pypi` but you configured `testpypi` on PyPI
2. **Repository/workflow name wrong**: Double-check the exact names match
3. **Organization/owner wrong**: Make sure it's `walkthru-earth` not your personal account

**Solution**: Go to PyPI trusted publishers settings and verify all fields match exactly.

### Error: "Package already exists"

**For PyPI**: You can't overwrite existing versions. Bump the version number in `enviroplus/__init__.py`.

**For TestPyPI**: You can't re-upload either, but TestPyPI periodically cleans up old packages.

### Workflow doesn't trigger on tag

**Checklist**:
- ✅ Tag starts with `v` (e.g., `v1.0.3`, not `1.0.3`)
- ✅ Tag is pushed to remote: `git push origin v1.0.3`
- ✅ Check Actions tab for any errors

### GitHub Environment approval required

If you set up **required reviewers** on the `pypi` environment:
1. The workflow will pause and wait for approval
2. You'll get a notification
3. Go to Actions → The running workflow
4. Click **"Review deployments"**
5. Approve the deployment

This is a safety feature to prevent accidental publishes!

---

## 📋 Pre-Publish Checklist

Before creating a release tag:

- [ ] All tests pass (`make qa`, `make pytest`)
- [ ] Version bumped in `enviroplus/__init__.py`
- [ ] CHANGELOG.md updated with changes
- [ ] README.md is up to date
- [ ] All changes committed and pushed
- [ ] Tested locally: `hatch build` succeeds
- [ ] Trusted Publisher configured on PyPI
- [ ] GitHub environments (`pypi`, `testpypi`) created

---

## 🔄 Version Numbering

We use **Semantic Versioning** (semver):

- **Major** (1.x.x): Breaking changes
- **Minor** (x.1.x): New features, backwards compatible
- **Patch** (x.x.1): Bug fixes

Examples:
- `v1.0.0` → First stable release
- `v1.0.1` → Bug fix
- `v1.1.0` → New feature added
- `v2.0.0` → Breaking change (e.g., API change)

---

## 🎯 Best Practices

### 1. Always Test on TestPyPI First

For major releases, test the full flow:
```bash
# Manually trigger workflow → testpypi
# Then verify installation works
# Then tag for production PyPI
```

### 2. Use Semantic Versioning

Clear version numbers help users understand changes:
- Patch bumps: Bug fixes, safe to update
- Minor bumps: New features, safe to update
- Major bumps: Breaking changes, review before updating

### 3. Write Good Release Notes

The workflow auto-generates release notes from commits. Write clear commit messages:
- `feat: add new sensor calibration feature`
- `fix: resolve I2C timeout issue`
- `docs: update installation instructions`
- `chore: bump version to 1.0.3`

### 4. Monitor Downloads

Track adoption:
- PyPI Stats: https://pypistats.org/packages/enviroplus-community
- GitHub Insights: https://github.com/walkthru-earth/enviroplus-python/pulse

### 5. Keep Dependencies Updated

Regularly update dependencies to get security fixes:
```bash
uv pip list --outdated
```

---

## 📞 Support

### PyPI Issues:
- PyPI Help: https://pypi.org/help/
- PyPI GitHub: https://github.com/pypi/warehouse/issues

### GitHub Actions Issues:
- Action Repo: https://github.com/pypa/gh-action-pypi-publish/issues
- GitHub Actions Docs: https://docs.github.com/en/actions

### Package Issues:
- Open an issue: https://github.com/walkthru-earth/enviroplus-python/issues

---

## 📚 Further Reading

- **PEP 740** - Index support for digital attestations: https://peps.python.org/pep-0740/
- **PyPI Trusted Publishers Blog**: https://blog.pypi.org/posts/2025-11-10-trusted-publishers-coming-to-orgs/
- **Python Packaging Guide**: https://packaging.python.org/
- **Hatch Documentation**: https://hatch.pypa.io/

---

**Last Updated**: November 2025
**Maintained by**: walkthru.earth
**Package**: enviroplus-community
**Repository**: https://github.com/walkthru-earth/enviroplus-python
