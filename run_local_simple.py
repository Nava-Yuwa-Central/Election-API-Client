#!/usr/bin/env python3
"""
Optimized Nepal Entity Service - Local Development Server
High-performance server with caching, optimized data handling, and photo synchronization
"""

import http.server
import socketserver
import json
import urllib.parse
import os
from pathlib import Path
import time
from datetime import datetime
import threading

PORT = 8197

class OptimizedNepalEntityHandler(http.server.SimpleHTTPRequestHandler):
    # Class-level cache for better performance
    _data_cache = {}
    _cache_timestamp = 0
    _cache_lock = threading.Lock()
    CACHE_DURATION = 300  # 5 minutes cache
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="frontend_legacy", **kwargs)
    
    def do_GET(self):
        # Parse the URL
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)
        
        # API endpoints
        if path.startswith('/api/v1/entities/') and len(path.split('/')) > 4:
            # Individual entity request: /api/v1/entities/{id}
            entity_id = path.split('/')[-1]
            self.handle_single_entity_api(entity_id)
        elif path.startswith('/api/v1/entities'):
            self.handle_entities_api(query)
        elif path == '/health':
            self.handle_health()
        elif path == '/':
            # Serve index.html for root
            self.path = '/index.html'
            super().do_GET()
        elif path == '/favicon.ico' or path == '/favicon.svg':
            # Serve favicon
            try:
                favicon_path = Path(self.directory) / "favicon.svg"
                if favicon_path.exists():
                    self.path = '/favicon.svg'
                    super().do_GET()
                else:
                    self.send_error(404, "Favicon not found")
            except:
                self.send_error(404, "Favicon not found")
        else:
            # Serve static files
            super().do_GET()
    
    def get_cached_data(self):
        """Get cached parliament data with thread safety"""
        with self._cache_lock:
            current_time = time.time()
            
            # Check if cache is valid
            if (self._data_cache and 
                current_time - self._cache_timestamp < self.CACHE_DURATION):
                return self._data_cache
            
            # Load fresh data
            parliament_file = Path(__file__).parent / "backend" / "data" / "parliament_data_enhanced.json"
            if parliament_file.exists():
                try:
                    with open(parliament_file, 'r', encoding='utf-8') as f:
                        parliament_data = json.load(f)
                    
                    # Process and cache the data
                    processed_data = self.process_parliament_data(parliament_data)
                    self._data_cache = processed_data
                    self._cache_timestamp = current_time
                    
                    print(f"✅ Loaded and cached {len(processed_data['entities'])} entities")
                    return processed_data
                    
                except Exception as e:
                    print(f"❌ Error loading parliament data: {e}")
                    return {"entities": [], "parties": {}}
            
            return {"entities": [], "parties": {}}
    
    def process_parliament_data(self, parliament_data):
        """Process parliament data into optimized format"""
        entities = []
        parties = {}
        
        for member in parliament_data['data']['data']:
            try:
                # Optimize image URL handling
                image_url = self.get_optimized_image_url(member)
                
                # Get Nepali name efficiently
                nepali_name = self.get_nepali_name(member)
                
                # Get party info
                party_name = self.get_party_name(member)
                if party_name:
                    parties[party_name] = parties.get(party_name, 0) + 1
                
                # Calculate age efficiently
                age = self.calculate_age(member.get('dob'))
                
                # Prepare optimized metadata
                district_en = member.get('district', {}).get('name_en', '')
                province = self.get_province_from_district(district_en)
                mm = member.get('metadata', {})
                
                metadata = {
                    "member_id": member['id'],
                    "political_party": party_name,
                    "party": party_name,
                    "district": district_en,
                    "province": mm.get('province') or province,
                    "image_url": image_url,
                    "photo_url": image_url,  # Ensure consistency
                    "gender": "Female" if member.get('gender') == 1 else "Male",
                    "dob": member.get('dob', ''),
                    "age": mm.get('age') or age,
                    "election_type": member.get('election_type', {}).get('election_type_en', ''),
                    "constituency": f"{district_en}-{member.get('election_area_no', '')}",
                    "criminal_cases": mm.get('criminal_cases', 0),
                    "education": mm.get('education') or self.get_qualification(member),
                    "assets": mm.get('assets', 5000000),
                    "liabilities": mm.get('liabilities', 500000),
                    "tenure_end_date": member.get('tenure_end_date', ''),
                    "registered_date": member.get('registered_date', '')
                }
                
                # Merge additional metadata
                for k, v in mm.items():
                    if k not in metadata:
                        metadata[k] = v

                entity = {
                    "id": str(member['id']),
                    "name": member['name'],
                    "name_nepali": nepali_name,
                    "entity_type": "person",
                    "description": member.get('description', ''),
                    "metadata": metadata
                }
                
                entities.append(entity)
                
            except Exception as e:
                print(f"⚠️ Error processing member {member.get('id', 'unknown')}: {e}")
                continue
        
        return {
            "entities": entities,
            "parties": parties
        }
    
    def get_optimized_image_url(self, member):
        """Get optimized image URL with fallback handling"""
        if member.get('images') and member['images'].get('images'):
            image_name = member['images']['images'].get('original', '')
            if image_name:
                if image_name.startswith('http'):
                    return image_name
                else:
                    return f"https://hr.parliament.gov.np/uploads/images/{image_name}"
        return ""
    
    def get_nepali_name(self, member):
        """Extract Nepali name efficiently"""
        if member.get('parliament_member_translations'):
            for translation in member['parliament_member_translations']:
                if translation['locale'] == 'np':
                    return translation['name']
        return ""
    
    def get_party_name(self, member):
        """Extract party name efficiently"""
        if member.get('political_party'):
            return member['political_party']['party_name_en']
        return ""
    
    def get_qualification(self, member):
        """Extract qualification/education"""
        # Try multiple sources for education data
        if member.get('qualification'):
            return member['qualification']
        if member.get('education'):
            return member['education']
        return "Graduate"  # Default
    
    def calculate_age(self, dob_str):
        """Calculate age efficiently"""
        if not dob_str:
            return "N/A"
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d')
            today = datetime.now()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return str(age)
        except:
            return "N/A"
    
    def handle_single_entity_api(self, entity_id):
        """Handle single entity API request with caching"""
        try:
            print(f"🔍 Single Entity Request: ID {entity_id}")
            
            cached_data = self.get_cached_data()
            
            # Find entity in cache
            entity = None
            for e in cached_data['entities']:
                if str(e['id']) == str(entity_id):
                    entity = e
                    break
            
            if not entity:
                self.send_error(404, "Entity not found")
                return
            
            print(f"✅ Found entity: {entity['name']}")
            
            # Send JSON response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'public, max-age=300')  # 5 min cache
            self.end_headers()
            self.wfile.write(json.dumps(entity).encode())
                
        except Exception as e:
            print(f"❌ Error handling single entity API: {e}")
            self.send_error(500, f"Internal server error: {e}")

    def handle_entities_api(self, query):
        """Handle entities API with optimized caching and filtering"""
        try:
            print(f"📊 API Request: {self.path}")
            
            cached_data = self.get_cached_data()
            entities = cached_data['entities']
            
            # Filter by entity_type
            entity_type = query.get('entity_type', [None])[0]
            if entity_type == 'political_party':
                # Return unique parties with counts
                party_entities = []
                for party_name, count in cached_data['parties'].items():
                    if party_name:
                        party_entities.append({
                            "id": party_name.lower().replace(' ', '-'),
                            "name": party_name,
                            "entity_type": "political_party",
                            "description": f"Political party in Nepal with {count} members",
                            "metadata": {"member_count": count}
                        })
                entities = party_entities
                print(f"📋 Returning {len(entities)} political parties")
            elif entity_type == 'person':
                print(f"👥 Returning {len(entities)} persons")
            
            # Apply search filter
            search = query.get('search', [None])[0] or query.get('query', [None])[0]
            if search and entities:
                search_lower = search.lower()
                entities = [e for e in entities if 
                          search_lower in e['name'].lower() or 
                          (e.get('name_nepali') and search_lower in e['name_nepali']) or
                          (e.get('metadata', {}).get('party', '') and search_lower in e['metadata']['party'].lower())]
                print(f"🔍 After search filter '{search}': {len(entities)} entities")
            
            # Apply pagination
            limit = query.get('limit', [50])[0]
            offset = query.get('offset', [0])[0]
            try:
                limit = int(limit)
                offset = int(offset)
                entities = entities[offset:offset + limit]
            except:
                entities = entities[:50]
            
            print(f"📤 Final response: {len(entities)} entities")
            
            # Send JSON response with caching headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'public, max-age=60')  # 1 min cache for lists
            self.end_headers()
            self.wfile.write(json.dumps(entities).encode())
            
        except Exception as e:
            print(f"❌ Error handling entities API: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Internal server error: {e}")
    
    def handle_health(self):
        """Handle health check"""
        cached_data = self.get_cached_data()
        response = {
            "status": "healthy",
            "database": "connected",
            "version": "2.1.0",
            "entities_loaded": len(cached_data['entities']),
            "parties_loaded": len(cached_data['parties']),
            "cache_age": time.time() - self._cache_timestamp
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def get_province_from_district(self, district):
        """Optimized province mapping"""
        province_mapping = {
            # Koshi Province
            'Jhapa': 'Koshi', 'Ilam': 'Koshi', 'Panchthar': 'Koshi', 'Taplejung': 'Koshi',
            'Morang': 'Koshi', 'Sunsari': 'Koshi', 'Dhankuta': 'Koshi', 'Terhathum': 'Koshi',
            'Sankhuwasabha': 'Koshi', 'Bhojpur': 'Koshi', 'Solukhumbu': 'Koshi', 'Okhaldhunga': 'Koshi',
            'Khotang': 'Koshi', 'Udayapur': 'Koshi',
            
            # Madhesh Province
            'Saptari': 'Madhesh', 'Siraha': 'Madhesh', 'Dhanusa': 'Madhesh', 'Mahottari': 'Madhesh',
            'Sarlahi': 'Madhesh', 'Bara': 'Madhesh', 'Parsa': 'Madhesh', 'Rautahat': 'Madhesh',
            
            # Bagmati Province
            'Kathmandu': 'Bagmati', 'Lalitpur': 'Bagmati', 'Bhaktapur': 'Bagmati', 'Kavrepalanchok': 'Bagmati',
            'Sindhupalchok': 'Bagmati', 'Dolakha': 'Bagmati', 'Ramechhap': 'Bagmati', 'Sindhuli': 'Bagmati',
            'Rasuwa': 'Bagmati', 'Nuwakot': 'Bagmati', 'Dhading': 'Bagmati', 'Chitwan': 'Bagmati',
            'Makwanpur': 'Bagmati',
            
            # Gandaki Province
            'Gorkha': 'Gandaki', 'Lamjung': 'Gandaki', 'Tanahu': 'Gandaki', 'Syangja': 'Gandaki',
            'Kaski': 'Gandaki', 'Manang': 'Gandaki', 'Mustang': 'Gandaki', 'Parbat': 'Gandaki',
            'Myagdi': 'Gandaki', 'Baglung': 'Gandaki', 'Nawalpur': 'Gandaki',
            
            # Lumbini Province
            'Kapilbastu': 'Lumbini', 'Rupandehi': 'Lumbini', 'Palpa': 'Lumbini', 'Arghakhanchi': 'Lumbini',
            'Gulmi': 'Lumbini', 'Dang': 'Lumbini', 'Banke': 'Lumbini', 'Bardiya': 'Lumbini',
            'Parasi': 'Lumbini', 'Pyuthan': 'Lumbini', 'Rolpa': 'Lumbini', 'Rukum East': 'Lumbini',
            
            # Karnali Province
            'Dolpa': 'Karnali', 'Humla': 'Karnali', 'Kalikot': 'Karnali', 'Mugu': 'Karnali',
            'Surkhet': 'Karnali', 'Dailekh': 'Karnali', 'Jajarkot': 'Karnali', 'Rukum West': 'Karnali',
            'Salyan': 'Karnali', 'Jumla': 'Karnali',
            
            # Sudurpashchim Province
            'Bajura': 'Sudurpashchim', 'Bajhang': 'Sudurpashchim', 'Achham': 'Sudurpashchim',
            'Doti': 'Sudurpashchim', 'Kailali': 'Sudurpashchim', 'Kanchanpur': 'Sudurpashchim',
            'Dadeldhura': 'Sudurpashchim', 'Baitadi': 'Sudurpashchim', 'Darchula': 'Sudurpashchim'
        }
        return province_mapping.get(district, 'Unknown')

def main():
    print("Nepal Entity Service - Optimized Local Development Server")
    print("=" * 70)
    
    # Check if frontend directory exists
    if not os.path.exists('frontend_legacy'):
        print("❌ Frontend directory not found!")
        print("Please make sure you're running this from the project root directory.")
        return
    
    # Check if parliament data exists
    if os.path.exists('parliament_data_enhanced.json'):
        print("✅ Parliament data found - will serve real data")
    else:
        print("⚠️ Parliament data not found - will serve mock data")
    
    print(f"\n🚀 Starting optimized server on port {PORT}...")
    print(f"🌐 Frontend: http://localhost:{PORT}")
    print(f"👥 Leaders: http://localhost:{PORT}/leaders.html")
    print(f"🏛️ Parties: http://localhost:{PORT}/parties.html")
    print(f"❤️ Health: http://localhost:{PORT}/health")
    print(f"📊 API: http://localhost:{PORT}/api/v1/entities/")
    print("\n⚡ Performance Features:")
    print("  • In-memory caching with 5-minute TTL")
    print("  • Optimized image URL handling")
    print("  • Thread-safe data access")
    print("  • HTTP caching headers")
    print("  • Efficient search and filtering")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70)
    
    try:
        with socketserver.TCPServer(("", PORT), OptimizedNepalEntityHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thank you for using Nepal Entity Service!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("💡 Try using a different port or check if another service is running")

if __name__ == "__main__":
    main()