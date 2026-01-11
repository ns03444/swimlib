# GitHub Pages Deployment Checklist

Quick checklist for deploying to GitHub Pages.

## Pre-Deployment

- [ ] GitHub Actions workflow created (`.github/workflows/docs.yml`) ✅
- [ ] Update `docs/conf.py` with your GitHub username:
  - [ ] Line 103: `source_repository` URL
  - [ ] Line 111: Footer GitHub icon URL
  - [ ] Line 213: `extlinks` URLs (optional)

## Git Setup

- [ ] Remove GitLab remote: `git remote remove origin`
- [ ] Add GitHub remote: `git remote add origin git@github.com:YOURUSERNAME/swimlib.git`
- [ ] Verify remote: `git remote -v`

## GitHub Repository Setup

- [ ] Push code to GitHub: `git push -u origin master`
- [ ] Go to repository Settings → Pages
- [ ] Set Source to "GitHub Actions"
- [ ] Wait for workflow to complete (Actions tab)
- [ ] Verify deployment at: `https://YOURUSERNAME.github.io/swimlib/`

## Post-Deployment

- [ ] Update README.md with documentation URL
- [ ] Add documentation badge (optional):
  ```markdown
  ![Docs](https://github.com/YOURUSERNAME/swimlib/actions/workflows/docs.yml/badge.svg)
  ```
- [ ] Test all documentation links
- [ ] Set up custom domain (optional)

## Quick Commands

```bash
# Test build locally
poetry run sphinx-build -b html docs public

# Serve locally
cd public && python -m http.server 8000

# Force rebuild and push
git add . && git commit -m "Update docs" && git push
```

## Troubleshooting

**Workflow not running?**
- Check Settings → Actions → General → Actions permissions

**Build fails?**
- Check Actions tab for detailed logs
- Verify `poetry.lock` is committed

**404 errors?**
- Ensure Pages source is "GitHub Actions" not "Deploy from branch"
- Check that workflow completed successfully

**Permission errors?**
- Go to Settings → Actions → General → Workflow permissions
- Select "Read and write permissions"
