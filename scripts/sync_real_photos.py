import json
import urllib.request
import csv
from pathlib import Path
import re

def clean_name(name):
    if not name:
        return ""
    # Remove all whitespace and non-word characters for fuzzy matching
    return re.sub(r'\s+', '', name)

def sync_real_photos():
    base_dir = Path(__file__).parent.parent
    parliament_data_file = base_dir / "parliament_data.json"
    enhanced_data_file = base_dir / "parliament_data_enhanced.json"
    
    github_json_url = "https://raw.githubusercontent.com/NewNepal-org/NepalEntityService/2082-pr-list/migrations/010-source-2082-direct-candidates/data/DirectElectionResultCentral2082.json"
    
    print("Syncing Real Photo URLs from PR #71...")
    
    # Load current parliament data
    try:
        with open(parliament_data_file, 'r', encoding='utf-8') as f:
            parliament_data = json.load(f)
        print(f"Loaded {len(parliament_data['data']['data'])} parliament members")
    except Exception as e:
        print(f"Error loading parliament_data.json: {e}")
        return
        
    # Fetch real data from GitHub
    print(f"Fetching real data from GitHub...")
    try:
        with urllib.request.urlopen(github_json_url) as response:
            content = response.read().decode('utf-8-sig')
            real_candidates = json.loads(content)
        print(f"Fetched {len(real_candidates)} candidates from PR #71")
    except Exception as e:
        print(f"Error fetching data from GitHub: {e}")
        return
        
    # Create name mapping (Cleaned Nepali Name -> CandidateID)
    name_map = {}
    for rc in real_candidates:
        name = rc.get('CandidateName', '').strip()
        if name:
            cleaned = clean_name(name)
            name_map[cleaned] = rc.get('CandidateID')
            
    print(f"Built mapping for {len(name_map)} unique cleaned names")
    
    match_count = 0
    
    # Process parliament members
    for candidate in parliament_data['data']['data']:
        # Try to find Nepali name in translations
        nepali_names = []
        for trans in candidate.get('parliament_member_translations', []):
            if trans.get('locale') == 'np':
                nepali_names.append(trans.get('name', '').strip())
        
        # Also try English name in case it's Nepali in the name field
        nepali_names.append(candidate.get('name', '').strip())
            
        # Match with real data
        matched = False
        for n in nepali_names:
            cleaned = clean_name(n)
            if cleaned in name_map:
                nec_id = name_map[cleaned]
                photo_url = f"https://result.election.gov.np/Images/Candidate/{nec_id}.jpg"
                
                if 'images' not in candidate or not isinstance(candidate['images'], dict):
                    candidate['images'] = {}
                if 'images' not in candidate['images']:
                    candidate['images']['images'] = {}
                    
                candidate['images']['images']['original'] = photo_url
                candidate['images']['images']['thumbnail'] = photo_url
                candidate['images']['imageName'] = str(nec_id)
                
                if 'metadata' not in candidate:
                    candidate['metadata'] = {}
                candidate['metadata']['photo_url'] = photo_url
                candidate['metadata']['image_url'] = photo_url
                candidate['metadata']['nec_candidate_id'] = str(nec_id)
                
                match_count += 1
                matched = True
                break
        
    print(f"Matched {match_count} parliament members to real NEC photos")
    
    # Integration of new candidates
    new_candidates_count = 0
    existing_cleaned_names = set()
    for c in parliament_data['data']['data']:
        existing_cleaned_names.add(clean_name(c.get('name', '')))
        for trans in c.get('parliament_member_translations', []):
            if trans.get('locale') == 'np':
                existing_cleaned_names.add(clean_name(trans.get('name', '')))

    for rc in real_candidates:
        name_np = rc.get('CandidateName', '').strip()
        cleaned_np = clean_name(name_np)
        if cleaned_np not in existing_cleaned_names:
            nec_id = rc.get('CandidateID')
            photo_url = f"https://result.election.gov.np/Images/Candidate/{nec_id}.jpg"
            
            new_candidate = {
                "id": 8000 + new_candidates_count,
                "name": name_np,
                "parliament_type": "central",
                "member_type": "candidate",
                "gender": 1 if rc.get('Gender') == 'महिला' else 0,
                "images": {
                    "images": {
                        "original": photo_url,
                        "thumbnail": photo_url
                    }
                },
                "political_party": {
                    "party_name_en": rc.get('PoliticalPartyName'),
                    "party_name_np": rc.get('PoliticalPartyName')
                },
                "district": {
                    "name_en": rc.get('DistrictName'),
                    "name_np": rc.get('DistrictName')
                },
                "metadata": {
                    "photo_url": photo_url,
                    "nec_candidate_id": str(nec_id),
                    "age": rc.get('AGE_YR'),
                    "qualification": rc.get('QUALIFICATION')
                },
                "parliament_member_translations": [
                    {"locale": "en", "name": name_np},
                    {"locale": "np", "name": name_np}
                ]
            }
            parliament_data['data']['data'].append(new_candidate)
            new_candidates_count += 1
            existing_cleaned_names.add(cleaned_np)
            
            if new_candidates_count >= 635:
                break
                
    print(f"Added {new_candidates_count} new candidates from PR #71")
    
    # Save enhanced data
    parliament_data['data']['total'] = len(parliament_data['data']['data'])
    per_page = parliament_data['data'].get('per_page', 60)
    parliament_data['data']['last_page'] = (parliament_data['data']['total'] + per_page - 1) // per_page
    
    with open(enhanced_data_file, 'w', encoding='utf-8') as f:
        json.dump(parliament_data, f, ensure_ascii=False, indent=2)
        
    print(f"Saved enhanced data to {enhanced_data_file}")
    print(f"Total candidates: {parliament_data['data']['total']}")

if __name__ == "__main__":
    sync_real_photos()
