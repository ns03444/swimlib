# Documentation Quick Start

## Build & View Documentation in 3 Steps

### Step 1: Install Documentation Dependencies

```bash
# Using Poetry (recommended)
poetry install --with docs

# Or using pip
pip install -e ".[docs]"
```

### Step 2: Build the Documentation

```bash
cd docs
make html
```

### Step 3: View in Browser

```bash
# macOS
open _build/html/index.html

# Linux
xdg-open _build/html/index.html

# Windows
start _build/html/index.html
```

## Live Development Mode

For automatic rebuilding and live preview:

```bash
cd docs
make livehtml
```

Then open http://127.0.0.1:8000 in your browser. The docs will auto-reload when you save changes!

## Common Commands

```bash
# Clean build (recommended if you see caching issues)
make clean && make html

# Check for broken links
make linkcheck

# Check documentation coverage
make coverage

# Build PDF (requires LaTeX)
make latexpdf

# Build EPUB
make epub
```

## Documentation Structure

- **Main Page:** [docs/index.rst](docs/index.rst)
- **API Reference:** [docs/api/](docs/api/)
- **Guides:** [docs/guides/](docs/guides/)
- **Examples:** [docs/examples/](docs/examples/)
- **Configuration:** [docs/conf.py](docs/conf.py)

## Need Help?

See [docs/README.md](docs/README.md) for detailed documentation authoring guide.

## Publishing

### To Read the Docs
1. Connect GitHub repo at readthedocs.org
2. Documentation will auto-build on each commit
3. Available at `https://swimlib.readthedocs.io`

### To GitHub Pages
```bash
make html
git checkout gh-pages
cp -r _build/html/* .
git add . && git commit -m "Update docs"
git push origin gh-pages
```

---

**Theme:** [Furo](https://pradyunsg.me/furo/) - Modern, clean, responsive
**Format:** [Sphinx](https://www.sphinx-doc.org/) with reStructuredText
**Docstring Style:** Sphinx-style with `:param:`, `:type:`, `:return:`, etc.
