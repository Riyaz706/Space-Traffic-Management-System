#!/usr/bin/env python3
"""
AI-Powered Space Traffic Management System
Main Application Entry Point
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SpaceTrafficManager:
    """
    Main orchestrator for the Space Traffic Management System
    """
    
    def __init__(self):
        self.satellites = {}
        self.collision_alerts = []
        self.maneuver_plans = []
        self.is_running = False
        
    async def start_system(self):
        """Start the space traffic management system"""
        logger.info("🚀 Starting AI-Powered Space Traffic Management System")
        self.is_running = True
        
        try:
            # Initialize all components
            await self.initialize_components()
            
            # Start the main monitoring loop
            await self.monitoring_loop()
            
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down system...")
            await self.shutdown()
        except Exception as e:
            logger.error(f"❌ System error: {e}")
            await self.shutdown()
    
    async def initialize_components(self):
        """Initialize all system components"""
        logger.info("🔧 Initializing system components...")
        
        # Initialize data collection
        from src.data_collection.satellite_data import SatelliteDataCollector
        self.data_collector = SatelliteDataCollector()
        
        # Initialize orbit propagation
        from src.orbit_propagation.orbit_engine import OrbitPropagationEngine
        self.orbit_engine = OrbitPropagationEngine()
        
        # Initialize collision detection
        from src.collision_detection.collision_detector import CollisionDetector
        self.collision_detector = CollisionDetector()
        
        # Initialize maneuver planning
        from src.maneuver_planning.maneuver_planner import ManeuverPlanner
        self.maneuver_planner = ManeuverPlanner()
        
        # Initialize visualization
        from src.visualization.space_visualizer import SpaceVisualizer
        self.visualizer = SpaceVisualizer()
        
        logger.info("✅ All components initialized successfully")
    
    async def monitoring_loop(self):
        """Main monitoring loop for satellite tracking and collision detection"""
        logger.info("👀 Starting satellite monitoring loop...")
        
        while self.is_running:
            try:
                # Step 1: Collect current satellite data (now from JSON file)
                logger.info("📡 Collecting satellite data from JSON file...")
                satellite_data = await self.data_collector.collect_data()
                self.satellites = satellite_data
                logger.info(f"✅ Loaded {len(satellite_data)} satellites/debris objects")
                
                # Step 2: Propagate orbits to predict future positions
                logger.info("🔮 Propagating orbits for all objects...")
                future_positions = await self.orbit_engine.propagate_orbits(satellite_data)
                logger.info(f"✅ Generated {len(future_positions)} future position predictions")
                
                # Step 3: Detect potential collisions
                logger.info("🚨 Checking for potential collisions...")
                collisions = await self.collision_detector.detect_collisions(future_positions)
                
                if collisions:
                    logger.warning(f"⚠️ Found {len(collisions)} potential collisions!")
                    self.collision_alerts.extend(collisions)
                    
                    # Step 4: Plan avoidance maneuvers
                    logger.info("🧭 Planning avoidance maneuvers...")
                    maneuvers = await self.maneuver_planner.plan_maneuvers(collisions)
                    self.maneuver_plans.extend(maneuvers)
                    logger.info(f"✅ Planned {len(maneuvers)} avoidance maneuvers")
                    
                    # Step 5: Update visualization
                    await self.visualizer.update_visualization(
                        satellites=satellite_data,
                        collisions=collisions,
                        maneuvers=maneuvers
                    )
                else:
                    logger.info("✅ No collision risks detected in this cycle")
                
                # Wait before next monitoring cycle (simulate real-time updates)
                await asyncio.sleep(10)  # 10-second update cycle
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def shutdown(self):
        """Gracefully shutdown the system"""
        logger.info("🛑 Shutting down Space Traffic Management System...")
        self.is_running = False
        
        # Cleanup resources
        if hasattr(self, 'data_collector'):
            await self.data_collector.cleanup()
        
        logger.info("✅ System shutdown complete")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "status": "running" if self.is_running else "stopped",
            "satellites_tracked": len(self.satellites),
            "active_alerts": len(self.collision_alerts),
            "planned_maneuvers": len(self.maneuver_plans),
            "last_update": datetime.now().isoformat()
        }

async def main():
    """Main entry point"""
    # Create and start the space traffic manager
    manager = SpaceTrafficManager()
    await manager.start_system()

if __name__ == "__main__":
    # Run the main application
    asyncio.run(main())
