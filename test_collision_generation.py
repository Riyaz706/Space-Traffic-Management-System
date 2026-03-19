#!/usr/bin/env python3
"""
Test script to verify collision generation with the new 38 objects
"""

import json
import os
from datetime import datetime, timedelta

def test_collision_generation():
    """Test collision generation with the 38 objects"""
    print("🚀 Testing Collision Generation with 38 Objects")
    print("=" * 60)
    
    # Load the JSON data (prefer processed, fallback to fake)
    try:
        path_candidates = [
            'data/processed_satellite_data.json',
            'data/fake_satellite_data.json'
        ]
        satellites = None
        for p in path_candidates:
            if os.path.exists(p):
                with open(p, 'r') as f:
                    data = json.load(f)
                    satellites = data['satellites']
                    print(f"📦 Loaded dataset: {p}")
                    break
        if satellites is None:
            raise FileNotFoundError('No dataset found')
        
        print(f"✅ Loaded {len(satellites)} satellite/debris objects")
        
        # Analyze the data
        debris_objects = [k for k, v in satellites.items() if v.get('object_type') == 'debris']
        active_satellites = [k for k, v in satellites.items() if v.get('object_type') == 'satellite']
        starlink_sats = [k for k in satellites.keys() if 'STARLINK' in k]
        
        print(f"📊 Data Analysis:")
        print(f"   • Total objects: {len(satellites)}")
        print(f"   • Satellites: {len(active_satellites)}")
        print(f"   • Debris: {len(debris_objects)}")
        print(f"   • Starlink satellites: {len(starlink_sats)}")
        
        # Simulate collision generation logic
        collision_pairs = []
        
        # Debris vs Active satellite collisions (high risk)
        for debris in debris_objects:
            for satellite in active_satellites[:8]:
                if debris != satellite:
                    collision_pairs.append((debris, satellite, 'high'))
        
        # Starlink constellation collisions (medium risk)
        for i in range(min(6, len(starlink_sats))):
            for j in range(i + 1, min(i + 4, len(starlink_sats))):
                collision_pairs.append((starlink_sats[i], starlink_sats[j], 'medium'))
        
        # ISS-specific high-risk collisions
        if 'ISS' in satellites:
            iss_data = satellites['ISS']
            iss_altitude = iss_data.get('altitude', 408)
            iss_inclination = iss_data.get('inclination', 51.6)
            
            for sat_name, sat_data in satellites.items():
                if sat_name != 'ISS':
                    sat_altitude = sat_data.get('altitude', 500)
                    sat_inclination = sat_data.get('inclination', 45)
                    
                    alt_diff = abs(iss_altitude - sat_altitude)
                    inc_diff = abs(iss_inclination - sat_inclination)
                    
                    if alt_diff < 100 and inc_diff < 20:
                        collision_pairs.append(('ISS', sat_name, 'critical'))
        
        # General satellite-to-satellite collisions
        for i, sat1 in enumerate(active_satellites[:10]):
            for j, sat2 in enumerate(active_satellites[i+1:i+6]):
                if sat1 != sat2:
                    sat1_data = satellites[sat1]
                    sat2_data = satellites[sat2]
                    
                    alt_diff = abs(sat1_data.get('altitude', 500) - sat2_data.get('altitude', 500))
                    if alt_diff < 200:
                        collision_pairs.append((sat1, sat2, 'medium'))
        
        print(f"\n🔍 Collision Generation Results:")
        print(f"   • Total collision pairs generated: {len(collision_pairs)}")
        
        # Count by risk level
        critical_collisions = [p for p in collision_pairs if p[2] == 'critical']
        high_collisions = [p for p in collision_pairs if p[2] == 'high']
        medium_collisions = [p for p in collision_pairs if p[2] == 'medium']
        
        print(f"   • Critical risk collisions: {len(critical_collisions)}")
        print(f"   • High risk collisions: {len(high_collisions)}")
        print(f"   • Medium risk collisions: {len(medium_collisions)}")
        
        # Show some examples
        print(f"\n🎯 Example Collision Scenarios:")
        for i, (sat1, sat2, risk) in enumerate(collision_pairs[:10]):
            sat1_data = satellites[sat1]
            sat2_data = satellites[sat2]
            alt_diff = abs(sat1_data.get('altitude', 500) - sat2_data.get('altitude', 500))
            print(f"   {i+1}. {sat1} vs {sat2} ({risk.upper()} risk, {alt_diff}km altitude diff)")
        
        if len(collision_pairs) > 10:
            print(f"   ... and {len(collision_pairs) - 10} more collision scenarios")
        
        print(f"\n✅ Collision generation test completed successfully!")
        print(f"🎉 Expected to generate {min(len(collision_pairs), 20)} collision events in the dashboard")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing collision generation: {e}")
        return False

if __name__ == "__main__":
    test_collision_generation()
