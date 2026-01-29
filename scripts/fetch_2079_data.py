#!/usr/bin/env python3
"""
Script to fetch 2079 election candidate data from GitHub PR #71
Downloads the required data files for integration
"""

import requests
import json
import csv
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # GitHub raw URLs for the data files from PR #71
        self.github_base = "https://raw.githubusercontent.com/NewNepal-org/NepalEntityService"
        self.pr_branch = "source-2082-direct-candidates"  # Branch from PR #71
        
        # Data file URLs (these would need to be updated with actual paths)
        self.data_files = {
            "candidates_2079": f"{self.github_base}/{self.pr_branch}/migrations/010-source-2082-direct-candidates/data/DirectElectionResultCentral2082.json",
            "candidate_matches": f"{self.github_base}/{self.pr_branch}/migrations/010-source-2082-direct-candidates/data/candidate_id_matches_2079_2082.csv",
            "district_mapping": f"{self.github_base}/{self.pr_branch}/migrations/010-source-2082-direct-candidates/data/district-to-slug.csv",
            "party_updates": f"{self.github_base}/{self.pr_branch}/migrations/010-source-2082-direct-candidates/data/party-updates.json"
        }
        
    def download_file(self, url, local_path):
        """Download a file from URL to local path"""
        try:
            logger.info(f"Downloading {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded to {local_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {url}: {e}")
            return False
    
    def fetch_all_data(self):
        """Fetch all required data files"""
        logger.info("Fetching 2079 election data files...")
        
        success_count = 0
        total_files = len(self.data_files)
        
        for file_key, url in self.data_files.items():
            local_filename = f"{file_key}.{url.split('.')[-1]}"
            local_path = self.data_dir / local_filename
            
            if self.download_file(url, local_path):
                success_count += 1
            else:
                logger.warning(f"Failed to download {file_key}")
        
        logger.info(f"Downloaded {success_count}/{total_files} files successfully")
        return success_count == total_files
    
    def create_mock_data(self):
        """Create mock data files for testing when actual files aren't available"""
        logger.info("Creating mock data files for testing...")
        
        # Mock candidate data (635 candidates from 2079 state election)
        mock_candidates = []
        
        # Sample districts and parties
        districts = ["Kathmandu", "Lalitpur", "Bhaktapur", "Chitwan", "Pokhara", "Butwal", "Biratnagar", "Janakpur"]
        parties = [
            "Nepal Communist Party (Unified Marxist-Leninist)",
            "Nepali Congress", 
            "Communist Party of Nepal (Maoist Centre)",
            "Rastriya Swatantra Party",
            "Rastriya Prajatantra Party",
            "Janata Samajwadi Party Nepal",
            "Nepal Workers Peasants Party",
            "Independent"
        ]
        
        for i in range(635):  # Create 635 candidates
            candidate = {
                "id": 6000 + i,
                "name": f"Candidate {i+1}",
                "name_nepali": f"उम्मेदवार {i+1}",
                "district": districts[i % len(districts)],
                "party": parties[i % len(parties)],
                "gender": i % 2,  # 0 = Male, 1 = Female
                "age": 25 + (i % 50),  # Age between 25-74
                "constituency": (i % 10) + 1,
                "election_type": "state",
                "election_year": 2079,
                "photo_url": f"https://example.com/photos/candidate_{6000+i}.jpg",
                "address": f"Ward {(i % 10) + 1}, {districts[i % len(districts)]}",
                "qualification": "Bachelor's Degree" if i % 3 == 0 else "Master's Degree",
                "occupation": "Politics" if i % 4 == 0 else "Business"
            }
            mock_candidates.append(candidate)
        
        # Save mock candidates
        candidates_file = self.data_dir / "candidates_2079.json"
        with open(candidates_file, 'w', encoding='utf-8') as f:
            json.dump(mock_candidates, f, ensure_ascii=False, indent=2)
        
        # Mock candidate matches (first 100 candidates match existing parliament members)
        matches = []
        for i in range(100):
            matches.append({
                "candidate_id_2079": str(6000 + i),
                "parliament_id": str(2501 + (i % 50))  # Cycle through existing IDs
            })
        
        matches_file = self.data_dir / "candidate_matches.csv"
        with open(matches_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['candidate_id_2079', 'parliament_id'])
            writer.writeheader()
            writer.writerows(matches)
        
        # Mock district mapping
        district_mapping = []
        for district in districts:
            district_mapping.append({
                "district_name": district,
                "district_slug": district.lower().replace(' ', '-')
            })
        
        district_file = self.data_dir / "district_mapping.csv"
        with open(district_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['district_name', 'district_slug'])
            writer.writeheader()
            writer.writerows(district_mapping)
        
        # Mock party updates
        party_updates = {
            "new_parties": [
                {
                    "name_en": "New Democratic Party",
                    "name_np": "नयाँ लोकतान्त्रिक पार्टी",
                    "slug": "new-democratic-party"
                }
            ],
            "updated_parties": [
                {
                    "old_name": "Old Party Name",
                    "new_name": "Updated Party Name",
                    "slug": "updated-party-name"
                }
            ]
        }
        
        party_file = self.data_dir / "party_updates.json"
        with open(party_file, 'w', encoding='utf-8') as f:
            json.dump(party_updates, f, ensure_ascii=False, indent=2)
        
        logger.info("Mock data files created successfully")
        logger.info(f"Created {len(mock_candidates)} candidate records")
        logger.info(f"Files saved in: {self.data_dir}")
        
        return True

def main():
    fetcher = DataFetcher()
    
    print("🇳🇵 Nepal 2079 Election Data Fetcher")
    print("=" * 50)
    
    # Try to fetch real data first
    print("Attempting to fetch real data from GitHub PR #71...")
    success = fetcher.fetch_all_data()
    
    if not success:
        print("\n⚠️  Could not fetch real data from GitHub")
        print("Creating mock data for testing purposes...")
        fetcher.create_mock_data()
        print("\n✅ Mock data created successfully!")
        print("\nNote: This is sample data for testing.")
        print("For real data, please:")
        print("1. Check the GitHub PR #71 for actual data file locations")
        print("2. Update the URLs in fetch_2079_data.py")
        print("3. Re-run this script")
    else:
        print("\n✅ Real data fetched successfully!")
    
    print(f"\nData files location: {fetcher.data_dir}")
    print("\nNext steps:")
    print("1. Run: python scripts/integrate_2079_candidates.py")
    print("2. This will integrate the 635 candidates into your application")

if __name__ == "__main__":
    main()