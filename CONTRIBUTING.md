# 🤝 Contributing Guide

## Welcome!

Thank you for considering contributing to the AI 2027 Scenario Intelligence RAG project!

---

## 🎯 How to Contribute

### 1. Report Bugs

Found a bug? Open an issue with:
- **Description:** What went wrong?
- **Steps to reproduce:** How can we recreate it?
- **Expected behavior:** What should happen?
- **Actual behavior:** What actually happened?
- **Environment:** OS, Python version, package versions

### 2. Suggest Features

Have an idea? Open an issue with:
- **Feature description:** What do you want to add?
- **Use case:** Why is this useful?
- **Implementation ideas:** How might this work?

### 3. Submit Pull Requests

**Process:**
1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests (if applicable)
5. Update documentation
6. Commit (`git commit -m 'Add amazing feature'`)
7. Push (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## 🏗️ Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-2027-scenario-intelligence-rag.git
cd ai-2027-scenario-intelligence-rag

# Add upstream remote
git remote add upstream https://github.com/nandu00000003435-max/ai-2027-scenario-intelligence-rag.git

# Create branch
git checkout -b feature/my-feature

# Make changes, then:
git add .
git commit -m "feat: Add my feature"
git push origin feature/my-feature
```

---

## 📝 Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://github.com/psf/black) for formatting
- Use type hints
- Add docstrings

**Format code:**
```bash
pip install black
black src/
```

### Commit Message Format

```
<type>: <description>

[optional body]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Add tests
- `chore`: Maintenance

**Examples:**
```
feat: Add graph-based retrieval
fix: Handle empty query edge case
docs: Update README with new features
```

---

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

### Add Tests

```python
# tests/test_retrieval.py
def test_branch_filtering():
    retriever = HybridRetriever()
    results = retriever.retrieve("test", branch_filter="race")
    
    # All results should be from race or shared branch
    for r in results:
        assert r['branch'] in ['race', 'shared']
```

---

## 📚 Documentation

### Update Documentation

If you change functionality, update:
- README.md (if user-facing)
- HOW_IT_WORKS.md (if technical)
- ARCHITECTURE.md (if design changes)
- Docstrings (always)

### Documentation Style

```python
def my_function(arg1: str, arg2: int) -> Dict:
    """
    Brief description of what function does
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
    
    Returns:
        Description of return value
    
    Example:
        >>> result = my_function("test", 42)
        >>> print(result)
    """
```

---

## 🎯 Priority Areas for Contribution

### High Priority
1. **Graph-based retrieval** (Neo4j integration)
2. **Web UI** (Streamlit or React)
3. **Multi-document support**
4. **More evaluation questions** (expand test suite)

### Medium Priority
1. **Caching layer** (Redis)
2. **Async retrieval** (parallel processing)
3. **Better reranking** (cross-encoder)
4. **Monitoring** (Prometheus metrics)

### Low Priority
1. **Docker deployment**
2. **CI/CD pipeline**
3. **Additional LLM providers** (Anthropic, Cohere)

---

## 🏆 Recognition

Contributors will be:
- Listed in README.md
- Mentioned in release notes
- Credited in documentation

---

## 📧 Questions?

- Open an issue
- Email: nandu00000003435@gmail.com

---

**Thank you for contributing! 🙏**
