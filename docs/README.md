# swimlib Documentation

This directory contains the Sphinx documentation for swimlib.

## Building Documentation

### Prerequisites

Install documentation dependencies:

```bash
# Using Poetry
poetry install --with docs

# Or using pip
pip install -e ".[docs]"
```

### Build HTML Documentation

```bash
cd docs
make html
```

The generated HTML will be in `docs/_build/html/`. Open `index.html` in a browser.

### Live Preview

For live-reloading during development:

```bash
cd docs
make livehtml
```

This will start a local server at `http://127.0.0.1:8000` with auto-reload on file changes.

### Other Build Formats

```bash
# PDF (requires LaTeX)
make latexpdf

# EPUB
make epub

# Check for broken links
make linkcheck

# Check documentation coverage
make coverage

# Clean build directory
make clean
```

## Documentation Structure

```
docs/
├── conf.py              # Sphinx configuration
├── index.rst            # Main documentation page
├── api/                 # API reference
│   ├── core.rst         # Core modules (asdb, logging, software_matrix)
│   ├── ssh.rst          # SSH connection management
│   ├── f5.rst           # F5 BIG-IP modules
│   └── exceptions.rst   # Exception reference
├── guides/              # User guides
│   ├── installation.rst
│   ├── quickstart.rst
│   ├── configuration.rst
│   ├── workflows.rst
│   ├── testing.rst
│   └── best_practices.rst
├── examples/            # Code examples
│   ├── basic_usage.rst
│   ├── f5_upgrade.rst
│   ├── error_handling.rst
│   ├── parallel_execution.rst
│   └── testing_strategies.rst
├── development/         # Development documentation
│   ├── contributing.rst
│   ├── changelog.rst
│   └── roadmap.rst
├── _static/             # Custom CSS, images, etc.
└── _templates/          # Custom Sphinx templates
```

## Theme

This documentation uses the **Furo** theme - a modern, clean, responsive Sphinx theme with:

- Beautiful typography and spacing
- Smart dark/light mode switching
- Excellent search UI
- Mobile-friendly responsive design
- Minimal configuration required

## Sphinx Extensions

The documentation uses these Sphinx extensions:

### Core Extensions
- `sphinx.ext.autodoc` - Automatic documentation from docstrings
- `sphinx.ext.autosummary` - Generate autodoc summaries
- `sphinx.ext.napoleon` - Google & NumPy style docstring support
- `sphinx.ext.intersphinx` - Link to other project documentation
- `sphinx.ext.viewcode` - Add links to highlighted source code
- `sphinx.ext.todo` - Support for TODO items
- `sphinx.ext.coverage` - Documentation coverage checker

### Third-Party Extensions
- `sphinx-copybutton` - Add copy button to code blocks
- `sphinx-inline-tabs` - Inline tabbed content
- `myst-parser` - Markdown support

## Docstring Style

swimlib uses **Sphinx-style docstrings** with `:param:`, `:type:`, `:return:`, `:rtype:`, etc.

Example:

```python
def example_function(param1, param2):
    """Brief description of the function.

    Longer description explaining the function's purpose, behavior,
    and any important details.

    :param param1: Description of param1
    :type param1: str
    :param param2: Description of param2
    :type param2: int
    :return: Description of return value
    :rtype: bool
    :raises ValueError: When param2 is negative

    Example:
        Usage example::

            result = example_function("test", 42)
            print(f"Result: {result}")

    .. versionadded:: 0.1.0
    """
    pass
```

## Contributing to Documentation

When adding new modules or features:

1. **Update docstrings** - Add comprehensive docstrings to all public classes, methods, and functions
2. **Add to API reference** - Include new modules in appropriate `api/*.rst` files
3. **Update guides** - Add relevant usage examples to guide files
4. **Test the build** - Run `make html` and check for warnings
5. **Check links** - Run `make linkcheck` to verify external links

## Best Practices

- Keep docstrings up-to-date with code changes
- Include example code in docstrings
- Use cross-references (`:mod:`, `:class:`, `:func:`, `:meth:`) to link related documentation
- Add `.. versionadded::`, `.. versionchanged::`, and `.. deprecated::` directives
- Use admonitions (`.. note::`, `.. warning::`, `.. important::`) for important information
- Include type hints in function signatures (Sphinx will render them automatically)

## Publishing Documentation

### Read the Docs

This project can be published to Read the Docs:

1. Connect GitHub repository to Read the Docs
2. RTD will automatically build on each commit
3. Documentation will be available at `https://swimlib.readthedocs.io`

### GitHub Pages

To publish to GitHub Pages:

```bash
# Build documentation
cd docs
make html

# Copy to gh-pages branch
git checkout gh-pages
cp -r _build/html/* .
git add .
git commit -m "Update documentation"
git push origin gh-pages
```

## Troubleshooting

### Build Warnings

Sphinx is strict about documentation. Common warnings:

- **"undefined label"** - Fix cross-references
- **"document isn't included in any toctree"** - Add file to a `.. toctree::` directive
- **"duplicate label"** - Use unique section labels
- **"WARNING: autodoc: failed to import"** - Check Python path in `conf.py`

### Clean Rebuild

If you encounter caching issues:

```bash
make clean
make html
```

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [Furo Theme Documentation](https://pradyunsg.me/furo/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Docstring Conventions (PEP 257)](https://peps.python.org/pep-0257/)
