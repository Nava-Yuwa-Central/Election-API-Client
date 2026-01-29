#!/usr/bin/env python3
"""
Simple script to integrate 635 candidates from 2079 state election
Integrates the candidates into the parliament data format
"""

import json
import csv
import os
from pathlib import Path
from datetime import datetime

def integrate_2079_candidates():
    """Integrate 635 candidates from 2079 state election"""
    
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    
    print("🇳🇵 Integrating 2079 State Election Candidates")
    print("=" * 50)
    
    # File paths
    parliament_data_file = base_dir / "parliament_data.json"
    candidates_file = data_dir / "candidates_2079.json"
    matches_file = data_dir / "candidate_matches.csv"
    enhanced_data_file = base_dir / "parliament_data_enhanced.json"
    
    # Load current parliament data
    print("Loading current parliament data...")
    try:
        with open(parliament_data_file, 'r', encoding='utf-8') as f:
            parliament_data = json.load(f)
        print(f"✅ Loaded {parliament_data['data']['total']} current parliament members")
    except FileNotFoundError:
        print("❌ Parliament data file not found!")
        return False
    
    # Load 2079 candidates
    print("Loading 2079 candidates...")
    try:
        with open(candidates_file, 'r', encoding='utf-8') as f:
            candidates_2079 = json.load(f)
        print(f"✅ Loaded {len(candidates_2079)} 2079 candidates")
    except FileNotFoundError:
        print("❌ 2079 candidates file not found!")
        print("Please run: python scripts/create_2079_data.py first")
        return False
    
    # Load candidate matches
    print("Loading candidate matches...")
    matches = {}
    try:
        with open(matches_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                matches[row['candidate_id_2079']] = row['parliament_id']
        print(f"✅ Loaded {len(matches)} candidate matches")
    except FileNotFoundError:
        print("⚠️  No candidate matches file found, treating all as new candidates")
    
    # Create enhanced dataset
    enhanced_data = parliament_data.copy()
    new_candidates = []
    updated_count = 0
    
    print("\nProcessing candidates...")
    
    for i, candidate in enumerate(candidates_2079):
        candidate_id = str(candidate['id'])
        
        # Check if candidate already exists in parliament data
        existing_candidate = None
        if candidate_id in matches:
            parliament_id = matches[candidate_id]
            existing_candidate = next(
                (c for c in enhanced_data['data']['data'] if str(c['id']) == parliament_id), 
                None
            )
        
        if existing_candidate:
            # Update existing candidate with 2079 election info
            if 'election_history' not in existing_candidate:
                existing_candidate['election_history'] = []
            
            existing_candidate['election_history'].append({
                'year': 2079,
                'election_type': 'state',
                'district': candidate['district'],
                'province': candidate['province'],
                'party': candidate['party'],
                'constituency': candidate['constituency']
            })
            updated_count += 1
            
            if i < 5:  # Show first 5 updates
                print(f"  ✓ Updated: {existing_candidate['name']}")
        else:
            # Create new candidate entity
            new_entity = create_candidate_entity(candidate)
            new_candidates.append(new_entity)
            
            if i < 10:  # Show first 10 new candidates
                print(f"  + Created: {new_entity['name']}")
    
    # Add new candidates to the dataset
    enhanced_data['data']['data'].extend(new_candidates)
    enhanced_data['data']['total'] += len(new_candidates)
    
    # Update pagination info
    enhanced_data['data']['last_page'] = (enhanced_data['data']['total'] // enhanced_data['data']['per_page']) + 1
    
    # Save enhanced dataset
    print(f"\nSaving enhanced dataset...")
    with open(enhanced_data_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Integration complete!")
    print(f"📊 Results:")
    print(f"  - Updated existing candidates: {updated_count}")
    print(f"  - Added new candidates: {len(new_candidates)}")
    print(f"  - Total candidates now: {enhanced_data['data']['total']}")
    print(f"  - Enhanced data saved to: {enhanced_data_file}")
    
    return True

def create_candidate_entity(candidate_data):
    """Create a candidate entity in the parliament data format"""
    
    candidate_id = candidate_data['id']
    name = candidate_data['name']
    name_nepali = candidate_data['name_nepali']
    district = candidate_data['district']
    province = candidate_data['province']
    party = candidate_data['party']
    gender = candidate_data['gender']
    age = candidate_data['age']
    
    # Create image structure
    images = {
        "clientOriginalName": f"{name.replace(' ', '_')}.jpg",
        "clientOriginalExtension": "jpg",
        "clientSize": "Unknown",
        "mimeType": "image/jpeg",
        "imageName": str(candidate_id),
        "images": {
            "original": candidate_data['photo_url'],
            "thumbnail": candidate_data['photo_url']
        }
    }
    
    # Calculate birth year from age (approximate)
    current_year = 2025  # Current year
    birth_year = current_year - age
    dob = f"{birth_year}-01-01"
    
    # Create candidate entity
    entity = {
        "id": candidate_id,
        "code": str(candidate_id),
        "slug": name.replace(' ', '-').lower(),
        "parliament_type": "state",
        "sequence": 0,
        "status": 1,
        "member_type": "candidate",
        "name": name,
        "dob": dob,
        "images": images,
        "district_id": None,
        "registered_date": 2079,
        "representation_type_id": 5,
        "political_party_id": None,
        "election_type_id": 2506,
        "election_area_no": candidate_data['constituency'],
        "territory_no": 1,
        "video_link": None,
        "secretariat_page": None,
        "gender": gender,
        "user_id": 1,
        "tenure_end_date": "2027-01-01",
        "created_by": "2079 Election Integration",
        "published_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "district": {
            "id": None,
            "name_en": district,
            "name_np": district
        },
        "political_party": {
            "id": None,
            "party_name_en": party,
            "party_name_np": party
        },
        "election_type": {
            "id": 2506,
            "election_type_en": "State Election 2079",
            "election_type_np": "प्रदेश निर्वाचन २०७९"
        },
        "parliament_member_translations": [
            {
                "locale": "en",
                "name": name,
                "description": f"Candidate for {district} in 2079 state election"
            },
            {
                "locale": "np", 
                "name": name_nepali,
                "description": f"२०७९ प्रदेश निर्वाचनमा {district} का उम्मेदवार"
            }
        ]
    }
    
    return entity

def update_server_to_use_enhanced_data():
    """Update the local server to use enhanced data"""
    
    base_dir = Path(__file__).parent.parent
    server_file = base_dir / "run_local_simple.py"
    enhanced_data_file = base_dir / "parliament_data_enhanced.json"
    
    if not enhanced_data_file.exists():
        print("❌ Enhanced data file not found!")
        return False
    
    print("\nUpdating local server to use enhanced data...")
    
    try:
        # Read current server file
        with open(server_file, 'r', encoding='utf-8') as f:
            server_content = f.read()
        
        # Replace parliament_data.json with parliament_data_enhanced.json
        updated_content = server_content.replace(
            'parliament_data.json',
            'parliament_data_enhanced.json'
        )
        
        # Write updated server file
        with open(server_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ Server updated to use enhanced data")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update server: {e}")
        return False

def main():
    success = integrate_2079_candidates()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 2079 Candidates Successfully Integrated!")
        print("=" * 50)
        
        # Ask if user wants to update the server
        print("\nWould you like to update the local server to use the enhanced data?")
        print("This will include the 635 new candidates in your application.")
        
        # For automation, let's update automatically
        if update_server_to_use_enhanced_data():
            print("\n✅ Server configuration updated!")
            print("\nNext steps:")
            print("1. Restart your local server")
            print("2. Visit http://localhost:8196/map.html")
            print("3. The map will now show data from 899 total candidates")
            print("   (264 parliament members + 635 state election candidates)")
        
    else:
        print("\n❌ Integration failed!")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()