# Nepal Entity Service - FastAPI

🇳🇵 Open Source, open data, and open API for managing Nepali public entities with PostgreSQL backend.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **PostgreSQL Database**: Robust relational database with advanced features
- **Docker Deployment**: Containerized application with Docker Compose
- **Entity Management**: Create, read, update, and delete Nepali entities
- **Relationship Tracking**: Manage relationships between entities
- **Async Support**: Fully asynchronous API for better performance
- **Database Migrations**: Alembic for database schema management
- **Type Safety**: Pydantic models for request/response validation

## Technology Stack

- **Python**: 3.12+
- **FastAPI**: 0.109.2
- **PostgreSQL**: 16
- **SQLAlchemy**: 2.0.25 (Async)
- **Alembic**: 1.13.1
- **Docker**: Latest
- **Docker Compose**: 3.8

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.12+ (for local development)

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd nepal-entity-service-fastapi
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Start the services:
```bash
docker-compose up -d
```

4. Access the API:
- API: http://localhost:8195
- API Docs: http://localhost:8195/docs
- Health Check: http://localhost:8195/health

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL and update `.env` file

4. Run migrations:
```bash
alembic upgrade head
```

5. Start the API:
```bash
uvicorn app.main:app --reload --port 8195
```

## API Endpoints

### Entities

- `POST /api/v1/entities/` - Create a new entity
- `GET /api/v1/entities/` - List all entities (with filters)
- `GET /api/v1/entities/{entity_id}` - Get a specific entity
- `PUT /api/v1/entities/{entity_id}` - Update an entity
- `DELETE /api/v1/entities/{entity_id}` - Delete an entity

### Relationships

- `POST /api/v1/relationships/` - Create a new relationship
- `GET /api/v1/relationships/` - List all relationships (with filters)
- `GET /api/v1/relationships/{relationship_id}` - Get a specific relationship
- `PUT /api/v1/relationships/{relationship_id}` - Update a relationship
- `DELETE /api/v1/relationships/{relationship_id}` - Delete a relationship

## Database Schema

### Entities Table

- `id`: UUID (Primary Key)
- `name`: String (255)
- `name_nepali`: String (255, Optional)
- `entity_type`: Enum (person, organization, government, political_party, other)
- `description`: Text
- `metadata`: JSONB
- `created_at`: Timestamp
- `updated_at`: Timestamp
- `version`: String

### Relationships Table

- `id`: UUID (Primary Key)
- `source_entity_id`: UUID (Foreign Key)
- `target_entity_id`: UUID (Foreign Key)
- `relationship_type`: String
- `description`: Text
- `metadata`: JSONB
- `created_at`: Timestamp
- `updated_at`: Timestamp

## Configuration

Environment variables can be configured in `.env` file:

```env
POSTGRES_USER=nesuser
POSTGRES_PASSWORD=nespassword
POSTGRES_DB=nepal_entity_db
POSTGRES_PORT=5432

DATABASE_URL=postgresql://nesuser:nespassword@postgres:5432/nepal_entity_db

HOST=0.0.0.0
PORT=8195
LOG_LEVEL=INFO

REDIS_URL=redis://localhost:6379/0
CACHE_EXPIRY=3600
```

## Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild containers
docker-compose up -d --build

# Run database migrations
docker-compose exec api alembic upgrade head

# Access database
docker-compose exec postgres psql -U nesuser -d nepal_entity_db
```

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

## License

Hippocratic License 3.0

## Contributing

Contributions are welcome! Please follow the contribution guidelines in the original [NewNepal-org/NepalEntityService](https://github.com/NewNepal-org/NepalEntityService) repository.
