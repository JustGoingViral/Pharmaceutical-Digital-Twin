# Release Instructions for v0.1.0

## Overview
This document provides instructions for completing the GitHub release process for version 0.1.0 of the Pharmaceutical Digital Twin Factory.

## Automated Preparation Completed ✅

The following steps have been completed automatically:

1. ✅ **CHANGELOG.md created** - Complete release notes and changelog
2. ✅ **VERSION file created** - Version tracking file with 0.1.0
3. ✅ **Git tag created locally** - Tag `v0.1.0` created with detailed message
4. ✅ **Release notes prepared** - Comprehensive release notes in RELEASE_NOTES_v0.1.0.md
5. ✅ **Changes committed** - All files committed to branch

## Manual Steps Required

Due to repository permissions, the following steps need to be completed manually by a repository administrator:

### Step 1: Push the Git Tag

The git tag `v0.1.0` has been created locally and needs to be pushed to the remote repository:

```bash
git push origin v0.1.0
```

Or if you prefer to push all tags:

```bash
git push origin --tags
```

### Step 2: Create GitHub Release

Once the tag is pushed, create a GitHub release:

#### Option A: Using GitHub Web Interface

1. Go to: https://github.com/JustGoingViral/Pharmaceutical-Digital-Twin/releases/new
2. Select tag: `v0.1.0`
3. Release title: `v0.1.0 - Initial Release`
4. Copy the contents of `RELEASE_NOTES_v0.1.0.md` into the release description
5. Check "Set as a pre-release" (since this is alpha)
6. Click "Publish release"

#### Option B: Using GitHub CLI

```bash
gh release create v0.1.0 \
  --title "v0.1.0 - Initial Release" \
  --notes-file RELEASE_NOTES_v0.1.0.md \
  --prerelease
```

#### Option C: Using GitHub API

```bash
# Set your GitHub token
export GITHUB_TOKEN="your_token_here"

# Create the release
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/JustGoingViral/Pharmaceutical-Digital-Twin/releases \
  -d '{
    "tag_name": "v0.1.0",
    "name": "v0.1.0 - Initial Release",
    "body": "See RELEASE_NOTES_v0.1.0.md for complete release notes",
    "draft": false,
    "prerelease": true
  }'
```

### Step 3: Verify Release

After creating the release, verify:

1. ✅ Tag is visible at: https://github.com/JustGoingViral/Pharmaceutical-Digital-Twin/tags
2. ✅ Release is visible at: https://github.com/JustGoingViral/Pharmaceutical-Digital-Twin/releases
3. ✅ Release notes are properly formatted
4. ✅ Release is marked as pre-release (alpha)

### Step 4: Optional - Update Documentation

Consider updating:
- Repository README.md badges to show latest release
- Project website with release announcement
- Social media announcement

## Release Assets (Optional)

You may want to include these assets with the release:

- Source code (automatically included by GitHub)
- Compiled documentation
- Docker images
- Example configurations

## Post-Release Checklist

- [ ] Tag pushed to GitHub
- [ ] GitHub release created
- [ ] Release marked as pre-release
- [ ] Release notes verified
- [ ] Team notified
- [ ] Users notified (if applicable)
- [ ] Documentation updated

## Notes

- This is an **alpha release** (version 0.1.0)
- Should be marked as "pre-release" in GitHub
- Future releases should follow semantic versioning
- Update CHANGELOG.md for future releases

## Troubleshooting

### If tag push fails
```bash
# Verify tag exists locally
git tag -l

# Verify remote connection
git remote -v

# Try pushing with verbose output
git push origin v0.1.0 -v
```

### If you need to recreate the tag
```bash
# Delete local tag
git tag -d v0.1.0

# Recreate tag
git tag -a v0.1.0 -m "Release v0.1.0"

# Push tag
git push origin v0.1.0
```

## Contact

For questions or issues with the release process, contact:
- Email: admin@justgoingviral.com
- Repository Issues: https://github.com/JustGoingViral/Pharmaceutical-Digital-Twin/issues

---

**Version**: 0.1.0  
**Date**: December 7, 2025  
**Status**: Ready for manual completion
