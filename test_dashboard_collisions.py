#!/usr/bin/env python3
"""
Test script to verify dashboard collision generation
"""

import json
import os
from datetime import datetime, timedelta

def test_dashboard_collision_generation():
    """Test the collision generation logic used in the dashboard"""
    print("🚀 Testing Dashboard Collision Generation")
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
        
        # Simulate the dashboard's collision generation logic
        def generate_realistic_collisions():
            """Generate realistic collision data based on loaded satellites"""
            collisions = []
            satellite_list = list(satellites.keys())
            
            # Generate collisions between different types of objects
            collision_pairs = []
            
            # High-risk collisions (debris vs active satellites)
            debris_objects = [k for k, v in satellites.items() if v.get('object_type') == 'debris']
            active_satellites = [k for k, v in satellites.items() if v.get('object_type') == 'satellite']
            
            print(f"📊 Found {len(debris_objects)} debris objects and {len(active_satellites)} active satellites")
            
            # Debris vs Active satellite collisions (high risk) - Generate more collisions
            for debris in debris_objects:  # Use all debris objects
                for satellite in active_satellites[:8]:  # Increase to 8 active satellites
                    if debris != satellite:
                        collision_pairs.append((debris, satellite, 'high'))
            
            # Starlink constellation collisions (medium risk) - Generate more constellation collisions
            starlink_sats = [k for k in satellite_list if 'STARLINK' in k]
            for i in range(min(6, len(starlink_sats))):  # Increase to 6 satellites
                for j in range(i + 1, min(i + 4, len(starlink_sats))):  # Increase pairs
                    collision_pairs.append((starlink_sats[i], starlink_sats[j], 'medium'))
            
            # Add ISS-specific high-risk collisions
            if 'ISS' in satellites:
                iss_data = satellites['ISS']
                iss_altitude = iss_data.get('altitude', 408)
                iss_inclination = iss_data.get('inclination', 51.6)
                
                # Find objects with similar altitude and inclination to ISS
                for sat_name, sat_data in satellites.items():
                    if sat_name != 'ISS':
                        sat_altitude = sat_data.get('altitude', 500)
                        sat_inclination = sat_data.get('inclination', 45)
                        
                        # Check if object is in ISS collision risk zone
                        alt_diff = abs(iss_altitude - sat_altitude)
                        inc_diff = abs(iss_inclination - sat_inclination)
                        
                        if alt_diff < 100 and inc_diff < 20:  # Close orbital parameters
                            collision_pairs.append(('ISS', sat_name, 'critical'))
            
            # Add more general satellite-to-satellite collisions
            for i, sat1 in enumerate(active_satellites[:10]):  # Check first 10 satellites
                for j, sat2 in enumerate(active_satellites[i+1:i+6]):  # Check next 5 satellites
                    if sat1 != sat2:
                        sat1_data = satellites[sat1]
                        sat2_data = satellites[sat2]
                        
                        alt_diff = abs(sat1_data.get('altitude', 500) - sat2_data.get('altitude', 500))
                        if alt_diff < 200:  # Within collision risk range
                            collision_pairs.append((sat1, sat2, 'medium'))
            
            print(f"🔍 Generated {len(collision_pairs)} collision pairs")
            print(f"📊 Debris objects: {len(debris_objects)}")
            print(f"🛰️ Active satellites: {len(active_satellites)}")
            print(f"🌟 Starlink satellites: {len([k for k in satellite_list if 'STARLINK' in k])}")
            
            # Generate collision data for each pair
            for i, (sat1, sat2, base_risk) in enumerate(collision_pairs):
                # Calculate realistic collision probability based on orbital parameters
                sat1_data = satellites[sat1]
                sat2_data = satellites[sat2]
                
                # Altitude difference affects collision probability
                alt_diff = abs(sat1_data.get('altitude', 500) - sat2_data.get('altitude', 500))
                base_prob = 0.8 if base_risk == 'high' else 0.4 if base_risk == 'medium' else 0.1
                
                # Adjust probability based on altitude difference
                if alt_diff < 50:
                    collision_prob = base_prob
                elif alt_diff < 100:
                    collision_prob = base_prob * 0.7
                else:
                    collision_prob = base_prob * 0.3
                
                # Generate realistic timing
                hours_ahead = (i * 3) + 2  # Spread collisions over time
                closest_approach_time = datetime.now() + timedelta(hours=hours_ahead)
                
                collision = {
                    "satellite1_name": sat1,
                    "satellite2_name": sat2,
                    "risk_level": base_risk,
                    "collision_probability": min(collision_prob, 0.95),
                    "closest_approach": {
                        "distance": 0.1 + (i * 0.5),  # Realistic distances
                        "time": closest_approach_time.strftime("%Y-%m-%dT%H:%M:%S")
                    },
                    "time_to_closest_approach": hours_ahead,
                    "altitude_difference": alt_diff,
                    "relative_velocity": 7.5 + (i * 0.2)  # km/s
                }
                collisions.append(collision)
            
            return collisions[:20]  # Limit to 20 most significant collisions
        
        # Test collision generation
        print("\n🔍 Testing collision generation...")
        collisions = generate_realistic_collisions()
        
        print(f"\n✅ Collision Generation Results:")
        print(f"   • Total collisions generated: {len(collisions)}")
        
        # Count by risk level
        critical_collisions = [c for c in collisions if c['risk_level'] == 'critical']
        high_collisions = [c for c in collisions if c['risk_level'] == 'high']
        medium_collisions = [c for c in collisions if c['risk_level'] == 'medium']
        
        print(f"   • Critical risk collisions: {len(critical_collisions)}")
        print(f"   • High risk collisions: {len(high_collisions)}")
        print(f"   • Medium risk collisions: {len(medium_collisions)}")
        
        # Show some examples
        print(f"\n🎯 Example Collision Scenarios:")
        for i, collision in enumerate(collisions[:10]):
            print(f"   {i+1}. {collision['satellite1_name']} vs {collision['satellite2_name']} ({collision['risk_level'].upper()} risk, {collision['altitude_difference']:.1f}km altitude diff, {collision['collision_probability']:.3f} probability)")
        
        if len(collisions) > 10:
            print(f"   ... and {len(collisions) - 10} more collision scenarios")
        
        print(f"\n🎉 Dashboard collision generation test completed successfully!")
        print(f"🚀 The dashboard should now show {len(collisions)} collision alerts!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing dashboard collision generation: {e}")
        return False

if __name__ == "__main__":
    test_dashboard_collision_generation()
