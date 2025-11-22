# Pull Request: Nepal Entity Service - FastAPI Implementation

## 📋 Summary

This PR introduces the complete **Nepal Entity Service v2.0.0** - a modern, production-ready FastAPI implementation for managing Nepali public entities and their relationships with PostgreSQL backend.

## 🎯 Purpose

Transform the Nepal Entity Service into a high-performance, async-first REST API using modern Python technologies to provide:
- **Open data access** to Nepali public entities
- **Relationship tracking** between entities (people, organizations, government bodies, etc.)
- **Bilingual support** for English and Nepali names
- **Scalable architecture** with containerized deployment

## ✨ What's New

### Core Features
- ✅ **FastAPI Framework** - Modern async web framework with automatic OpenAPI docs
- ✅ **PostgreSQL 16** - Robust relational database with JSONB support
- ✅ **Async Architecture** - Fully asynchronous operations using SQLAlchemy 2.0
- ✅ **Docker Deployment** - Complete containerization with Docker Compose
- ✅ **Database Migrations** - Alembic integration for schema management
- ✅ **Type Safety** - Pydantic models for request/response validation
- ✅ **CORS Support** - Enabled for frontend integration
- ✅ **Health Checks** - Database and API health monitoring

### API Endpoints

#### Entities API (`/api/v1/entities/`)
- `POST /api/v1/entities/` - Create new entity
- `GET /api/v1/entities/` - List all entities with filtering
- `GET /api/v1/entities/{id}` - Get specific entity
- `PUT /api/v1/entities/{id}` - Update entity
- `DELETE /api/v1/entities/{id}` - Delete entity

#### Relationships API (`/api/v1/relationships/`)
- `POST /api/v1/relationships/` - Create new relationship
- `GET /api/v1/relationships/` - List relationships with filtering
- `GET /api/v1/relationships/{id}` - Get specific relationship
- `PUT /api/v1/relationships/{id}` - Update relationship
- `DELETE /api/v1/relationships/{id}` - Delete relationship

### Database Schema

#### Entities Table
```sql
- id: UUID (Primary Key)
- name: VARCHAR(255) - Entity name in English
- name_nepali: VARCHAR(255) - Entity name in Nepali (Optional)
- entity_type: ENUM (person, organization, government, political_party, other)
- description: TEXT - Detailed description
- metadata: JSONB - Flexible metadata storage
- created_at: TIMESTAMP - Creation timestamp
- updated_at: TIMESTAMP - Last update timestamp
- version: VARCHAR - Version tracking
```

#### Relationships Table
```sql
- id: UUID (Primary Key)
- source_entity_id: UUID (Foreign Key → entities.id)
- target_entity_id: UUID (Foreign Key → entities.id)
- relationship_type: VARCHAR - Type of relationship
- description: TEXT - Relationship description
- metadata: JSONB - Additional relationship data
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

## 🏗️ Technical Architecture

### Technology Stack
- **Python**: 3.12+
- **FastAPI**: 0.109.2
- **PostgreSQL**: 16-alpine
- **SQLAlchemy**: 2.0.25 (Async)
- **Alembic**: 1.13.1
- **asyncpg**: 0.29.0
- **Pydantic**: 2.6.1
- **uvicorn**: 0.27.1

### Project Structure
```
nepal-entity-service-fastapi/
├── app/
│   ├── api/v1/          # API routes and endpoints
│   ├── core/            # Configuration and database setup
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic validation schemas
│   └── main.py          # Application entry point
├── migrations/          # Alembic database migrations
├── tests/              # Test suite
├── docker-compose.yml  # Docker orchestration
├── Dockerfile          # Container definition
├── init.sql            # Database initialization
├── pyproject.toml      # Poetry dependencies
├── requirements.txt    # Pip dependencies
├── alembic.ini         # Alembic configuration
├── .env.example        # Environment template
└── README.md           # Documentation
```

## 🚀 Deployment

### Quick Start
```bash
# Clone and setup
git clone https://github.com/revil2025o/new1.git
cd new1
cp .env.example .env

# Start with Docker
docker-compose up -d

# Access API
# - API: http://localhost:8195
# - Docs: http://localhost:8195/docs
# - Health: http://localhost:8195/health
```

### Docker Services
1. **postgres**: PostgreSQL 16 with health checks and persistent volume
2. **api**: FastAPI application with hot-reload for development

### Environment Configuration
```env
# Database
POSTGRES_USER=nesuser
POSTGRES_PASSWORD=nespassword
POSTGRES_DB=nepal_entity_db
POSTGRES_PORT=5432

# API
HOST=0.0.0.0
PORT=8195
LOG_LEVEL=INFO
DATABASE_URL=postgresql://nesuser:nespassword@postgres:5432/nepal_entity_db
```

## 📊 Performance Benefits

- **Async Operations**: Non-blocking I/O for better concurrency
- **Connection Pooling**: Efficient database connection management
- **Auto-documentation**: Zero overhead for OpenAPI/Swagger docs
- **Type Safety**: Runtime validation with Pydantic reduces errors
- **Hot Reload**: Fast development cycles with uvicorn reload

## 🧪 Testing

### Run Tests
```bash
# With Docker
docker-compose exec api pytest

# Local development
pytest tests/
```

### Test Coverage
- Unit tests for models and schemas
- API integration tests
- Database migration tests

## 📝 Database Migrations

### Create Migration
```bash
alembic revision --autogenerate -m "Description"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback
```bash
alembic downgrade -1
```

## 🔒 Security Considerations

- ✅ Environment-based configuration (no hardcoded secrets)
- ✅ SQL injection protection via ORM
- ✅ Input validation with Pydantic
- ✅ CORS configuration for controlled access
- ⚠️ **TODO**: Add authentication/authorization
- ⚠️ **TODO**: Rate limiting implementation

## 📚 Documentation

### API Documentation
- **Interactive Docs**: http://localhost:8195/docs (Swagger UI)
- **ReDoc**: http://localhost:8195/redoc (Alternative documentation)
- **OpenAPI Schema**: http://localhost:8195/openapi.json

### Additional Resources
- [README.md](README.md) - Complete setup guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment instructions
- [.env.example](.env.example) - Configuration template

## 🔄 Migration Path

### From Previous Version
This is a complete rewrite with:
- Migration from synchronous to asynchronous operations
- Upgraded to Python 3.12 and FastAPI latest
- PostgreSQL instead of previous database (if any)
- Docker-native deployment

### Breaking Changes
- New API structure (`/api/v1/` prefix)
- UUID-based entity identification
- Changed response formats (Pydantic models)
- New database schema

## ✅ Checklist

- [x] Core FastAPI application setup
- [x] Database models and schemas
- [x] CRUD operations for entities
- [x] CRUD operations for relationships
- [x] Docker and Docker Compose configuration
- [x] Database migrations with Alembic
- [x] API documentation
- [x] README and deployment docs
- [x] Environment configuration
- [x] Health check endpoints
- [ ] Unit tests (in progress)
- [ ] Integration tests (in progress)
- [ ] Authentication/Authorization (planned)
- [ ] Rate limiting (planned)
- [ ] Caching layer with Redis (planned)

## 🎮 Usage Examples

### Create Entity
```bash
curl -X POST "http://localhost:8195/api/v1/entities/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nepal Government",
    "name_nepali": "नेपाल सरकार",
    "entity_type": "government",
    "description": "Federal Government of Nepal",
    "metadata": {"established": "2015"}
  }'
```

### List Entities
```bash
curl "http://localhost:8195/api/v1/entities/?entity_type=government"
```

### Create Relationship
```bash
curl -X POST "http://localhost:8195/api/v1/relationships/" \
  -H "Content-Type: application/json" \
  -d '{
    "source_entity_id": "uuid-here",
    "target_entity_id": "uuid-here",
    "relationship_type": "member_of",
    "description": "Member since 2020"
  }'
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [NewNepal-org/NepalEntityService](https://github.com/NewNepal-org/NepalEntityService) for contribution guidelines.

## 📄 License

This project is licensed under the **Hippocratic License 3.0** - an ethical open source license.

## 🙏 Acknowledgments

- NewNepal-org community
- FastAPI framework contributors
- PostgreSQL community

## 📮 Feedback

Please review and provide feedback on:
1. API design and endpoint structure
2. Database schema decisions
3. Documentation completeness
4. Deployment approach
5. Security considerations

---

**Repository**: https://github.com/revil2025o/new1  
**Version**: 2.0.0  
**Status**: Ready for Review  
**Author**: NewNepal Contributors
