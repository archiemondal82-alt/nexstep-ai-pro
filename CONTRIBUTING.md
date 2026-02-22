# Contributing to JobLess AI

First off, thank you for considering contributing to JobLess AI! 🎉

This document provides guidelines for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

---

## 🤝 Code of Conduct

We are committed to a welcoming and inclusive environment. Contributors should use respectful language, accept constructive criticism gracefully, and focus on what's best for the community.

---

## 💡 How Can I Contribute?

- **Bug reports** — Use the bug report template with reproduction steps and your environment
- **Feature requests** — Explain the problem it solves and why it's broadly useful
- **Documentation** — Fix typos, clarify sections, add examples
- **Code** — Look for issues labeled `good-first-issue` or `help-wanted`

---

## 🛠️ Development Setup

1. **Fork and clone**
```bash
git clone https://github.com/YOUR_USERNAME/jobless-ai.git
cd jobless-ai
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the app**
```bash
streamlit run jobless_ai_public.py
```

---

## 📝 Coding Standards

- Follow **PEP 8** (max line length 100)
- Use `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants
- Add docstrings to all public functions/classes (Google-style)
- Include type hints

**Format with Black:**
```bash
black jobless_ai_public.py --line-length 100
```

**Lint with Flake8:**
```bash
flake8 jobless_ai_public.py --max-line-length=100
```

---

## 🔄 Commit Guidelines

Format: `<type>(<scope>): <subject>`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

Examples:
```
feat(ai): add support for OpenAI provider
fix(pdf): handle corrupted PDF files gracefully
docs(readme): update provider list
```

---

## 🚀 Pull Request Process

1. Update your fork from upstream
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes, test thoroughly, format code
4. Commit: `git commit -m "feat(scope): message"`
5. Push and open a Pull Request with a clear description

---

## 🏆 Recognition

Contributors are listed in the README and mentioned in release notes.

---

## 📞 Questions?

Open an issue with the `question` label.

---

**Happy Contributing! 🚀**

*Maintained by Anubhab Mondal*
