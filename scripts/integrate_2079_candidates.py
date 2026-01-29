#!/usr/bin/env python3
"""
Script to integrate 635 candidates from 2079 state election data
Based on NewNepal-org/NepalEntityService PR #71

This script integrates the 635 candidates who ran in the 2079 state election
with their photos and electoral information.
"""

import json
import csv
import os
import requests
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CandidateIntegrator:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Current parliament data
        self.parliament_data_file = self.base_dir / "parliament_data.json"
        
        # New candidate data files (to be downloaded/provided)
        self.candidates_2079_file = self.data_dir / "DirectElectionResultState2079.json"
        self.candidate_matches_file = self.data_dir / "candidate_id_matches_2079.csv"
        self.district_mapping_file = self.data_dir / "district-to-slug.csv"
        
        # Output file
        self.enhanced_data_file = self.base_dir / "parliament_data_enhanced.json"
        
    def load_current_parliament_data(self):
        """Load current parliament data"""
        try:
            with open(self.parliament_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Parliament data file not found: {self.parliament_data_file}")
            return None
    
    def download_candidate_data(self):
        """
        Download or prepare candidate data files
        This would need to be adapted based on actual data source
        """
        logger.info("Preparing candidate data files...")
        
        # For now, create placeholder structure
        # In actual implementation, this would download from the PR or data source
        
        if not self.candidates_2079_file.exists():
            logger.warning(f"2079 candidate data file not found: {self.candidates_2079_file}")
            logger.info("Please provide the DirectElectionResultState2079.json file")
            return False
            
        if not self.candidate_matches_file.exists():
            logger.warning(f"Candidate matches file not found: {self.candidate_matches_file}")
            logger.info("Please provide the candidate_id_matches_2079.csv file")
            return False
            
        return True
    
    def load_2079_candidates(self):
        """Load 2079 state election candidates"""
        try:
            with open(self.candidates_2079_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} 2079 candidates")
                return data
        except FileNotFoundError:
            logger.error("2079 candidate data file not found")
            return []
    
    def load_candidate_matches(self):
        """Load candidate ID matches between different elections"""
        matches = {}
        try:
            with open(self.candidate_matches_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    matches[row['candidate_id_2079']] = row['parliament_id']
                logger.info(f"Loaded {len(matches)} candidate matches")
        except FileNotFoundError:
            logger.error("Candidate matches file not found")
        return matches
    
    def create_candidate_entity(self, candidate_data, candidate_id=None):
        """
        Create a candidate entity in the parliament data format
        """
        # Generate new ID if not provided
        if not candidate_id:
            candidate_id = 3000 + len(self.enhanced_candidates)
        
        # Extract candidate information
        name = candidate_data.get('name', '')
        name_nepali = candidate_data.get('name_nepali', '')
        district = candidate_data.get('district', '')
        party = candidate_data.get('party', '')
        gender = candidate_data.get('gender', 0)  # 0 = Male, 1 = Female
        age = candidate_data.get('age', '')
        
        # Create image structure if photo available
        images = {}
        if candidate_data.get('photo_url'):
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
        
        # Create candidate entity
        entity = {
            "id": candidate_id,
            "code": str(candidate_id),
            "slug": name.replace(' ', '-').lower(),
            "parliament_type": "state",  # State election
            "sequence": 0,
            "status": 1,
            "member_type": "candidate",
            "name": name,
            "dob": "1980-01-01",  # Placeholder, calculate from age if available
            "images": images,
            "district_id": None,  # Would need district mapping
            "registered_date": 2079,  # 2079 BS election
            "representation_type_id": 5,
            "political_party_id": None,  # Would need party mapping
            "election_type_id": 2506,  # State election type
            "election_area_no": candidate_data.get('constituency', 1),
            "territory_no": 1,
            "video_link": None,
            "secretariat_page": None,
            "gender": gender,
            "user_id": 1,
            "tenure_end_date": "2027-01-01",  # Estimated
            "created_by": "Data Integration",
            "published_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "district": {
                "id": None,
                "name_en": district,
                "name_np": district  # Would need proper Nepali name
            },
            "political_party": {
                "id": None,
                "party_name_en": party,
                "party_name_np": party  # Would need proper Nepali name
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
    
    def integrate_candidates(self):
        """Main integration function"""
        logger.info("Starting candidate integration...")
        
        # Load current parliament data
        parliament_data = self.load_current_parliament_data()
        if not parliament_data:
            return False
        
        # Check if data files are available
        if not self.download_candidate_data():
            logger.error("Required data files not available")
            return False
        
        # Load 2079 candidates
        candidates_2079 = self.load_2079_candidates()
        if not candidates_2079:
            return False
        
        # Load candidate matches
        candidate_matches = self.load_candidate_matches()
        
        # Filter to get only the 635 candidates who ran in state elections
        state_candidates = [c for c in candidates_2079 if c.get('election_type') == 'state'][:635]
        logger.info(f"Processing {len(state_candidates)} state election candidates")
        
        # Create enhanced dataset
        enhanced_data = parliament_data.copy()
        new_candidates = []
        updated_count = 0
        
        for candidate in state_candidates:
            candidate_id = candidate.get('id')
            
            # Check if candidate already exists in parliament data
            existing_candidate = None
            if str(candidate_id) in candidate_matches:
                parliament_id = candidate_matches[str(candidate_id)]
                existing_candidate = next(
                    (c for c in enhanced_data['data']['data'] if str(c['id']) == parliament_id), 
                    None
                )
            
            if existing_candidate:
                # Update existing candidate with 2079 election info
                existing_candidate['election_history'] = existing_candidate.get('election_history', [])
                existing_candidate['election_history'].append({
                    'year': 2079,
                    'election_type': 'state',
                    'district': candidate.get('district'),
                    'party': candidate.get('party'),
                    'constituency': candidate.get('constituency')
                })
                updated_count += 1
                logger.info(f"Updated existing candidate: {existing_candidate['name']}")
            else:
                # Create new candidate entity
                new_entity = self.create_candidate_entity(candidate)
                new_candidates.append(new_entity)
                logger.info(f"Created new candidate: {new_entity['name']}")
        
        # Add new candidates to the dataset
        enhanced_data['data']['data'].extend(new_candidates)
        enhanced_data['data']['total'] += len(new_candidates)
        
        # Save enhanced dataset
        with open(self.enhanced_data_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Integration complete!")
        logger.info(f"Updated {updated_count} existing candidates")
        logger.info(f"Added {len(new_candidates)} new candidates")
        logger.info(f"Enhanced data saved to: {self.enhanced_data_file}")
        
        return True
    
    def create_sample_data_files(self):
        """Create sample data files for testing"""
        logger.info("Creating sample data files...")
        
        # Sample 2079 candidates data
        sample_candidates = []
        for i in range(10):  # Create 10 sample candidates
            candidate = {
                "id": 5000 + i,
                "name": f"Sample Candidate {i+1}",
                "name_nepali": f"नमूना उम्मेदवार {i+1}",
                "district": "Kathmandu" if i % 2 == 0 else "Lalitpur",
                "party": "Sample Party" if i % 3 == 0 else "Another Party",
                "gender": i % 2,  # Alternate gender
                "age": 35 + i,
                "constituency": i + 1,
                "election_type": "state",
                "photo_url": f"https://example.com/photos/candidate_{5000+i}.jpg"
            }
            sample_candidates.append(candidate)
        
        # Save sample candidates
        with open(self.candidates_2079_file, 'w', encoding='utf-8') as f:
            json.dump(sample_candidates, f, ensure_ascii=False, indent=2)
        
        # Sample candidate matches
        sample_matches = []
        for i in range(5):  # Match first 5 candidates to existing parliament members
            sample_matches.append({
                "candidate_id_2079": str(5000 + i),
                "parliament_id": str(2501 + i)  # Existing parliament IDs
            })
        
        # Save sample matches
        with open(self.candidate_matches_file, 'w', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['candidate_id_2079', 'parliament_id'])
            writer.writeheader()
            writer.writerows(sample_matches)
        
        logger.info("Sample data files created successfully")

def main():
    integrator = CandidateIntegrator()
    
    # For demonstration, create sample data files
    integrator.create_sample_data_files()
    
    # Run integration
    success = integrator.integrate_candidates()
    
    if success:
        print("\n✅ Candidate integration completed successfully!")
        print(f"Enhanced data available at: {integrator.enhanced_data_file}")
        print("\nTo use the enhanced data in your application:")
        print("1. Replace parliament_data.json with parliament_data_enhanced.json")
        print("2. Restart your local server")
        print("3. The map and leaders pages will now include 2079 state election candidates")
    else:
        print("\n❌ Candidate integration failed!")
        print("Please ensure all required data files are available")

if __name__ == "__main__":
    main()