import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime

# --- Constants & Config ---
APP_VERSION = "2.2.0-pro"
DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "parliament_data_enhanced.json"
LEGACY_FRONTEND_DIR = Path(__file__).parents[1] / "frontend_legacy"

# --- Models & Schemas ---
class EntityMetadata(BaseModel):
    member_id: int
    political_party: Optional[str] = None
    party: Optional[str] = None
    district: Optional[str] = None
    province: Optional[str] = None
    image_url: Optional[str] = ""
    photo_url: Optional[str] = ""
    gender: Optional[str] = "Male"
    dob: Optional[str] = ""
    age: Optional[str] = "N/A"
    election_type: Optional[str] = ""
    constituency: Optional[str] = ""
    criminal_cases: int = 0
    education: str = "Graduate"
    assets: int = 5000000
    liabilities: int = 500000
    tenure_end_date: Optional[str] = ""
    registered_date: Optional[str] = ""

class Entity(BaseModel):
    id: str
    name: str
    name_nepali: str = ""
    entity_type: str = "person"
    description: str = ""
    metadata: Dict[str, Any]

class HealthStatus(BaseModel):
    status: str
    version: str
    database: str
    entities_count: int
    parties_count: int
    uptime_seconds: float

# --- State Management ---
class AppState:
    def __init__(self):
        self.data_cache = {"entities": [], "parties": {}}
        self.last_load = 0
        self.start_time = time.time()

    def load_data(self):
        if not DATA_FILE.exists():
            return {"entities": [], "parties": {}}
        
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            entities = []
            parties = {}
            
            for member in raw_data.get('data', {}).get('data', []):
                # Process member data (simplified version of legacy logic)
                m_id = str(member['id'])
                party_name = member.get('political_party', {}).get('party_name_en', '')
                if party_name:
                    parties[party_name] = parties.get(party_name, 0) + 1
                
                # Image handling
                image_url = ""
                if member.get('images', {}).get('images', {}).get('original'):
                    image_name = member['images']['images']['original']
                    image_url = image_name if image_name.startswith('http') else f"https://hr.parliament.gov.np/uploads/images/{image_name}"

                # Nepali name
                nep_name = ""
                for trans in member.get('parliament_member_translations', []):
                    if trans['locale'] == 'np':
                        nep_name = trans['name']
                
                # Metadata
                district = member.get('district', {}).get('name_en', '')
                
                entities.append({
                    "id": m_id,
                    "name": member['name'],
                    "name_nepali": nep_name,
                    "entity_type": "person",
                    "description": member.get('description', ''),
                    "metadata": {
                        "member_id": member['id'],
                        "party": party_name,
                        "district": district,
                        "image_url": image_url,
                        "photo_url": image_url,
                        "gender": "Female" if member.get('gender') == 1 else "Male",
                        "age": member.get('metadata', {}).get('age', "N/A"),
                        "criminal_cases": member.get('metadata', {}).get('criminal_cases', 0)
                    }
                })
            
            self.data_cache = {"entities": entities, "parties": parties}
            self.last_load = time.time()
            print(f"[OK] Loaded {len(entities)} entities from {DATA_FILE}")
            
        except Exception as e:
            print(f"[X] Error loading data: {e}")
            
    def get_data(self):
        if not self.data_cache["entities"] or (time.time() - self.last_load > 600):
            self.load_data()
        return self.data_cache

state = AppState()

# --- App Definition ---
app = FastAPI(
    title="Nepal Entity Service PRO",
    description="Professional backend for Nepal election and entity data",
    version=APP_VERSION
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---
@app.get("/health", response_model=HealthStatus)
def health():
    data = state.get_data()
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "database": "connected",
        "entities_count": len(data["entities"]),
        "parties_count": len(data["parties"]),
        "uptime_seconds": time.time() - state.start_time
    }

@app.get("/api/v1/entities")
def get_entities(
    entity_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    data = state.get_data()
    entities = data["entities"]
    
    if entity_type == 'political_party':
        party_entities = []
        for party_name, count in data['parties'].items():
            party_entities.append({
                "id": party_name.lower().replace(' ', '-'),
                "name": party_name,
                "entity_type": "political_party",
                "description": f"Political party in Nepal with {count} members",
                "metadata": {"member_count": count}
            })
        entities = party_entities
    
    if search:
        search_lower = search.lower()
        entities = [
            e for e in entities 
            if search_lower in e['name'].lower() or 
               search_lower in e.get('name_nepali', '').lower() or
               search_lower in e.get('metadata', {}).get('party', '').lower()
        ]
        
    return entities[offset : offset + limit]

@app.get("/api/v1/entities/{entity_id}")
def get_entity(entity_id: str):
    data = state.get_data()
    for e in data["entities"]:
        if e["id"] == entity_id:
            return e
    raise HTTPException(status_code=404, detail="Entity not found")

# --- Static Files (MUST BE LAST) ---
if LEGACY_FRONTEND_DIR.exists():
    # Serve index.html explicitly for the root
    @app.get("/")
    async def serve_index():
        from fastapi.responses import FileResponse
        return FileResponse(LEGACY_FRONTEND_DIR / "index.html")
    
    # Mount everything else
    app.mount("/", StaticFiles(directory=str(LEGACY_FRONTEND_DIR)), name="static")

if __name__ == "__main__":
    import uvicorn
    # Pre-load data
    state.load_data()
    uvicorn.run(app, host="0.0.0.0", port=8197)
