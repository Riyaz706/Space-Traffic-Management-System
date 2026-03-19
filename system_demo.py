"""
Space Traffic Management System - Complete Demonstration
Shows how all components work together to manage orbital traffic
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_collection.satellite_data import SatelliteDataCollector
from src.orbit_propagation.orbit_engine import OrbitPropagationEngine
from src.collision_detection.collision_detector import CollisionDetector
from src.maneuver_planning.maneuver_planner import ManeuverPlanner
from src.visualization.space_visualizer import SpaceVisualizer

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"🚀 {title}")
    print("=" * 70)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n📋 {title}")
    print("-" * 50)

async def demonstrate_complete_system():
    """Demonstrate the complete space traffic management system"""
    print_header("Space Traffic Management System - Complete Demonstration")
    
    print("\n🎯 This demonstration shows how our AI-powered system:")
    print("   1. Collects satellite data from multiple sources")
    print("   2. Propagates orbits to predict future positions")
    print("   3. Detects potential collisions using AI")
    print("   4. Plans fuel-efficient avoidance maneuvers")
    print("   5. Visualizes the entire system in real-time")
    
    # Initialize all components
    print_section("Initializing System Components")
    
    data_collector = SatelliteDataCollector()
    orbit_engine = OrbitPropagationEngine()
    collision_detector = CollisionDetector()
    maneuver_planner = ManeuverPlanner()
    visualizer = SpaceVisualizer()
    
    print("✅ All system components initialized successfully")
    
    # Step 1: Data Collection
    print_section("Step 1: Satellite Data Collection")
    
    print("🛰️ Collecting satellite data from multiple sources...")
    try:
        satellite_data = await data_collector.collect_data()
        print(f"✅ Collected data for {len(satellite_data)} objects")
        
        # Show sample data
        sample_satellites = list(satellite_data.keys())[:3]
        for sat_id in sample_satellites:
            sat_data = satellite_data[sat_id]
            print(f"   📡 {sat_id}: {sat_data.get('name', 'Unknown')} at {sat_data.get('altitude', 0)}km")
            
    except Exception as e:
        print(f"⚠️ Using sample data due to: {e}")
        # Create sample data
        satellite_data = {
            "ISS": {
                "object_type": "satellite",
                "name": "International Space Station",
                "altitude": 408,
                "inclination": 51.6,
                "status": "active"
            },
            "STARLINK-1234": {
                "object_type": "satellite", 
                "name": "Starlink Satellite 1234",
                "altitude": 550,
                "inclination": 53.0,
                "status": "active"
            },
            "DEBRIS-001": {
                "object_type": "debris",
                "name": "Rocket Body Debris",
                "altitude": 425,
                "inclination": 52.0,
                "status": "inactive"
            }
        }
        print(f"✅ Using sample data for {len(satellite_data)} objects")
    
    # Step 2: Orbit Propagation
    print_section("Step 2: Orbit Propagation")
    
    print("🔄 Propagating orbits to predict future positions...")
    try:
        future_positions = await orbit_engine.propagate_orbits(satellite_data)
        print(f"✅ Propagated orbits for {len(future_positions)} objects")
        
        # Show propagation results
        for sat_id, positions in list(future_positions.items())[:2]:
            if positions:
                latest_pos = positions[-1]
                print(f"   📍 {sat_id}: Position at {latest_pos.get('time', 'Unknown')}")
                
    except Exception as e:
        print(f"⚠️ Orbit propagation simulation: {e}")
        future_positions = satellite_data  # Use current positions as fallback
    
    # Step 3: Collision Detection
    print_section("Step 3: AI-Powered Collision Detection")
    
    print("🚨 Analyzing orbital trajectories for potential collisions...")
    try:
        collisions = await collision_detector.detect_collisions(future_positions)
        print(f"✅ Detected {len(collisions)} potential collision scenarios")
        
        if collisions:
            for i, collision in enumerate(collisions[:3], 1):
                risk_level = collision.get('risk_level', 'unknown')
                probability = collision.get('collision_probability', 0)
                distance = collision.get('closest_approach', {}).get('distance', 0)
                
                print(f"   {i}. {collision.get('satellite1_name', 'Unknown')} vs {collision.get('satellite2_name', 'Unknown')}")
                print(f"      Risk: {risk_level.upper()}, Probability: {probability:.1%}, Distance: {distance:.2f}km")
        else:
            print("   🎉 No collision threats detected!")
            
    except Exception as e:
        print(f"⚠️ Collision detection simulation: {e}")
        # Create sample collisions for demonstration
        collisions = [
            {
                "satellite1_name": "ISS",
                "satellite2_name": "DEBRIS-001", 
                "risk_level": "high",
                "collision_probability": 0.85,
                "closest_approach": {"distance": 0.5, "time": "2024-01-15T14:30:00Z"},
                "time_to_closest_approach": 2.5
            }
        ]
        print(f"✅ Demo: {len(collisions)} collision scenario(s) for demonstration")
    
    # Step 4: Maneuver Planning
    print_section("Step 4: Maneuver Planning")
    
    if collisions:
        print("🧭 Planning collision avoidance maneuvers...")
        try:
            maneuvers = await maneuver_planner.plan_maneuvers(collisions)
            print(f"✅ Generated {len(maneuvers)} maneuver plans")
            
            if maneuvers:
                total_delta_v = sum(m.get('delta_v_magnitude', 0) for m in maneuvers)
                total_fuel = sum(m.get('fuel_consumption', 0) for m in maneuvers)
                
                print(f"   📊 Total Delta-V: {total_delta_v:.2f} m/s")
                print(f"   ⛽ Total Fuel: {total_fuel:.4f} kg")
                
                for i, maneuver in enumerate(maneuvers, 1):
                    print(f"   {i}. {maneuver.get('maneuver_satellite_id', 'Unknown')}: {maneuver.get('delta_v_magnitude', 0):.2f} m/s")
            else:
                print("   ⚠️ No maneuvers generated (simulation mode)")
                
        except Exception as e:
            print(f"⚠️ Maneuver planning simulation: {e}")
            maneuvers = []
    else:
        print("✅ No maneuvers needed - no collision threats")
        maneuvers = []
    
    # Step 5: Visualization
    print_section("Step 5: System Visualization")
    
    print("🎨 Updating visualization with current data...")
    try:
        await visualizer.update_visualization(
            satellites=future_positions,
            collisions=collisions,
            maneuvers=maneuvers
        )
        print("✅ Visualization updated successfully")
        
        # Get visualization stats
        stats = visualizer.get_visualization_stats()
        print(f"   📈 Objects tracked: {stats.get('total_satellites', 0)}")
        print(f"   🚨 Collisions detected: {stats.get('total_collisions', 0)}")
        print(f"   🧭 Maneuvers planned: {stats.get('total_maneuvers', 0)}")
        
    except Exception as e:
        print(f"⚠️ Visualization update: {e}")
    
    # System Summary
    print_section("System Summary")
    
    print("📊 Current System Status:")
    print(f"   🛰️ Objects Tracked: {len(satellite_data)}")
    print(f"   🚨 Active Alerts: {len(collisions)}")
    print(f"   🧭 Planned Maneuvers: {len(maneuvers)}")
    
    # Calculate system health
    health_score = 95
    if collisions:
        high_risk = sum(1 for c in collisions if c.get('risk_level') == 'high')
        health_score -= high_risk * 15
    
    print(f"   💚 System Health: {health_score}%")
    
    # Recommendations
    print("\n🎯 System Recommendations:")
    if collisions:
        high_risk_count = sum(1 for c in collisions if c.get('risk_level') == 'high')
        if high_risk_count > 0:
            print(f"   🚨 IMMEDIATE ACTION: {high_risk_count} high-risk collision(s) detected")
            print("   🧭 Execute planned maneuvers immediately")
        else:
            print("   ⚠️ Monitor medium/low risk scenarios")
    else:
        print("   ✅ All clear - continue normal operations")
    
    print("   📊 Continue monitoring orbital traffic")
    print("   🔄 Regular data updates recommended")
    
    # Dashboard Information
    print_section("Accessing the Dashboard")
    
    print("🌐 The enhanced dashboard is now running!")
    print("   📱 Open your web browser and go to:")
    print("   🔗 http://localhost:8501")
    print("\n🎮 Dashboard Features:")
    print("   • Real-time 3D space visualization")
    print("   • Interactive collision alerts")
    print("   • Maneuver planning and execution")
    print("   • Analytics and reporting")
    print("   • System settings and configuration")
    
    print("\n🎭 Demo Data:")
    print("   • Click '🎭 Load Demo Data' in the sidebar")
    print("   • View the '🚨 Alert Center' tab for collision scenarios")
    print("   • Check the '🧭 Maneuver Control' tab for planned maneuvers")
    
    print("\n✅ Space Traffic Management System demonstration completed!")
    print("🚀 Your AI-powered orbital collision prevention system is ready!")

def main():
    """Main function to run the complete demonstration"""
    asyncio.run(demonstrate_complete_system())

if __name__ == "__main__":
    main()
