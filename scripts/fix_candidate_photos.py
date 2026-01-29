#!/usr/bin/env python3
"""
Script to fix candidate photo issues and provide better photo sources
Fixes URL concatenation issues and provides reliable photo alternatives
"""

import json
import os
from pathlib import Path
import random

def fix_candidate_photos():
    """Fix candidate photo URLs and provide better alternatives"""
    
    base_dir = Path(__file__).parent.parent
    enhanced_data_file = base_dir / "parliament_data_enhanced.json"
    
    print("🔧 Fixing Candidate Photo Issues")
    print("=" * 50)
    
    # Load enhanced data
    try:
        with open(enhanced_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data['data']['data'])} candidates")
    except FileNotFoundError:
        print("❌ Enhanced data file not found!")
        return False
    
    # Better photo services that are more reliable
    photo_services = {
        'avatars': 'https://i.pravatar.cc/200?img={}',
        'dicebear_personas': 'https://avatars.dicebear.com/api/personas/{}.svg',
        'dicebear_avataaars': 'https://avatars.dicebear.com/api/avataaars/{}.svg',
        'robohash': 'https://robohash.org/{}?set=set1&size=200x200',
        'placeholder': 'https://via.placeholder.com/200x200/4A90E2/FFFFFF?text={}'
    }
    
    # Create consistent photo assignments
    male_photo_base = "https://i.pravatar.cc/200?img="
    female_photo_base = "https://i.pravatar.cc/200?img="
    
    # Available photo IDs (pravatar has photos 1-70 for both genders)
    male_photo_ids = list(range(1, 71))  # 1-70 for males
    female_photo_ids = list(range(1, 71))  # 1-70 for females (different set)
    
    fixed_count = 0
    parliament_kept = 0
    
    print("Processing candidates...")
    
    for i, candidate in enumerate(data['data']['data']):
        try:
            candidate_id = candidate.get('id', i + 1000)
            gender = candidate.get('gender', 0)
            name = candidate.get('name', f'Candidate {i+1}')
            
            # Check if this is a parliament member with existing official photo
            is_parliament_member = candidate.get('parliament_type') == 'hr'
            has_official_photo = False
            
            if is_parliament_member and candidate.get('images', {}).get('images', {}).get('original'):
                original_url = candidate['images']['images']['original']
                # Check if it's a valid parliament.gov.np URL (not concatenated)
                if 'parliament.gov.np' in original_url and not 'https://randomuser.me' in original_url:
                    has_official_photo = True
                    parliament_kept += 1
                    continue  # Keep official parliament photos
            
            # Fix/assign photos for all other candidates
            if gender == 1:  # Female
                photo_id = female_photo_ids[candidate_id % len(female_photo_ids)]
                primary_photo = f"{female_photo_base}{photo_id + 40}"  # Offset for female photos
                fallback_photo = f"https://avatars.dicebear.com/api/personas/female{candidate_id}.svg"
            else:  # Male
                photo_id = male_photo_ids[candidate_id % len(male_photo_ids)]
                primary_photo = f"{male_photo_base}{photo_id}"
                fallback_photo = f"https://avatars.dicebear.com/api/personas/male{candidate_id}.svg"
            
            # Alternative photo for variety
            alternative_photo = f"https://robohash.org/{candidate_id}?set=set1&size=200x200"
            
            # Ensure proper image structure
            if not candidate.get('images'):
                candidate['images'] = {}
            
            if not candidate['images'].get('images'):
                candidate['images']['images'] = {}
            
            # Set clean photo URLs
            candidate['images']['images']['original'] = primary_photo
            candidate['images']['images']['thumbnail'] = primary_photo
            
            # Update image metadata
            candidate['images']['clientOriginalName'] = f"{name.replace(' ', '_')}.jpg"
            candidate['images']['clientOriginalExtension'] = "jpg"
            candidate['images']['mimeType'] = "image/jpeg"
            candidate['images']['imageName'] = str(candidate_id)
            
            # Ensure metadata exists
            if not candidate.get('metadata'):
                candidate['metadata'] = {}
            
            # Set multiple photo options in metadata
            candidate['metadata']['photo_url'] = primary_photo
            candidate['metadata']['image_url'] = primary_photo
            candidate['metadata']['fallback_photo'] = fallback_photo
            candidate['metadata']['alternative_photo'] = alternative_photo
            
            fixed_count += 1
            
            # Show progress for first few candidates
            if i < 10:
                gender_str = "Female" if gender == 1 else "Male"
                print(f"  ✓ Fixed: {name} ({gender_str}) - {primary_photo}")
        
        except Exception as e:
            print(f"  ⚠️  Error processing candidate {i}: {e}")
    
    # Save fixed data
    print(f"\nSaving fixed data...")
    with open(enhanced_data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Photo fixing complete!")
    print(f"📊 Results:")
    print(f"  - Fixed photos: {fixed_count}")
    print(f"  - Parliament photos kept: {parliament_kept}")
    print(f"  - Total candidates: {len(data['data']['data'])}")
    print(f"  - Fixed data saved to: {enhanced_data_file}")
    
    return True

def create_better_placeholder():
    """Create a better placeholder image"""
    base_dir = Path(__file__).parent.parent
    frontend_dir = base_dir / "frontend" / "assets"
    frontend_dir.mkdir(exist_ok=True)
    
    # Create a better SVG placeholder
    placeholder_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
    <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#4A90E2;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#357ABD;stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect width="200" height="200" fill="url(#grad1)" rx="100"/>
    <circle cx="100" cy="80" r="30" fill="white" opacity="0.8"/>
    <path d="M 60 140 Q 100 120 140 140 L 140 180 Q 100 160 60 180 Z" fill="white" opacity="0.8"/>
    <text x="100" y="190" text-anchor="middle" fill="white" font-size="12" font-family="Arial">Nepal</text>
</svg>'''
    
    placeholder_file = frontend_dir / "placeholder.svg"
    with open(placeholder_file, 'w', encoding='utf-8') as f:
        f.write(placeholder_svg)
    
    print(f"✅ Created better placeholder: {placeholder_file}")

def update_frontend_photo_handling():
    """Update frontend JavaScript to handle photos better"""
    base_dir = Path(__file__).parent.parent
    leaders_file = base_dir / "frontend" / "leaders.html"
    
    print("🔧 Updating frontend photo handling...")
    
    try:
        with open(leaders_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Better photo URL function
        better_photo_function = '''        // Helper to get photo URL with better fallbacks
        function getPhotoUrl(leader) {
            // Try multiple sources for photo URL in order of preference
            let photoUrl = null;
            
            // 1. Try images.images.original (main photo)
            if (leader.images && leader.images.images && leader.images.images.original) {
                photoUrl = leader.images.images.original;
                // Make sure it's not a concatenated URL
                if (!photoUrl.includes('https://randomuser.me') || photoUrl.indexOf('https://') === photoUrl.lastIndexOf('https://')) {
                    return photoUrl;
                }
            }
            
            // 2. Try metadata photo_url
            if (leader.metadata && leader.metadata.photo_url) {
                return leader.metadata.photo_url;
            }
            
            // 3. Try metadata image_url
            if (leader.metadata && leader.metadata.image_url) {
                return leader.metadata.image_url;
            }
            
            // 4. Generate a consistent photo based on ID and gender
            const candidateId = leader.id || 1000;
            const gender = leader.gender || 0;
            
            if (gender === 1) {
                // Female - use pravatar with offset
                return `https://i.pravatar.cc/200?img=${(candidateId % 70) + 40}`;
            } else {
                // Male - use pravatar
                return `https://i.pravatar.cc/200?img=${(candidateId % 70) + 1}`;
            }
        }'''
        
        # Replace the existing getPhotoUrl function
        if 'function getPhotoUrl(leader)' in content:
            # Find the start and end of the existing function
            start = content.find('// Helper to get photo URL')
            if start == -1:
                start = content.find('function getPhotoUrl(leader)')
            
            # Find the end of the function (next function or script end)
            end = content.find('function ', start + 10)
            if end == -1:
                end = content.find('</script>', start)
            
            if start != -1 and end != -1:
                content = content[:start] + better_photo_function + '\n\n        ' + content[end:]
        else:
            # Add the function before the last script tag
            script_end = content.rfind('</script>')
            if script_end != -1:
                content = content[:script_end] + better_photo_function + '\n    ' + content[script_end:]
        
        # Save updated file
        with open(leaders_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Frontend photo handling updated")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not update frontend: {e}")
        return False

def main():
    print("🇳🇵 Nepal Candidate Photo Fixing Tool")
    print("=" * 50)
    
    # Create better placeholder
    create_better_placeholder()
    
    # Fix candidate photos
    success = fix_candidate_photos()
    
    # Update frontend photo handling
    update_frontend_photo_handling()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 Photo Fixing Complete!")
        print("=" * 50)
        print("\n✅ Fixes applied:")
        print("  - Fixed concatenated photo URLs")
        print("  - Provided reliable photo sources (pravatar.cc)")
        print("  - Added multiple fallback options")
        print("  - Created better placeholder image")
        print("  - Updated frontend photo handling")
        print("  - Kept official parliament photos where valid")
        
        print("\n🔄 Next steps:")
        print("1. Restart your local server")
        print("2. Visit http://localhost:8196/leaders.html")
        print("3. All candidate photos should now load properly")
        print("4. Photos are consistent and reliable")
        
    else:
        print("\n❌ Photo fixing failed!")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()