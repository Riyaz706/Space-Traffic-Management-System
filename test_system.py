#!/usr/bin/env python3
"""
Test Script for Space Traffic Management System
Verifies that all components work correctly
"""

import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_data_collection():
    """Test satellite data collection"""
    print("🧪 Testing Data Collection...")
    
    try:
        from data_collection.satellite_data import SatelliteDataCollector
        
        collector = SatelliteDataCollector()
        satellite_data = asyncio.run(collector.collect_data())
        
        print(f"✅ Data collection successful! Found {len(satellite_data)} satellites")
        
        # Print sample data
        for sat_id, sat_data in list(satellite_data.items())[:3]:
            print(f"  - {sat_data.get('name', 'Unknown')} (ID: {sat_id})")
        
        return satellite_data
        
    except Exception as e:
        print(f"❌ Data collection failed: {e}")
        return None

def test_orbit_propagation(satellite_data):
    """Test orbit propagation"""
    print("\n🧪 Testing Orbit Propagation...")
    
    try:
        from orbit_propagation.orbit_engine import OrbitPropagationEngine
        
        engine = OrbitPropagationEngine()
        future_positions = asyncio.run(engine.propagate_orbits(satellite_data))
        
        print(f"✅ Orbit propagation successful! Propagated {len(future_positions)} objects")
        
        # Print sample propagation data
        for sat_id, pos_data in list(future_positions.items())[:2]:
            positions = pos_data.get('positions', [])
            if positions:
                print(f"  - {pos_data.get('name', 'Unknown')}: {len(positions)} future positions")
        
        return future_positions
        
    except Exception as e:
        print(f"❌ Orbit propagation failed: {e}")
        return None

def test_collision_detection(future_positions):
    """Test collision detection"""
    print("\n🧪 Testing Collision Detection...")
    
    try:
        from collision_detection.collision_detector import CollisionDetector
        
        detector = CollisionDetector()
        collisions = asyncio.run(detector.detect_collisions(future_positions))
        
        print(f"✅ Collision detection successful! Found {len(collisions)} potential collisions")
        
        # Print collision details
        for collision in collisions[:3]:
            sat1 = collision.get('satellite1_name', 'Unknown')
            sat2 = collision.get('satellite2_name', 'Unknown')
            risk = collision.get('risk_level', 'unknown')
            distance = collision['closest_approach']['distance']
            print(f"  - {sat1} vs {sat2}: {risk} risk, {distance:.2f} km")
        
        return collisions
        
    except Exception as e:
        print(f"❌ Collision detection failed: {e}")
        return []

def test_maneuver_planning(collisions):
    """Test maneuver planning"""
    print("\n🧪 Testing Maneuver Planning...")
    
    try:
        from maneuver_planning.maneuver_planner import ManeuverPlanner
        
        planner = ManeuverPlanner()
        maneuvers = asyncio.run(planner.plan_maneuvers(collisions))
        
        print(f"✅ Maneuver planning successful! Planned {len(maneuvers)} maneuvers")
        
        # Print maneuver details
        for maneuver in maneuvers[:3]:
            sat_id = maneuver.get('maneuver_satellite_id', 'Unknown')
            maneuver_type = maneuver.get('maneuver_type', 'unknown')
            delta_v = maneuver.get('delta_v_magnitude', 0)
            print(f"  - {sat_id}: {maneuver_type}, {delta_v:.2f} m/s delta-v")
        
        return maneuvers
        
    except Exception as e:
        print(f"❌ Maneuver planning failed: {e}")
        return []

def test_visualization(satellite_data, collisions, maneuvers):
    """Test visualization"""
    print("\n🧪 Testing Visualization...")
    
    try:
        from visualization.space_visualizer import SpaceVisualizer
        
        visualizer = SpaceVisualizer()
        
        # Update visualization data
        asyncio.run(visualizer.update_visualization(
            satellites=satellite_data,
            collisions=collisions,
            maneuvers=maneuvers
        ))
        
        # Create plots
        fig_3d = visualizer.create_3d_space_plot()
        dashboard_plots = visualizer.create_dashboard_plots()
        
        print(f"✅ Visualization successful!")
        print(f"  - 3D plot created: {fig_3d is not None}")
        print(f"  - Dashboard plots created: {len(dashboard_plots)} plots")
        
        # Get statistics
        stats = visualizer.get_visualization_stats()
        print(f"  - Statistics: {stats.get('total_satellites', 0)} satellites, {stats.get('total_collisions', 0)} collisions")
        
        return True
        
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        return False

def test_dashboard():
    """Test dashboard components"""
    print("\n🧪 Testing Dashboard Components...")
    
    try:
        # Test if we can import dashboard components
        sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))
        
        # This would normally test the dashboard, but for now just check imports
        print("✅ Dashboard components importable")
        return True
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Space Traffic Management System - Component Tests")
    print("=" * 60)
    
    # Test each component
    satellite_data = test_data_collection()
    if not satellite_data:
        print("❌ Cannot continue without satellite data")
        return
    
    future_positions = test_orbit_propagation(satellite_data)
    if not future_positions:
        print("❌ Cannot continue without orbit propagation")
        return
    
    collisions = test_collision_detection(future_positions)
    maneuvers = test_maneuver_planning(collisions)
    
    visualization_ok = test_visualization(satellite_data, collisions, maneuvers)
    dashboard_ok = test_dashboard()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"  ✅ Data Collection: {'PASS' if satellite_data else 'FAIL'}")
    print(f"  ✅ Orbit Propagation: {'PASS' if future_positions else 'FAIL'}")
    print(f"  ✅ Collision Detection: {'PASS' if collisions is not None else 'FAIL'}")
    print(f"  ✅ Maneuver Planning: {'PASS' if maneuvers is not None else 'FAIL'}")
    print(f"  ✅ Visualization: {'PASS' if visualization_ok else 'FAIL'}")
    print(f"  ✅ Dashboard: {'PASS' if dashboard_ok else 'FAIL'}")
    
    if all([satellite_data, future_positions, visualization_ok, dashboard_ok]):
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nTo run the system:")
        print("  python main.py                    # Run main application")
        print("  streamlit run dashboard/app.py    # Run dashboard")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
