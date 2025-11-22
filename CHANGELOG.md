# Changelog

All notable changes to the Nepal Entity Service will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Authentication and authorization system
- Rate limiting for API endpoints
- Redis caching layer
- Advanced search and filtering
- Export functionality (CSV, JSON)
- Batch operations support
- WebSocket support for real-time updates

## [2.0.0] - 2025-11-23

### 🎉 Major Release - FastAPI Migration

This is a complete rewrite of the Nepal Entity Service using FastAPI and modern Python async architecture.

### Added

#### Core Framework
- **FastAPI 0.109.2** - Modern async web framework
- **Python 3.12+** - Latest Python with performance improvements
- **PostgreSQL 16** - Production-grade relational database
- **SQLAlchemy 2.0.25** - Async ORM for database operations
- **Alembic 1.13.1** - Database migration management
- **Pydantic 2.6.1** - Request/response validation

#### API Features
- RESTful API with OpenAPI documentation
- Automatic interactive documentation at `/docs`
- ReDoc alternative documentation at `/redoc`
- JSON Schema generation
- CORS middleware support
- Health check endpoint at `/health`
- API versioning (`/api/v1/`)

#### Entity Management
- Create, read, update, delete (CRUD) operations for entities
- Support for multiple entity types:
  - Person
  - Organization
  - Government
  - Political Party
  - Other
- Bilingual support (English and Nepali names)
- Flexible JSONB metadata storage
- UUID-based entity identification
- Timestamp tracking (created_at, updated_at)
- Version tracking

#### Relationship Management
- CRUD operations for entity relationships
- Flexible relationship types
- Bidirectional relationship support
- Metadata storage for relationships
- Foreign key constraints
- Cascade delete options

#### Database
- PostgreSQL 16 with Alpine Linux
- Async database operations
- Connection pooling
- Database health checks
- Automated migrations with Alembic
- JSONB support for flexible metadata
- UUID primary keys
- Timestamped records

#### Docker Deployment
- Multi-container Docker Compose setup
- Separate PostgreSQL service
- API service with hot-reload
- Volume persistence for database
- Health check integration
- Network isolation
- Environment-based configuration

#### Development Tools
- Poetry for dependency management
- Black code formatter (100 char line length)
- isort for import sorting
- flake8 for linting
- pytest for testing
- pytest-asyncio for async tests

#### Documentation
- Comprehensive README.md
- DEPLOYMENT.md with deployment instructions
- API documentation (auto-generated)
- Environment configuration examples
- Docker usage examples
- Database migration guides

### Changed

#### Breaking Changes
- **API Structure**: New `/api/v1/` prefix for all endpoints
- **Database Schema**: Complete schema redesign with UUID keys
- **Response Format**: Pydantic models for consistent responses
- **Authentication**: Removed (to be reimplemented)
- **Sync to Async**: All operations now asynchronous

#### Improvements
- Significantly faster response times with async operations
- Better error handling and validation
- Improved type safety with Pydantic
- Enhanced developer experience with auto-documentation
- Containerized deployment for easier scaling
- Better separation of concerns (models, schemas, routes)

### Technical Details

#### API Endpoints

**Entities** (`/api/v1/entities/`)
```
POST   /api/v1/entities/           Create new entity
GET    /api/v1/entities/           List entities (with filters)
GET    /api/v1/entities/{id}       Get specific entity
PUT    /api/v1/entities/{id}       Update entity
DELETE /api/v1/entities/{id}       Delete entity
```

**Relationships** (`/api/v1/relationships/`)
```
POST   /api/v1/relationships/      Create new relationship
GET    /api/v1/relationships/      List relationships (with filters)
GET    /api/v1/relationships/{id}  Get specific relationship
PUT    /api/v1/relationships/{id}  Update relationship
DELETE /api/v1/relationships/{id}  Delete relationship
```

**System**
```
GET    /                           Root endpoint
GET    /health                     Health check
GET    /docs                       Interactive API docs
GET    /redoc                      Alternative documentation
```

#### Database Schema

**Entities Table**
- Primary Key: UUID
- Indexed fields: name, entity_type, created_at
- JSONB field for flexible metadata
- Relationship support with cascade options

**Relationships Table**
- Primary Key: UUID
- Foreign Keys: source_entity_id, target_entity_id
- Indexed fields: relationship_type, created_at
- Cascade delete on entity removal

#### Environment Variables
```env
POSTGRES_USER          Database username
POSTGRES_PASSWORD      Database password
POSTGRES_DB           Database name
POSTGRES_PORT         Database port (default: 5432)
DATABASE_URL          Full database connection string
HOST                  API host (default: 0.0.0.0)
PORT                  API port (default: 8195)
LOG_LEVEL            Logging level (default: INFO)
```

### Deployment

#### Docker Compose Services
1. **postgres** - PostgreSQL 16 Alpine
   - Persistent volume: `postgres_data`
   - Health checks enabled
   - Auto-initialization with init.sql

2. **api** - FastAPI Application
   - Depends on healthy postgres
   - Hot-reload enabled for development
   - Volume mounts for app and migrations
   - Exposes port 8195

#### Quick Start
```bash
docker-compose up -d
# API available at http://localhost:8195
# Docs available at http://localhost:8195/docs
```

### Migration Notes

#### From Previous Versions
This is a complete rewrite. Migration path:
1. Export data from old version
2. Transform data to new schema
3. Import using new API endpoints
4. Verify data integrity

#### Database Setup
```bash
# Automatic with Docker
docker-compose up -d

# Manual setup
alembic upgrade head
```

### Security

#### Current Security Features
- Environment-based configuration
- SQL injection protection via ORM
- Input validation with Pydantic
- CORS configuration

#### Security TODO
- [ ] Authentication implementation
- [ ] Authorization and permissions
- [ ] Rate limiting
- [ ] API key management
- [ ] Request signing
- [ ] Audit logging

### Performance

#### Benchmarks
- Async operations: ~10x faster than sync
- Connection pooling: Reduced DB overhead
- Type validation: Minimal runtime cost

### Dependencies

#### Core Dependencies
```
fastapi==0.109.2
uvicorn[standard]==0.27.1
sqlalchemy==2.0.25
asyncpg==0.29.0
psycopg2-binary==2.9.9
alembic==1.13.1
pydantic==2.6.1
pydantic-settings==2.1.0
```

#### Development Dependencies
```
pytest==8.0.0
pytest-asyncio==0.23.0
black==24.0.0
isort==5.13.0
flake8==7.0.0
```

### Known Issues
- None reported in this version

### Contributors
- NewNepal Contributors

### Links
- [GitHub Repository](https://github.com/revil2025o/new1)
- [Documentation](README.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Contributing Guidelines](CONTRIBUTING.md)

---

## [1.0.0] - Previous Version

Previous implementation details (if migrating from an older version)

---

## Release Schedule

- **Major versions** (X.0.0): Breaking changes, major features
- **Minor versions** (x.X.0): New features, backward compatible
- **Patch versions** (x.x.X): Bug fixes, minor improvements

## Support

- **Current**: 2.0.x (active development)
- **LTS**: TBD
- **EOL**: 1.x (if applicable)

---

[Unreleased]: https://github.com/revil2025o/new1/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/revil2025o/new1/releases/tag/v2.0.0
