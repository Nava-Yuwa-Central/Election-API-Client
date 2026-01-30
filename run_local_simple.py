#!/usr/bin/env python3
"""
Simple local server to run the Nepal Entity Service frontend
This serves the frontend and provides mock API data for development
"""

import http.server
import socketserver
import json
import urllib.parse
import os
from pathlib import Path

PORT = 8196

class NepalEntityHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="frontend", **kwargs)
    
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
    
    def handle_single_entity_api(self, entity_id):
        """Handle single entity API request"""
        try:
            print(f"Single Entity Request: ID {entity_id}")
            
            # Load parliament data
            parliament_file = Path(__file__).parent / "parliament_data_enhanced.json"
            if parliament_file.exists():
                with open(parliament_file, 'r', encoding='utf-8') as f:
                    parliament_data = json.load(f)
                
                # Find the member by ID
                member = None
                for m in parliament_data['data']['data']:
                    if str(m['id']) == str(entity_id):
                        member = m
                        break
                
                if not member:
                    self.send_error(404, "Entity not found")
                    return
                
                # Get image URL
                image_url = ""
                if member.get('images') and member['images'].get('images'):
                    image_name = member['images']['images'].get('original', '')
                    if image_name:
                        if image_name.startswith('http'):
                            image_url = image_name
                        else:
                            image_url = f"https://hr.parliament.gov.np/uploads/images/{image_name}"
                
                # Get Nepali name
                nepali_name = ""
                if member.get('parliament_member_translations'):
                    for translation in member['parliament_member_translations']:
                        if translation['locale'] == 'np':
                            nepali_name = translation['name']
                            break
                
                # Get party info
                party_name = ""
                if member.get('political_party'):
                    party_name = member['political_party']['party_name_en']
                
                # Calculate age from DOB if available
                age = "N/A"
                if member.get('dob'):
                    try:
                        from datetime import datetime
                        dob = datetime.strptime(member['dob'], '%Y-%m-%d')
                        today = datetime.now()
                        age = str(today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day)))
                    except:
                        age = "N/A"
                
                entity = {
                    "id": str(member['id']),
                    "name": member['name'],
                    "name_nepali": nepali_name,
                    "entity_type": "person",
                    "description": member.get('description', ''),
                    "metadata": {
                        "member_id": member['id'],
                        "political_party": party_name,
                        "party": party_name,
                        "district": member.get('district', {}).get('name_en', ''),
                        "province": self.get_province_from_district(member.get('district', {}).get('name_en', '')),
                        "image_url": image_url,
                        "photo_url": image_url,  # Alias for compatibility
                        "gender": "Female" if member.get('gender') == 1 else "Male",
                        "dob": member.get('dob', ''),
                        "age": age,
                        "election_type": member.get('election_type', {}).get('election_type_en', ''),
                        "constituency": f"{member.get('district', {}).get('name_en', '')}-{member.get('election_area_no', '')}",
                        "criminal_cases": 0,  # Mock data
                        "education": "Graduate",  # Mock data
                        "assets": 5000000,  # Mock data
                        "liabilities": 500000,  # Mock data
                        "tenure_end_date": member.get('tenure_end_date', ''),
                        "registered_date": member.get('registered_date', '')
                    }
                }
                
                print(f"Found entity: {entity['name']} with image: {image_url}")
                
                # Send JSON response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(entity).encode())
                
            else:
                self.send_error(404, "Data file not found")
                
        except Exception as e:
            print(f"Error handling single entity API: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Internal server error: {e}")

    def handle_entities_api(self, query):
        """Handle entities API with mock data from parliament_data_enhanced.json"""
        try:
            print(f"API Request: {self.path}")
            print(f"Query params: {query}")
            
            # Load parliament data
            parliament_file = Path(__file__).parent / "parliament_data_enhanced.json"
            if parliament_file.exists():
                with open(parliament_file, 'r', encoding='utf-8') as f:
                    parliament_data = json.load(f)
                
                entities = []
                
                # Convert parliament members to entities
                for member in parliament_data['data']['data']:
                    # Get image URL
                    image_url = ""
                    if member.get('images') and member['images'].get('images'):
                        image_name = member['images']['images'].get('original', '')
                        if image_name:
                            if image_name.startswith('http'):
                                image_url = image_name
                            else:
                                image_url = f"https://hr.parliament.gov.np/uploads/images/{image_name}"
                    
                    # Get Nepali name
                    nepali_name = ""
                    if member.get('parliament_member_translations'):
                        for translation in member['parliament_member_translations']:
                            if translation['locale'] == 'np':
                                nepali_name = translation['name']
                                break
                    
                    # Get party info
                    party_name = ""
                    if member.get('political_party'):
                        party_name = member['political_party']['party_name_en']
                    
                    entity = {
                        "id": str(member['id']),
                        "name": member['name'],
                        "name_nepali": nepali_name,
                        "entity_type": "person",
                        "description": member.get('description', ''),
                        "metadata": {
                            "member_id": member['id'],
                            "political_party": party_name,
                            "party": party_name,  # Alias for compatibility
                            "district": member.get('district', {}).get('name_en', ''),
                            "province": self.get_province_from_district(member.get('district', {}).get('name_en', '')),
                            "image_url": image_url,
                            "gender": member.get('gender'),
                            "election_type": member.get('election_type', {}).get('election_type_en', ''),
                            "constituency": f"{member.get('district', {}).get('name_en', '')}-{member.get('election_area_no', '')}",
                            "criminal_cases": 0,  # Mock data
                            "education": "Graduate",  # Mock data
                            "assets": 5000000,  # Mock data
                            "liabilities": 500000,  # Mock data
                            "age": "45"  # Mock data
                        }
                    }
                    entities.append(entity)
                
                print(f"Loaded {len(entities)} parliament members")
                
                # Filter by entity_type if specified
                entity_type = query.get('entity_type', [None])[0]
                if entity_type == 'political_party':
                    # Return unique parties
                    parties = {}
                    for entity in entities:
                        party = entity['metadata'].get('political_party')
                        if party and party not in parties:
                            parties[party] = {
                                "id": party.lower().replace(' ', '-'),
                                "name": party,
                                "entity_type": "political_party",
                                "description": f"Political party in Nepal",
                                "metadata": {}
                            }
                    entities = list(parties.values())
                    print(f"Returning {len(entities)} political parties")
                elif entity_type == 'person':
                    # Already filtered to persons
                    print(f"Returning {len(entities)} persons")
                
                # Apply search filter
                search = query.get('search', [None])[0] or query.get('query', [None])[0]
                if search:
                    search_lower = search.lower()
                    entities = [e for e in entities if 
                              search_lower in e['name'].lower() or 
                              (e.get('name_nepali') and search_lower in e['name_nepali'])]
                    print(f"After search filter: {len(entities)} entities")
                
                # Apply limit
                limit = query.get('limit', [50])[0]
                try:
                    limit = int(limit)
                    entities = entities[:limit]
                except:
                    entities = entities[:50]
                
                response = entities  # Return array directly, not wrapped in data object
                print(f"Final response: {len(response)} entities")
                
            else:
                print("Parliament data file not found, using fallback")
                # Fallback mock data
                response = [
                    {
                        "id": "1",
                        "name": "Sample Leader",
                        "name_nepali": "नमूना नेता",
                        "entity_type": "person",
                        "description": "Sample parliament member",
                        "metadata": {
                            "political_party": "Sample Party",
                            "district": "Kathmandu",
                            "province": "Bagmati",
                            "image_url": "assets/placeholder.jpg"
                        }
                    }
                ]
            
            # Send JSON response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Error handling entities API: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Internal server error: {e}")
    
    def handle_health(self):
        """Handle health check"""
        response = {
            "status": "healthy",
            "database": "connected",
            "version": "2.0.0"
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def get_province_from_district(self, district):
        """Map district to province"""
        province_mapping = {
            'Kathmandu': 'Bagmati', 'Lalitpur': 'Bagmati', 'Bhaktapur': 'Bagmati',
            'Morang': 'Koshi', 'Jhapa': 'Koshi', 'Sunsari': 'Koshi',
            'Saptari': 'Madhesh', 'Siraha': 'Madhesh', 'Dhanusa': 'Madhesh',
            'Kaski': 'Gandaki', 'Syangja': 'Gandaki', 'Parbat': 'Gandaki',
            'Rupandehi': 'Lumbini', 'Kapilbastu': 'Lumbini', 'Nawalpur': 'Lumbini',
            'Surkhet': 'Karnali', 'Dailekh': 'Karnali', 'Jajarkot': 'Karnali',
            'Kailali': 'Sudurpashchim', 'Kanchanpur': 'Sudurpashchim', 'Doti': 'Sudurpashchim'
        }
        return province_mapping.get(district, 'Unknown')

def main():
    print("Nepal Entity Service - Local Development Server")
    print("=" * 60)
    
    # Check if frontend directory exists
    if not os.path.exists('frontend'):
        print("X Frontend directory not found!")
        print("Please make sure you're running this from the project root directory.")
        return
    
    # Check if parliament data exists
    if os.path.exists('parliament_data_enhanced.json'):
        print("V Parliament data found - will serve real data")
    else:
        print("! Parliament data not found - will serve mock data")
    
    print(f"\nStarting server on port {PORT}...")
    print(f"Frontend: http://localhost:{PORT}")
    print(f"Leaders: http://localhost:{PORT}/leaders.html")
    print(f"Parties: http://localhost:{PORT}/parties.html")
    print(f"API Health: http://localhost:{PORT}/health")
    print(f"API Entities: http://localhost:{PORT}/api/v1/entities/")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        with socketserver.TCPServer(("", PORT), NepalEntityHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thank you for using Nepal Entity Service!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("💡 Try using a different port or check if another service is running on port 8195")

if __name__ == "__main__":
    main()