#!/bin/bash

# Script to import all data from Nepal Entity Service API into local PostgreSQL database
# Usage: ./database/import_all_data.sh [options]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
IMPORT_SCRIPT="$PROJECT_DIR/database/import_entities.py"
MAX_ENTITIES=10000
SKIP_EXISTING=true

# Set PYTHONPATH to include project directory
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check if import script exists
    if [ ! -f "$IMPORT_SCRIPT" ]; then
        log_error "Import script not found: $IMPORT_SCRIPT"
        exit 1
    fi
    
    # Check if virtual environment is activated (optional)
    if [ -z "$VIRTUAL_ENV" ]; then
        log_warning "Virtual environment not activated. Using system Python."
        log_info "Make sure you have installed all dependencies: pip install -r requirements.txt"
    fi
    
    log_success "Dependencies check passed"
}

check_database_connection() {
    log_info "Checking database connection..."
    
    # Try to run a simple Python command to test database connection
    python3 -c "
import sys
sys.path.insert(0, '$PROJECT_DIR')
try:
    from app.core.database import AsyncSessionLocal
    from app.core.config import settings
    import asyncio
    from sqlalchemy import text
    
    async def test_connection():
        async with AsyncSessionLocal() as session:
            await session.execute(text('SELECT 1'))
    
    asyncio.run(test_connection())
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
" || {
        log_error "Cannot connect to database. Make sure:"
        log_error "  1. PostgreSQL is running (docker-compose up -d postgres)"
        log_error "  2. DATABASE_URL is set correctly in .env file"
        exit 1
    }
    
    log_success "Database connection successful"
}

import_entity_type() {
    local entity_type=$1
    local description=$2
    
    log_info "Importing $description..."
    
    # Run with PYTHONPATH set
    if PYTHONPATH="$PROJECT_DIR:$PYTHONPATH" python3 "$IMPORT_SCRIPT" --type "$entity_type" --all --limit "$MAX_ENTITIES"; then
        log_success "Completed importing $description"
        return 0
    else
        log_error "Failed to import $description"
        return 1
    fi
}

import_by_query() {
    local query=$1
    local description=$2
    
    log_info "Importing $description (query: $query)..."
    
    if PYTHONPATH="$PROJECT_DIR:$PYTHONPATH" python3 "$IMPORT_SCRIPT" --query "$query" --all --limit "$MAX_ENTITIES"; then
        log_success "Completed importing $description"
        return 0
    else
        log_error "Failed to import $description"
        return 1
    fi
}

show_summary() {
    log_info "Generating import summary..."
    
    PYTHONPATH="$PROJECT_DIR:$PYTHONPATH" python3 -c "
import sys
sys.path.insert(0, '$PROJECT_DIR')
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.entity import Entity, EntityType
from sqlalchemy import select, func

async def get_summary():
    async with AsyncSessionLocal() as session:
        # Total entities
        result = await session.execute(select(func.count(Entity.id)))
        total = result.scalar()
        
        # By type
        result = await session.execute(
            select(Entity.entity_type, func.count(Entity.id))
            .group_by(Entity.entity_type)
        )
        by_type = result.all()
        
        print(f'\n📊 Import Summary:')
        print(f'   Total Entities: {total}')
        print(f'\n   By Type:')
        for entity_type, count in by_type:
            print(f'     - {entity_type.value}: {count}')

asyncio.run(get_summary())
" || log_warning "Could not generate summary"
}

# Main execution
main() {
    log_info "=========================================="
    log_info "Nepal Entity Service - Data Import Script"
    log_info "=========================================="
    echo ""
    
    # Change to project directory
    cd "$PROJECT_DIR" || exit 1
    
    # Check dependencies
    check_dependencies
    echo ""
    
    # Check database connection
    check_database_connection
    echo ""
    
    # Parse command line arguments
    IMPORT_PERSONS=true
    IMPORT_ORGANIZATIONS=true
    IMPORT_LOCATIONS=true
    IMPORT_POLITICAL_PARTIES=true
    SKIP_EXISTING=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --persons-only)
                IMPORT_ORGANIZATIONS=false
                IMPORT_LOCATIONS=false
                IMPORT_POLITICAL_PARTIES=false
                shift
                ;;
            --organizations-only)
                IMPORT_PERSONS=false
                IMPORT_LOCATIONS=false
                IMPORT_POLITICAL_PARTIES=false
                shift
                ;;
            --political-parties-only)
                IMPORT_PERSONS=false
                IMPORT_ORGANIZATIONS=false
                IMPORT_LOCATIONS=false
                shift
                ;;
            --no-skip-existing)
                SKIP_EXISTING=false
                shift
                ;;
            --max-entities)
                MAX_ENTITIES="$2"
                shift 2
                ;;
            --help|-h)
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --persons-only              Import only persons"
                echo "  --organizations-only        Import only organizations"
                echo "  --political-parties-only    Import only political parties"
                echo "  --no-skip-existing          Re-import existing entities"
                echo "  --max-entities N            Maximum entities to import (default: 10000)"
                echo "  --help, -h                  Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Start import process
    log_info "Starting data import process..."
    log_info "Max entities per type: $MAX_ENTITIES"
    log_info "Skip existing: $SKIP_EXISTING"
    echo ""
    
    local total_imported=0
    local total_failed=0
    
    # Import persons
    if [ "$IMPORT_PERSONS" = true ]; then
        if import_entity_type "person" "Persons"; then
            ((total_imported++))
        else
            ((total_failed++))
        fi
        echo ""
    fi
    
    # Import organizations
    if [ "$IMPORT_ORGANIZATIONS" = true ]; then
        if import_entity_type "organization" "Organizations"; then
            ((total_imported++))
        else
            ((total_failed++))
        fi
        echo ""
    fi
    
    # Import political parties (as a subset of organizations)
    if [ "$IMPORT_POLITICAL_PARTIES" = true ]; then
        log_info "Importing Political Parties..."
        if PYTHONPATH="$PROJECT_DIR:$PYTHONPATH" python3 "$IMPORT_SCRIPT" --type "organization" --query "political_party" --all --limit "$MAX_ENTITIES"; then
            log_success "Completed importing Political Parties"
            ((total_imported++))
        else
            log_error "Failed to import Political Parties"
            ((total_failed++))
        fi
        echo ""
    fi
    
    # Import locations
    if [ "$IMPORT_LOCATIONS" = true ]; then
        if import_entity_type "location" "Locations"; then
            ((total_imported++))
        else
            ((total_failed++))
        fi
        echo ""
    fi
    
    # Show summary
    echo ""
    log_info "=========================================="
    log_info "Import Process Complete"
    log_info "=========================================="
    log_success "Successfully imported: $total_imported entity type(s)"
    if [ $total_failed -gt 0 ]; then
        log_warning "Failed imports: $total_failed entity type(s)"
    fi
    echo ""
    
    show_summary
    echo ""
    
    log_success "Data import completed! 🎉"
}

# Run main function
main "$@"