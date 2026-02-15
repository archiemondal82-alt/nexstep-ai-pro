# Contributing to NexStep AI Pro

First off, thank you for considering contributing to NexStep AI Pro! 🎉

This document provides guidelines for contributing to the project. Following these guidelines helps maintain code quality and makes the contribution process smooth for everyone.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)

---

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for everyone. We expect all contributors to:

- Use welcoming and inclusive language
- Respect differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or trolling
- Publishing others' private information
- Inappropriate sexual attention or advances
- Other conduct that's unprofessional or harmful

---

## 💡 How Can I Contribute?

### Reporting Bugs 🐛

Found a bug? Help us fix it!

**Before submitting:**
1. Check [existing issues](https://github.com/yourusername/nexstep-ai-pro/issues)
2. Try the latest version
3. Gather relevant information

**Submit a bug report:**
- Use the bug report template
- Include clear title and description
- Provide steps to reproduce
- Share expected vs. actual behavior
- Include screenshots if applicable
- Note your environment (OS, Python version, etc.)

### Suggesting Features 💡

Have an idea? We'd love to hear it!

**Before suggesting:**
1. Check if it already exists in [planned features](CHANGELOG.md#unreleased)
2. Verify it aligns with project goals
3. Consider if it's broadly useful

**Submit a feature request:**
- Use the feature request template
- Explain the problem it solves
- Describe your proposed solution
- Provide examples or mockups
- Explain why it would benefit users

### Improving Documentation 📚

Documentation improvements are always welcome!

**Ways to help:**
- Fix typos or grammar
- Clarify confusing sections
- Add missing examples
- Update outdated information
- Translate to other languages

### Contributing Code 💻

Ready to code? Awesome!

**Good first issues:**
Look for issues labeled:
- `good-first-issue`
- `help-wanted`
- `documentation`

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.8+
- Git
- Google Gemini API key
- Text editor or IDE

### Setup Steps

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/nexstep-ai-pro.git
   cd nexstep-ai-pro
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/nexstep-ai-pro.git
   ```

4. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Activate:
   # Windows: venv\Scripts\activate
   # Mac/Linux: source venv/bin/activate
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

6. **Configure environment**
   ```bash
   cp .env.template .env
   # Edit .env and add your API key
   ```

7. **Run the app**
   ```bash
   streamlit run nexstep_pro.py
   ```

### Development Dependencies

Create `requirements-dev.txt`:
```
pytest==7.4.3
pytest-cov==4.1.0
black==23.12.1
flake8==7.0.0
pylint==3.0.3
mypy==1.8.0
```

---

## 📝 Coding Standards

### Python Style Guide

We follow **PEP 8** with some exceptions:

#### Formatting
- **Line length**: Max 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes `"` for strings
- **Blank lines**: 
  - 2 before class definitions
  - 1 between methods
  - 1 to separate logical sections

#### Naming Conventions
- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: Leading underscore `_private_method`

#### Example:
```python
class CareerAnalyzer:
    """Analyzes career paths based on user input."""
    
    MAX_RECOMMENDATIONS = 3
    
    def __init__(self, config):
        self.config = config
        self._api_key = config.get_api_key()
    
    def analyze_skills(self, user_input: str) -> Dict:
        """
        Analyze user skills and return career recommendations.
        
        Args:
            user_input: User's skills and experience as string
        
        Returns:
            Dictionary containing career analysis results
        """
        # Implementation here
        pass
```

### Code Quality Tools

**Format with Black:**
```bash
black nexstep_pro.py --line-length 100
```

**Lint with Flake8:**
```bash
flake8 nexstep_pro.py --max-line-length=100
```

**Type checking with mypy:**
```bash
mypy nexstep_pro.py
```

### Documentation

- Add docstrings to all public functions/classes
- Use Google-style docstrings
- Include type hints
- Comment complex logic
- Update README for new features

**Example:**
```python
def extract_text(uploaded_file) -> str:
    """
    Extract text content from uploaded PDF file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        Extracted text as string, or empty string if extraction fails
    
    Raises:
        PDFExtractionError: If PDF is corrupted or password-protected
    
    Example:
        >>> file = st.file_uploader("Upload PDF")
        >>> text = extract_text(file)
        >>> print(text[:100])
    """
    # Implementation
```

### Testing

Write tests for new features:

```python
# tests/test_pdf_handler.py
import pytest
from nexstep_pro import PDFHandler

def test_extract_text_success():
    """Test successful text extraction from PDF."""
    handler = PDFHandler()
    # Test implementation
    
def test_extract_text_invalid_file():
    """Test handling of invalid PDF file."""
    handler = PDFHandler()
    # Test implementation
```

Run tests:
```bash
pytest tests/
pytest --cov=nexstep_pro tests/  # With coverage
```

---

## 🔄 Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no code change)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples

**Good commits:**
```
feat(ai): add support for multiple AI models

- Implement model selection dropdown
- Add fallback for unavailable models
- Update documentation

Closes #42
```

```
fix(pdf): handle corrupted PDF files gracefully

Previously, corrupted PDFs would crash the app.
Now shows user-friendly error message.

Fixes #123
```

```
docs(readme): add troubleshooting section

Added common issues and solutions based on user feedback.
```

**Bad commits:**
```
❌ fixed stuff
❌ update
❌ minor changes
❌ asdfasdf
```

### Best Practices

- Keep commits atomic (one logical change per commit)
- Write clear, descriptive messages
- Reference issues: `Fixes #123`, `Closes #456`
- Use present tense: "add feature" not "added feature"

---

## 🚀 Pull Request Process

### Before Submitting

1. **Update your fork**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Write clean code
   - Add tests
   - Update documentation

4. **Test thoroughly**
   ```bash
   # Run the app
   streamlit run nexstep_pro.py
   
   # Test manually
   # Run automated tests (if available)
   pytest tests/
   ```

5. **Format and lint**
   ```bash
   black nexstep_pro.py --line-length 100
   flake8 nexstep_pro.py
   ```

6. **Commit changes**
   ```bash
   git add .
   git commit -m "feat(scope): descriptive message"
   ```

7. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

### Submitting Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Fill out the template:
   - Clear title
   - Description of changes
   - Related issues
   - Testing performed
   - Screenshots (if UI changes)

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## How Has This Been Tested?
- [ ] Manual testing
- [ ] Automated tests
- [ ] Tested on Windows/Mac/Linux

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Added comments for complex code
- [ ] Updated documentation
- [ ] No new warnings
- [ ] Added tests (if applicable)
- [ ] All tests pass
```

### Review Process

1. Maintainers review within 7 days
2. Address feedback promptly
3. Make requested changes
4. Update PR with fixes
5. Once approved, maintainer will merge

### After Merging

1. Delete your branch
   ```bash
   git branch -d feature/amazing-feature
   git push origin --delete feature/amazing-feature
   ```

2. Update your main
   ```bash
   git checkout main
   git pull upstream main
   ```

---

## 🐛 Bug Reports

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Enter '....'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Windows 11, macOS 13, Ubuntu 22.04]
 - Python version: [e.g. 3.9.7]
 - Streamlit version: [e.g. 1.31.0]
 - Browser: [e.g. Chrome 120]

**Additional context**
Any other relevant information.

**Logs**
```
Paste relevant logs here
```
```

---

## ✨ Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem. Ex. I'm frustrated when [...]

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions or features you've considered.

**Additional context**
Mockups, examples, or references.

**Would you like to implement this feature?**
- [ ] Yes, I can implement this
- [ ] No, just suggesting
```

---

## 🎯 Priority Labels

Issues and PRs are labeled by priority:

- `critical`: Must be fixed immediately
- `high`: Important, fix soon
- `medium`: Should be addressed
- `low`: Nice to have
- `wontfix`: Not planned

---

## 🏆 Recognition

Contributors will be:
- Listed in README
- Mentioned in release notes
- Given credit in CHANGELOG

---

## 📞 Questions?

- 💬 GitHub Discussions
- 📧 Email: support@example.com
- 💭 Open an issue with `question` label

---

## 🙏 Thank You!

Your contributions make NexStep AI Pro better for everyone. We appreciate your time and effort!

---

**Happy Contributing! 🚀**

*Maintained by Anubhab Mondal*
