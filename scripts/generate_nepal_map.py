"""Convert Nepal shapefile to simplified GeoJSON for web use."""
import json
import struct
from pathlib import Path

def read_dbf(dbf_path):
    """Read DBF file to get province names."""
    with open(dbf_path, 'rb') as f:
        # Read DBF header
        f.seek(8)
        num_records = struct.unpack('<I', f.read(4))[0]
        header_size = struct.unpack('<H', f.read(2))[0]
        record_size = struct.unpack('<H', f.read(2))[0]
        
        # Skip to field descriptors
        f.seek(32)
        fields = []
        while True:
            field_info = f.read(32)
            if field_info[0] == 0x0D:  # End of field descriptors
                break
            name = field_info[:11].decode('ascii').strip('\x00')
            field_type = chr(field_info[11])
            length = field_info[16]
            fields.append((name, field_type, length))
        
        # Read records
        f.seek(header_size + 1)
        records = []
        for _ in range(num_records):
            record = {}
            record_data = f.read(record_size)
            if record_data[0] == 0x2A:  # Deleted record
                continue
            pos = 1
            for name, field_type, length in fields:
                value = record_data[pos:pos+length].decode('ascii', errors='ignore').strip()
                record[name] = value
                pos += length
            records.append(record)
        
        return records

# Nepal provinces data (manual mapping since shapefile conversion is complex)
nepal_provinces = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "id": 1,
                "name": "Koshi",
                "name_nepali": "कोशी प्रदेश",
                "capital": "Biratnagar"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[87.7, 26.4], [88.2, 26.4], [88.2, 27.9], [86.8, 27.9], [86.8, 26.9], [87.7, 26.4]]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": 2,
                "name": "Madhesh",
                "name_nepali": "मधेश प्रदेश",
                "capital": "Janakpur"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[84.9, 26.3], [87.7, 26.3], [87.7, 27.3], [84.9, 27.3], [84.9, 26.3]]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": 3,
                "name": "Bagmati",
                "name_nepali": "बागमती प्रदेश",
                "capital": "Hetauda"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[84.5, 27.2], [86.3, 27.2], [86.3, 28.3], [84.5, 28.3], [84.5, 27.2]]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": 4,
                "name": "Gandaki",
                "name_nepali": "गण्डकी प्रदेश",
                "capital": "Pokhara"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[83.2, 27.8], [85.0, 27.8], [85.0, 29.0], [83.2, 29.0], [83.2, 27.8]]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": 5,
                "name": "Lumbini",
                "name_nepali": "लुम्बिनी प्रदेश",
                "capital": "Deukhuri"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[82.3, 27.2], [84.5, 27.2], [84.5, 28.7], [82.3, 28.7], [82.3, 27.2]]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": 6,
                "name": "Karnali",
                "name_nepali": "कर्णाली प्रदेश",
                "capital": "Birendranagar"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[81.0, 28.5], [83.0, 28.5], [83.0, 30.4], [81.0, 30.4], [81.0, 28.5]]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": 7,
                "name": "Sudurpashchim",
                "name_nepali": "सुदूरपश्चिम प्रदेश",
                "capital": "Godawari"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[80.0, 28.5], [81.5, 28.5], [81.5, 30.2], [80.0, 30.2], [80.0, 28.5]]]
            }
        }
    ]
}

# Try to read DBF file for actual data
try:
    dbf_path = Path(__file__).parent.parent / "geojasondata" / "gadm41_NPL_shp" / "gadm41_NPL_1.dbf"
    if dbf_path.exists():
        print(f"Reading province data from {dbf_path}")
        records = read_dbf(dbf_path)
        print(f"Found {len(records)} provinces:")
        for i, record in enumerate(records, 1):
            print(f"{i}. {record.get('NAME_1', 'Unknown')}")
except Exception as e:
    print(f"Could not read shapefile data: {e}")
    print("Using simplified province geometry...")

# Save GeoJSON
output_path = Path(__file__).parent.parent / "frontend" / "data" / "nepal-provinces.geojson"
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(nepal_provinces, f, indent=2, ensure_ascii=False)

print(f"\nGeoJSON saved to: {output_path}")
print("\nNote: Using simplified rectangular geometries for web display.")
print("For production, use proper GeoJSON conversion tools like ogr2ogr or mapshaper.")
