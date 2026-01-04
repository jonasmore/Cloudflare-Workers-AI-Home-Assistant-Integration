# GitHub Workflows Explained

This document explains the GitHub Actions workflows included in this project.

## Workflows Overview

The project includes three automated workflows that run on GitHub Actions:

### 1. `hassfest.yaml` - Home Assistant Validation

**Purpose**: Validates that the integration follows Home Assistant's standards and requirements.

**What it does**:
- Checks `manifest.json` for required fields and correct format
- Validates integration structure and file organization
- Ensures dependencies are properly declared
- Verifies version numbers and metadata

**When it runs**:
- On every push to the repository
- On every pull request
- Daily at midnight (scheduled)

**Why it's important**: Ensures the integration meets Home Assistant's quality standards and will work correctly when installed.

### 2. `validate.yaml` - HACS Validation

**Purpose**: Validates that the integration is compatible with HACS (Home Assistant Community Store).

**What it does**:
- Checks `hacs.json` configuration
- Validates repository structure for HACS
- Ensures all required files are present
- Verifies integration metadata

**When it runs**:
- On every push to the repository
- On every pull request
- Daily at midnight (scheduled)
- Manually via workflow_dispatch

**Why it's important**: Ensures users can install the integration via HACS, the most popular way to install custom integrations.

### 3. `release.yaml` - Automated Releases

**Purpose**: Automatically creates release archives when a new version is published.

**What it does**:
1. Extracts version number from the release tag
2. Updates `manifest.json` with the version number
3. Creates a ZIP archive of the integration
4. Uploads the archive as a release asset

**When it runs**:
- When a new GitHub release is published

**Why it's important**: Automates the release process and provides downloadable archives for manual installation.

## How to Use These Workflows

### For Contributors

When you submit a pull request:
1. The workflows will automatically run
2. Check the "Actions" tab to see if they pass
3. Fix any issues reported by the workflows
4. Your PR will be reviewed once all checks pass

### For Maintainers

**Creating a Release**:
1. Update version in `manifest.json` to the new version (e.g., `0.2.0`)
2. Update `CHANGELOG.md` with changes
3. Commit and push changes
4. Create a new release on GitHub:
   - Tag: `v0.2.0` (must start with `v`)
   - Title: `v0.2.0 - Release Name`
   - Description: Copy from `CHANGELOG.md`
5. Publish the release
6. The workflow will automatically create and upload the ZIP file

### Monitoring Workflows

**View workflow runs**:
1. Go to the "Actions" tab on GitHub
2. Click on a workflow to see its runs
3. Click on a specific run to see details
4. Review logs if there are failures

**Workflow badges**: The README includes badges that show the status of these workflows.

## Workflow Benefits

### Continuous Integration
- Catches issues early before they reach users
- Ensures code quality and standards compliance
- Provides confidence in changes

### Automated Quality Checks
- Validates integration structure
- Checks HACS compatibility
- Ensures proper versioning

### Streamlined Releases
- Automates repetitive tasks
- Reduces human error
- Provides consistent release artifacts

## Troubleshooting Workflows

### hassfest Failures

**Common issues**:
- Missing required fields in `manifest.json`
- Invalid version format
- Missing dependencies
- Incorrect file structure

**How to fix**:
1. Review the error message in the workflow log
2. Check Home Assistant's [integration documentation](https://developers.home-assistant.io/docs/creating_integration_manifest)
3. Fix the issue and push again

### HACS Validation Failures

**Common issues**:
- Missing or invalid `hacs.json`
- Incorrect repository structure
- Missing README or other required files

**How to fix**:
1. Review HACS [requirements](https://hacs.xyz/docs/publish/integration)
2. Ensure all required files are present
3. Validate `hacs.json` format

### Release Workflow Failures

**Common issues**:
- Tag doesn't start with `v`
- Version mismatch between tag and manifest
- ZIP creation errors

**How to fix**:
1. Ensure tag format is correct (`v0.1.0`)
2. Verify manifest.json has correct version
3. Check workflow logs for specific errors

## Adding New Workflows

To add a new workflow:

1. Create a new `.yaml` file in `.github/workflows/`
2. Define the workflow triggers and jobs
3. Test the workflow on a feature branch
4. Document it in this file

## Best Practices

1. **Always test locally first** before pushing
2. **Review workflow logs** when failures occur
3. **Keep workflows simple** and focused
4. **Document changes** to workflows
5. **Use workflow badges** in README for visibility

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [HACS Documentation](https://hacs.xyz/docs/publish/integration)

---

These workflows help maintain code quality and streamline the development process. 