# Nepal Entity Service - FastAPI

🇳🇵 **Who's My Neta Nepal** - Open Source, open data, and open API for managing Nepali public entities with comprehensive parliament member data and beautiful frontend.

## ✨ Features

- **Complete Parliament Data**: All 264+ parliament members with photos, party affiliations, and detailed information
- **Beautiful Frontend**: Modern, responsive web interface with search, filtering, and interactive displays
- **FastAPI Backend**: Modern, fast web framework for building APIs
- **PostgreSQL Database**: Robust relational database with advanced features
- **Docker Deployment**: Containerized application with Docker Compose
- **Entity Management**: Create, read, update, and delete Nepali entities
- **Relationship Tracking**: Manage relationships between entities
- **Async Support**: Fully asynchronous API for better performance
- **Database Migrations**: Alembic for database schema management
- **Type Safety**: Pydantic models for request/response validation
- **Real Images**: Parliament member photos from official sources

## 🚀 Quick Start

### Prerequisites

- **Docker and Docker Compose** (Recommended - easiest setup)
- **Python 3.12+** (for local development)
- **Git** (to clone the repository)

### Option 1: One-Click Setup (Windows)

1. **Clone the repository:**
```bash
git clone <repository-url>
cd nepal-entity-service-fastapi
```

2. **Run the setup script:**
```powershell
# PowerShell (Recommended)
.\setup.ps1

# Or Command Prompt
run_setup.bat
```

3. **Access the application:**
- **Main App**: http://localhost:8195
- **API Docs**: http://localhost:8195/docs
- **Leaders Page**: http://localhost:8195/leaders.html
- **Parties Page**: http://localhost:8195/parties.html

### Option 2: Manual Docker Setup

1. **Clone and setup:**
```bash
git clone <repository-url>
cd nepal-entity-service-fastapi
cp .env.example .env
```

2. **Start services:**
```bash
docker compose up -d
```

3. **Load parliament data:**
```bash
# Wait for services to start (about 30 seconds)
python scripts/comprehensive_seed_data.py
```

4. **Test the setup:**
```bash
python test_api_endpoints.py
```

### Option 3: Local Development

1. **Setup Python environment:**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Setup PostgreSQL** and update `.env` with your database URL

4. **Run migrations:**
```bash
alembic upgrade head
```

5. **Load data:**
```bash
python scripts/comprehensive_seed_data.py
```

6. **Start the server:**
```bash
uvicorn app.main:app --reload --port 8195
```

## 📊 What's Included

### Parliament Data
- **264+ Parliament Members** with official photos
- **Political Party Information** with member counts
- **District and Province** mapping
- **Biographical Information** including Nepali names
- **Electoral Details** including constituency information

### Frontend Features
- **Interactive Leaders Table** with sorting and filtering
- **Party Overview Page** with member counts
- **Search Functionality** with autocomplete
- **Responsive Design** works on all devices
- **Real Member Photos** from parliament.gov.np
- **Bilingual Support** (English and Nepali names)

### API Endpoints

#### Entities
- `GET /api/v1/entities/` - List all entities with filtering
- `GET /api/v1/entities/{id}` - Get specific entity
- `POST /api/v1/entities/` - Create new entity
- `PUT /api/v1/entities/{id}` - Update entity
- `DELETE /api/v1/entities/{id}` - Delete entity

#### Query Parameters
- `entity_type=person` - Filter by person entities (leaders)
- `entity_type=political_party` - Filter by political parties
- `search=query` - Search by name
- `limit=50` - Limit results
- `offset=0` - Pagination offset

### Database Schema

#### Entities Table
- `id`: UUID (Primary Key)
- `name`: String (255) - English name
- `name_nepali`: String (255) - Nepali name
- `entity_type`: Enum (person, organization, government, political_party, other)
- `description`: Text
- `metadata`: JSONB - Flexible data storage
- `created_at`: Timestamp
- `updated_at`: Timestamp

#### Metadata Fields (for Parliament Members)
```json
{
  "member_id": "Parliament member ID",
  "political_party": "Party name in English",
  "political_party_nepali": "Party name in Nepali",
  "district": "District name",
  "province": "Province name",
  "image_url": "Official photo URL",
  "gender": "0=male, 1=female",
  "election_type": "Direct/Indirect",
  "constituency": "Electoral constituency"
}
```

## 🛠️ Configuration

Environment variables in `.env` file:

```env
# Database
POSTGRES_USER=nesuser
POSTGRES_PASSWORD=nespassword123
POSTGRES_DB=nepal_entity_db
DATABASE_URL=postgresql://nesuser:nespassword123@localhost:5432/nepal_entity_db

# Server
HOST=0.0.0.0
PORT=8195
ENVIRONMENT=development
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-here
REQUIRE_AUTHENTICATION=false

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8195"]
```

## 🐳 Docker Commands

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Rebuild containers
docker compose up -d --build

# Access database
docker compose exec postgres psql -U nesuser -d nepal_entity_db

# Run migrations in container
docker compose exec api alembic upgrade head
```

## 📱 Frontend Pages

### Home Page (`/`)
- Hero section with search
- Statistics overview
- Featured leaders
- Quick navigation

### Leaders Page (`/leaders.html`)
- Complete parliament members table
- Advanced filtering (party, province, education)
- Sorting by various fields
- Search functionality
- Pagination

### Parties Page (`/parties.html`)
- All political parties with member counts
- Party logos and information
- Click to filter leaders by party

### Map Page (`/map.html`)
- Interactive Nepal map (coming soon)
- Province-wise leader distribution

## 🔧 Development

### Adding New Data
```python
# Add new parliament member
python scripts/add_member.py --name "Member Name" --party "Party Name"

# Update existing data
python scripts/update_data.py
```

### API Testing
```bash
# Test all endpoints
python test_api_endpoints.py

# Manual API testing
curl http://localhost:8195/api/v1/entities/?entity_type=person&limit=5
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🎨 Customization

### Adding New Entity Types
1. Update `EntityType` enum in `app/models/entity.py`
2. Create migration: `alembic revision --autogenerate -m "Add new entity type"`
3. Update frontend filters and displays

### Styling
- Main styles: `frontend/styles/main.css`
- Components: `frontend/styles/components.css`
- Animations: `frontend/styles/animations.css`

### Adding New Pages
1. Create HTML file in `frontend/`
2. Add route in `app/main.py`
3. Update navigation in existing pages

## 🚨 Troubleshooting

### Common Issues

**Docker services won't start:**
```bash
# Check Docker is running
docker --version

# Check ports are free
netstat -an | findstr :8195
netstat -an | findstr :5432
```

**Database connection errors:**
```bash
# Check database is running
docker compose ps

# Reset database
docker compose down -v
docker compose up -d
```

**Python/API errors:**
```bash
# Check logs
docker compose logs api

# Restart API service
docker compose restart api
```

**Frontend not loading:**
- Check if API is running: http://localhost:8195/health
- Clear browser cache
- Check browser console for errors

### Performance Tips
- Use pagination for large datasets
- Enable database indexing for search fields
- Use Redis caching for frequently accessed data
- Optimize images for faster loading

## 📄 License

Hippocratic License 3.0 - See LICENSE file

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📞 Support

- **Issues**: Create GitHub issue
- **Documentation**: Check `/docs` endpoint when running
- **API Reference**: Visit `/docs` when server is running

---

**Made with ❤️ for transparency in Nepali politics**
