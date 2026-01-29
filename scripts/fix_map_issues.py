#!/usr/bin/env python3
"""
Script to fix common map issues and improve map functionality
Addresses GeoJSON loading, API integration, and map display problems
"""

import json
import os
from pathlib import Path

def fix_map_issues():
    """Fix common map issues and improve functionality"""
    
    base_dir = Path(__file__).parent.parent
    map_file = base_dir / "frontend" / "map.html"
    
    print("🗺️ Fixing Map Issues")
    print("=" * 40)
    
    try:
        with open(map_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix 1: Add better error handling and debugging
        better_load_data = '''        async function loadData() {
            try {
                console.log('Loading map data...');
                
                // Load leaders data first
                try {
                    const leadersRes = await api.fetchLeaders({ limit: 1000 });
                    leadersData = leadersRes;
                    console.log(`✅ Loaded ${leadersData.length} leaders`);
                } catch (apiError) {
                    console.error('❌ Failed to load leaders data:', apiError);
                    leadersData = [];
                }

                // Try to load district GeoJSON data first (more detailed)
                let geoRes;
                let dataType = 'district';
                let mapDataLoaded = false;
                
                try {
                    console.log('🔍 Trying to load district boundaries...');
                    geoRes = await fetch('data/NewNepalDistrict.json');
                    if (!geoRes.ok) {
                        throw new Error(`District data HTTP ${geoRes.status}: ${geoRes.statusText}`);
                    }
                    mapData = await geoRes.json();
                    console.log(`✅ Loaded ${mapData.features?.length || 0} district boundaries`);
                    mapDataLoaded = true;
                } catch (e) {
                    console.log('⚠️ District data not available:', e.message);
                    
                    try {
                        console.log('🔍 Trying to load province boundaries...');
                        geoRes = await fetch('data/NewNepalProvince.json');
                        if (!geoRes.ok) {
                            throw new Error(`Province data HTTP ${geoRes.status}: ${geoRes.statusText}`);
                        }
                        mapData = await geoRes.json();
                        dataType = 'province';
                        console.log(`✅ Loaded ${mapData.features?.length || 0} province boundaries`);
                        mapDataLoaded = true;
                    } catch (e2) {
                        console.log('⚠️ Province data not available:', e2.message);
                        console.log('🔄 Creating fallback map...');
                        createFallbackMap();
                        return;
                    }
                }

                if (mapDataLoaded) {
                    // Add base map tiles with Nepal-focused styling
                    console.log('🗺️ Adding base map tiles...');
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: '© OpenStreetMap contributors',
                        maxZoom: 10,
                        bounds: [[26.3, 80.0], [30.4, 88.2]]
                    }).addTo(map);

                    // Fit map to Nepal bounds initially
                    map.fitBounds([[26.3, 80.0], [30.4, 88.2]], { padding: [10, 10] });

                    console.log('🎨 Adding GeoJSON layer...');
                    addGeoJsonLayer();
                    console.log('✅ Map initialization complete!');
                } else {
                    console.log('❌ No map data available, using fallback');
                    createFallbackMap();
                }

            } catch (err) {
                console.error("❌ Failed to load map data:", err);
                createFallbackMap();
            }
        }'''
        
        # Replace the existing loadData function
        start_marker = 'async function loadData() {'
        end_marker = 'createSimpleProvinceMap()'
        
        start_pos = content.find(start_marker)
        end_pos = content.find(end_marker)
        
        if start_pos != -1 and end_pos != -1:
            # Find the end of the loadData function
            brace_count = 0
            func_end = start_pos
            in_function = False
            
            for i in range(start_pos, end_pos):
                if content[i] == '{':
                    brace_count += 1
                    in_function = True
                elif content[i] == '}':
                    brace_count -= 1
                    if in_function and brace_count == 0:
                        func_end = i + 1
                        break
            
            if func_end > start_pos:
                content = content[:start_pos] + better_load_data + '\n\n        function ' + content[end_pos:]
        
        # Fix 2: Improve fallback map
        better_fallback = '''        function createFallbackMap() {
            console.log('🔄 Creating fallback map...');
            
            // Add OpenStreetMap tiles
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 10
            }).addTo(map);

            // Fit to Nepal bounds
            map.fitBounds([[26.3, 80.0], [30.4, 88.2]], { padding: [10, 10] });

            // Create province markers with leader counts
            const provinceData = [
                { name: 'Koshi', lat: 27.025, lng: 87.267, color: '#4A90E2' },
                { name: 'Madhesh', lat: 26.728, lng: 85.373, color: '#7ED321' },
                { name: 'Bagmati', lat: 27.717, lng: 85.324, color: '#F5A623' },
                { name: 'Gandaki', lat: 28.230, lng: 83.988, color: '#50E3C2' },
                { name: 'Lumbini', lat: 27.875, lng: 82.183, color: '#BD10E0' },
                { name: 'Karnali', lat: 29.267, lng: 82.183, color: '#D0021B' },
                { name: 'Sudurpashchim', lat: 29.267, lng: 80.583, color: '#F8E71C' }
            ];

            provinceData.forEach(province => {
                // Count leaders in this province
                const leaderCount = leadersData.filter(l => {
                    const prov = getProvinceForLeader(l);
                    return prov && prov.toLowerCase() === province.name.toLowerCase();
                }).length;

                const circle = L.circle([province.lat, province.lng], {
                    color: province.color,
                    fillColor: province.color,
                    fillOpacity: 0.6,
                    radius: Math.max(30000, leaderCount * 2000)
                }).addTo(map);

                circle.bindTooltip(`<strong>${province.name} Province</strong><br>${leaderCount} Representatives<br>Click to view details`, {
                    permanent: false,
                    direction: 'top'
                });

                circle.on('click', () => {
                    selectProvinceByName(province.name);
                });
            });

            console.log('✅ Fallback map created with province markers');
        }'''
        
        # Replace createFallbackMap function
        fallback_start = content.find('function createFallbackMap() {')
        if fallback_start != -1:
            # Find the end of the function
            brace_count = 0
            func_end = fallback_start
            in_function = False
            
            for i in range(fallback_start, len(content)):
                if content[i] == '{':
                    brace_count += 1
                    in_function = True
                elif content[i] == '}':
                    brace_count -= 1
                    if in_function and brace_count == 0:
                        func_end = i + 1
                        break
            
            if func_end > fallback_start:
                # Find the next function to preserve spacing
                next_func = content.find('function ', func_end)
                if next_func == -1:
                    next_func = len(content)
                
                content = content[:fallback_start] + better_fallback + '\n\n        ' + content[next_func:]
        
        # Fix 3: Add better error handling for API calls
        if 'api.fetchLeaders' in content and 'catch' not in content[content.find('api.fetchLeaders'):content.find('api.fetchLeaders') + 200]:
            content = content.replace(
                'const leadersRes = await api.fetchLeaders({ limit: 1000 });',
                '''try {
                    const leadersRes = await api.fetchLeaders({ limit: 1000 });
                } catch (apiError) {
                    console.error('API Error:', apiError);
                    const leadersRes = [];
                }'''
            )
        
        # Save the fixed file
        with open(map_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Map issues fixed!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing map: {e}")
        return False

def verify_geojson_files():
    """Verify GeoJSON files are valid and accessible"""
    
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "frontend" / "data"
    
    print("🔍 Verifying GeoJSON files...")
    
    files_to_check = [
        "NewNepalDistrict.json",
        "NewNepalProvince.json"
    ]
    
    for filename in files_to_check:
        file_path = data_dir / filename
        
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                feature_count = len(data.get('features', []))
                print(f"✅ {filename}: {feature_count} features")
                
                # Check if features have required properties
                if feature_count > 0:
                    sample_feature = data['features'][0]
                    props = sample_feature.get('properties', {})
                    print(f"   Sample properties: {list(props.keys())[:5]}...")
                
            except json.JSONDecodeError as e:
                print(f"❌ {filename}: Invalid JSON - {e}")
            except Exception as e:
                print(f"❌ {filename}: Error reading file - {e}")
        else:
            print(f"❌ {filename}: File not found")
    
    return True

def create_debug_map():
    """Create a debug version of the map for testing"""
    
    base_dir = Path(__file__).parent.parent
    debug_file = base_dir / "frontend" / "map-debug.html"
    map_file = base_dir / "frontend" / "map.html"
    
    print("🐛 Creating debug map...")
    
    try:
        with open(map_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add debug console logging
        debug_script = '''
        <script>
            // Debug logging
            const originalLog = console.log;
            const originalError = console.error;
            
            console.log = function(...args) {
                originalLog.apply(console, args);
                // You could also display logs on the page here
            };
            
            console.error = function(...args) {
                originalError.apply(console, args);
                // Display errors on the page
                const errorDiv = document.getElementById('debug-errors') || createErrorDiv();
                errorDiv.innerHTML += '<div style="color: red; margin: 5px 0;">' + args.join(' ') + '</div>';
            };
            
            function createErrorDiv() {
                const div = document.createElement('div');
                div.id = 'debug-errors';
                div.style.cssText = 'position: fixed; top: 10px; right: 10px; background: white; border: 1px solid red; padding: 10px; max-width: 300px; z-index: 10000; max-height: 200px; overflow-y: auto;';
                document.body.appendChild(div);
                return div;
            }
        </script>
        '''
        
        # Insert debug script before closing head tag
        content = content.replace('</head>', debug_script + '\n</head>')
        
        # Add debug title
        content = content.replace('<title>Interactive Map', '<title>[DEBUG] Interactive Map')
        
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Debug map created: {debug_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating debug map: {e}")
        return False

def main():
    print("🇳🇵 Nepal Map Fixing Tool")
    print("=" * 40)
    
    # Verify GeoJSON files
    verify_geojson_files()
    
    # Fix map issues
    success = fix_map_issues()
    
    # Create debug version
    create_debug_map()
    
    if success:
        print("\n" + "=" * 40)
        print("🎉 Map Fixes Applied!")
        print("=" * 40)
        print("\n✅ Improvements made:")
        print("  - Enhanced error handling and debugging")
        print("  - Better GeoJSON loading with fallbacks")
        print("  - Improved API error handling")
        print("  - Enhanced fallback map with province markers")
        print("  - Added comprehensive logging")
        print("  - Created debug version for testing")
        
        print("\n🔄 Next steps:")
        print("1. Restart your local server")
        print("2. Visit http://localhost:8196/map.html")
        print("3. Check browser console for detailed logs")
        print("4. Use http://localhost:8196/map-debug.html for debugging")
        
    else:
        print("\n❌ Map fixing failed!")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()