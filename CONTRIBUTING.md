# Contributing to IKOB

First off, thank you for considering contributing to IKOB! It's much appreciated.

## Table of Contents

- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guide](#style-guide)


## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues to avoid 
duplicates. When you create a bug report, include as many details as 
possible.

**Great bug reports include:**
- A clear, descriptive title
- Steps to reproduce the behavior
- Expected behavior vs actual behavior
- Screenshots (if applicable)
- Environment details (project / python version etc.)

### 💡 Suggesting Features

Feature requests are welcome!

**Great feature requests include:**
- Clear problem statement
- Proposed solution
- Additional context
- Alternative solutions you've considered (if applicable)

### 📝 Improving Documentation

Documentation improvements are always welcome! This includes:
- Fixing typos
- Adding examples
- Clarifying confusing sections

### 💻 Development

To get your changes accepted into the ikob repo, first open an issue for discussion.

## Development Setup

### Getting started **without** push access to IKOB repo

Follow the instructions in the readme under [Installation and usage (manual installation)](README.md#installation-and-usage). \
Instead of cloning the IKOB repo directly, first create a fork and clone that repo.

1. Add upstream remote.
   ```bash
   git remote add upstream https://github.com/Stichting-CROW/ikob.git
   ```

2. Create a branch for your changes

3. Setup development environment, see the [Development section](README.md#development) in the readme

4. push your changes to the fork


5. Create a pull request against the master branch with 'compare across forks' on GitHub. See [Pull Request Process](#pull-request-process).

6. Wait for review

### Getting started **with** push acces to IKOB repo
Follow the instructions in the readme under [Installation and usage (manual installation)](README.md#installation-and-usage)

1. Create an issue or find an existing issue related to your work

2. From within the issue, create a branch for your changes

3. Fetch the new branch and switch to it

4. Push your work and open a PR linked to the branch. See [Pull Request Process](#pull-request-process).

5. Wait for review

## Pull Request Process

### Before Submitting

0. **Open an issue first** for discussion.

1. **Update your branch** with the latest upstream changes: \
   From a fork:
   ```bash
   git fetch upstream
   git merge upstream/master
   ```
   From the ikob repo:
   ```bash
   git fetch origin
   git merge origin/master
   ```


2. **format your code**
   ```bash
   python -m ruff format .
   ```

3. **Run the full test suite** and ensure all tests pass:
   ```bash
   pytest .
   ```
   for more about testing see [the relevant section in the readme](README.md#testing)



### PR Checklist

- [ ] My code follows the project's [style guidelines](#style-guide)
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas and focusing on _why_ the code is the way it is over _what_ the code doing. _What_ should ideally be clear from the code itself.
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass with my changes

## Style Guide

### Commit Messages

We follow [Conventional Commits](https://conventionalcommits.org/):

```
<type>(<optional scope>): <description> 

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests
- `chore`: Maintenance tasks

**Examples:**
```
fix(ui): Display correct units for parking costs
docs: Add contributing.md
```

### Code Style

- Use ruff

### Testing

- Bug fixes should include regression tests
- Tests should be deterministic (no flaky tests)

---

Thank you for contributing! 🎉
