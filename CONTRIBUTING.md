# Contributing to Nepal Entity Service

🇳🇵 Thank you for your interest in contributing to the Nepal Entity Service! This document provides guidelines and instructions for contributing.

## 📜 Code of Conduct

By participating in this project, you agree to abide by our ethical principles as outlined in the Hippocratic License 3.0. We are committed to providing a welcoming and inclusive environment for all contributors.

## 🎯 How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title** - Descriptive summary of the issue
- **Description** - Detailed explanation of the problem
- **Steps to reproduce** - Numbered list of exact steps
- **Expected behavior** - What you expected to happen
- **Actual behavior** - What actually happened
- **Environment** - OS, Python version, Docker version, etc.
- **Screenshots** - If applicable
- **Logs** - Relevant error messages or stack traces

**Example:**
```markdown
### Bug: Entity creation fails with special characters in Nepali name

**Environment:**
- OS: Ubuntu 22.04
- Python: 3.12.1
- Docker: 24.0.7

**Steps to reproduce:**
1. Send POST request to `/api/v1/entities/`
2. Include Nepali name with special characters: "नेपाल सरकार"
3. Observe error response

**Expected:** Entity created successfully
**Actual:** 500 Internal Server Error

**Error log:**
```
UnicodeDecodeError: 'utf-8' codec can't decode...
```
```

### ✨ Suggesting Features

Feature requests are welcome! Please provide:

- **Clear title** - Brief feature description
- **Use case** - Why this feature is needed
- **Proposed solution** - How you envision it working
- **Alternatives** - Other approaches you've considered
- **Additional context** - Mockups, examples, etc.

### 🔧 Pull Requests

1. **Fork the repository**
2. **Create a feature branch** from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following our coding standards
4. **Write tests** for your changes
5. **Run the test suite** to ensure everything passes
6. **Commit your changes** with descriptive messages
7. **Push to your fork**
8. **Open a Pull Request** using our template

## 💻 Development Setup

### Prerequisites

- Python 3.12 or higher
- Docker and Docker Compose
- Poetry (optional but recommended)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/revil2025o/new1.git
   cd new1
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # Or using Poetry
   poetry install
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

5. **Start PostgreSQL with Docker**
   ```bash
   docker-compose up -d postgres
   ```

6. **Run migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start development server**
   ```bash
   uvicorn app.main:app --reload --port 8195
   ```

8. **Access the API**
   - API: http://localhost:8195
   - Docs: http://localhost:8195/docs

### Docker Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head

# Access API shell
docker-compose exec api bash
```

## 🎨 Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

- **Line length**: 100 characters (configured in black)
- **Formatter**: Black
- **Import sorting**: isort
- **Linter**: flake8

### Code Formatting

Before committing, format your code:

```bash
# Format with black
black app/ tests/

# Sort imports
isort app/ tests/

# Check with flake8
flake8 app/ tests/
```

### Naming Conventions

- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`
- **Files**: `snake_case.py`

### Type Hints

Always use type hints for function parameters and return values:

```python
from typing import Optional, List
from uuid import UUID

async def get_entity(entity_id: UUID) -> Optional[Entity]:
    """Retrieve an entity by ID."""
    pass

async def list_entities(skip: int = 0, limit: int = 100) -> List[Entity]:
    """List entities with pagination."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
async def create_relationship(
    source_id: UUID,
    target_id: UUID,
    relationship_type: str
) -> Relationship:
    """Create a relationship between two entities.
    
    Args:
        source_id: UUID of the source entity
        target_id: UUID of the target entity
        relationship_type: Type of relationship (e.g., 'member_of')
    
    Returns:
        Created Relationship object
    
    Raises:
        EntityNotFoundError: If either entity doesn't exist
        ValidationError: If relationship_type is invalid
    """
    pass
```

## 🧪 Testing

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the structure of the `app/` directory
- Name test files with `test_` prefix
- Use descriptive test function names

**Example:**
```python
import pytest
from uuid import uuid4

@pytest.mark.asyncio
async def test_create_entity_success():
    """Test successful entity creation with valid data."""
    # Arrange
    entity_data = {
        "name": "Test Entity",
        "entity_type": "organization",
        "description": "Test description"
    }
    
    # Act
    response = await client.post("/api/v1/entities/", json=entity_data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["name"] == "Test Entity"

@pytest.mark.asyncio
async def test_create_entity_invalid_type():
    """Test entity creation fails with invalid entity_type."""
    entity_data = {
        "name": "Test Entity",
        "entity_type": "invalid_type",
        "description": "Test"
    }
    
    response = await client.post("/api/v1/entities/", json=entity_data)
    assert response.status_code == 422
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_entities.py

# Run specific test
pytest tests/test_entities.py::test_create_entity_success

# Run with verbose output
pytest -v
```

## 📝 Commit Messages

Write clear, descriptive commit messages following conventional commits:

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples

```bash
# Good commit messages
feat(entities): add support for bulk entity creation
fix(relationships): resolve cascade delete issue with orphaned entities
docs(readme): update deployment instructions for Docker
test(entities): add integration tests for entity filtering
refactor(database): optimize query performance for entity listing

# Bad commit messages (avoid these)
fix bug
update code
changes
WIP
asdfasdf
```

## 🔄 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No console.log or debug code
- [ ] Environment variables documented
- [ ] Database migrations created (if needed)

### PR Title

Follow conventional commits format:
```
feat(scope): brief description
fix(scope): brief description
docs: brief description
```

### PR Description

Use the provided template and include:

1. **Summary** - What does this PR do?
2. **Type of change** - Feature, bug fix, etc.
3. **Testing** - How was it tested?
4. **Screenshots** - If UI changes
5. **Breaking changes** - If any
6. **Migration notes** - If needed

### Review Process

1. Automated checks must pass (tests, linting)
2. At least one maintainer approval required
3. All review comments addressed
4. Merge conflicts resolved
5. Documentation updated

## 🗂️ Project Structure

```
nepal-entity-service-fastapi/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/      # API route handlers
│   │       └── router.py       # Router configuration
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   └── database.py        # Database connection
│   ├── models/                # SQLAlchemy models
│   │   ├── entity.py
│   │   └── relationship.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── entity.py
│   │   └── relationship.py
│   └── main.py               # Application entry point
├── migrations/               # Alembic migrations
├── tests/
│   ├── api/                 # API endpoint tests
│   ├── models/              # Model tests
│   └── conftest.py          # Pytest configuration
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── requirements.txt
```

## 🗃️ Database Migrations

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "descriptive message"

# Review the generated migration file
# Edit if necessary to ensure correctness

# Apply migration
alembic upgrade head
```

### Migration Best Practices

- Always review auto-generated migrations
- Test migrations on a copy of production data
- Include both upgrade and downgrade scripts
- Document complex migrations
- Test rollback procedures

## 🔐 Security

### Reporting Vulnerabilities

**DO NOT** create public issues for security vulnerabilities. Instead:

1. Email security concerns to project maintainers
2. Provide detailed description
3. Include steps to reproduce
4. Wait for confirmation before public disclosure

### Security Best Practices

- Never commit secrets or credentials
- Use environment variables for sensitive data
- Validate all user inputs
- Use parameterized queries (handled by SQLAlchemy)
- Keep dependencies updated
- Follow OWASP guidelines

## 📄 License

By contributing, you agree that your contributions will be licensed under the Hippocratic License 3.0.

## 🙋 Questions?

- Create a GitHub issue for questions
- Join community discussions
- Refer to existing documentation

## 🙏 Recognition

All contributors will be recognized in our README and release notes. Thank you for helping make the Nepal Entity Service better!

---

**Last Updated**: 2025-11-23  
**Version**: 2.0.0
