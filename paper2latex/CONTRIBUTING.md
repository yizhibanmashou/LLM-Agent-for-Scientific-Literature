# Contributing to paper2latex

Thank you for your interest in contributing to paper2latex! This document provides guidelines for contributing.

## Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/yourusername/paper2latex.git
   cd paper2latex
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

3. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Start GROBID** (required for testing):
   ```bash
   docker run -d -p 8070:8070 lfoppiano/grobid:0.8.0
   ```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/paper2latex --cov-report=html

# Run specific test file
pytest tests/test_tei_parser.py -v
```

## Code Style

We use `black` for formatting and `ruff` for linting:

```bash
# Format code
black src/ tests/

# Check linting
ruff check src/ tests/

# Fix linting issues
ruff check --fix src/ tests/
```

## Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass
   - Follow the code style guidelines

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test changes
   - `refactor:` for code refactoring

4. **Push and create a PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

   Then create a Pull Request on GitHub.

## Areas for Contribution

### High Priority

- **Formula OCR Integration**: Implement pix2tex or similar for formula recognition
- **Figure Caption Detection**: Extract and parse figure captions from TEI
- **LaTeX Compilation**: Add automatic compilation checking and error fixing
- **Integration Tests**: Add end-to-end tests with real PDFs

### Medium Priority

- **URL/arXiv/DOI Support**: Add support for non-local PDF sources
- **Scanned PDF Support**: OCR fallback for scanned documents
- **Multi-language Support**: Better handling of non-English papers
- **Performance**: Optimize for large documents (100+ pages)

### Documentation

- **Tutorials**: Step-by-step guides for common use cases
- **API Documentation**: Detailed API reference
- **Examples**: More usage examples for different scenarios

## Testing Guidelines

- Add unit tests for all new functions
- Add integration tests for new features
- Ensure test coverage remains above 80%
- Test edge cases and error conditions

## Documentation Guidelines

- Update README.md for user-facing changes
- Add docstrings to all public functions
- Include type hints for all function parameters
- Update SPEC.md if changing the design

## Questions?

- Open an issue for questions or discussions
- Check existing issues before creating a new one
- Be respectful and constructive in all interactions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
