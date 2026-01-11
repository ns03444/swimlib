# GitLab Pages Documentation Deployment

This project uses GitLab CI/CD to automatically build and deploy Sphinx documentation to GitLab Pages.

## How It Works

When you push commits to the default branch (main/master), GitLab CI/CD will automatically:

1. Install Poetry and project dependencies (including Sphinx)
2. Build the HTML documentation from the `docs/` directory
3. Deploy the generated site to GitLab Pages

## Accessing Your Documentation

Once deployed, your documentation will be available at:

```
https://<your-username>.gitlab.io/swimlib
```

Replace `<your-username>` with your GitLab username or group name.

## Pipeline Configuration

The `.gitlab-ci.yml` file contains:

- **Image**: `python:3.13-slim` - Matches your project's Python version
- **Cache**: Poetry dependencies are cached for faster builds
- **Pages Job**: Builds docs to the `public/` directory (required by GitLab Pages)
- **Deploy Rule**: Only deploys from the default branch

## Local Testing

To test the build locally before pushing:

```bash
# Build documentation to public/ directory (same as CI)
poetry run sphinx-build -b html docs public

# View the result
python -m http.server -d public 8000
# Then open http://localhost:8000 in your browser
```

## Build Status

Check the pipeline status in your GitLab project:

1. Go to **CI/CD → Pipelines** to see build history
2. Click on a pipeline to view detailed logs
3. Go to **Settings → Pages** to see deployment status and URL

## Troubleshooting

### Pipeline Fails on Build

Check the pipeline logs for errors. Common issues:

- Missing dependencies in `pyproject.toml` (ensure `docs` extras are installed)
- Sphinx warnings treated as errors (check `docs/conf.py`)
- Invalid RST syntax in documentation files

### Documentation Not Updating

- Verify the pipeline completed successfully
- Check you pushed to the default branch (main/master)
- Pages deployment can take 1-2 minutes after pipeline success

## Customization

### Change Deployment Branch

Edit `.gitlab-ci.yml` and modify the `rules` section:

```yaml
rules:
  - if: $CI_COMMIT_BRANCH == "production"  # Deploy from 'production' branch
```

### Add Additional Stages

You can add testing or linting stages before deployment:

```yaml
test:
  stage: test
  script:
    - poetry run pytest
    - poetry run ruff check

pages:
  stage: deploy
  # ... rest of config
```

## Additional Resources

- [GitLab Pages Documentation](https://docs.gitlab.com/ee/user/project/pages/)
- [GitLab CI/CD Configuration](https://docs.gitlab.com/ee/ci/yaml/)
- [Sphinx Documentation](https://www.sphinx-doc.org/)
