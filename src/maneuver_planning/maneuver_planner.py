"""
Maneuver Planning Module
Designs fuel-efficient collision avoidance maneuvers (CAMs) for satellites
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import logging
from scipy.optimize import minimize
import cvxpy as cp

logger = logging.getLogger(__name__)

class ManeuverPlanner:
    """
    AI-powered maneuver planning system
    Designs fuel-efficient collision avoidance maneuvers
    """
    
    def __init__(self):
        self.earth_radius = 6378.137  # km
        self.mu_earth = 398600.4418  # km³/s²
        self.max_delta_v = 100.0  # m/s - maximum maneuver capability
        self.min_safety_distance = 5.0  # km - minimum safe distance after maneuver
        
    async def plan_maneuvers(self, collisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Plan collision avoidance maneuvers for detected collisions
        
        Args:
            collisions: List of detected potential collisions
            
        Returns:
            List of planned maneuvers
        """
        logger.info(f"🧭 Planning maneuvers for {len(collisions)} potential collisions...")
        
        maneuvers = []
        
        for collision in collisions:
            try:
                # Plan maneuver for this collision
                maneuver = await self._plan_single_maneuver(collision)
                if maneuver:
                    maneuvers.append(maneuver)
                    logger.info(f"✅ Maneuver planned for {collision['satellite1_id']} vs {collision['satellite2_id']}")
                
            except Exception as e:
                logger.error(f"❌ Error planning maneuver for collision: {e}")
                continue
        
        logger.info(f"✅ Maneuver planning complete. Planned {len(maneuvers)} maneuvers")
        return maneuvers
    
    async def _plan_single_maneuver(self, collision: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Plan a single collision avoidance maneuver
        
        Args:
            collision: Collision data
            
        Returns:
            Planned maneuver data
        """
        try:
            # Extract collision information
            sat1_id = collision['satellite1_id']
            sat2_id = collision['satellite2_id']
            closest_approach = collision['closest_approach']
            risk_level = collision['risk_level']
            
            # Determine which satellite to maneuver
            # Generally, maneuver the more maneuverable satellite (active vs debris)
            maneuver_sat_id = self._select_maneuver_satellite(collision)
            
            if not maneuver_sat_id:
                logger.warning(f"⚠️ No suitable satellite for maneuver: {sat1_id} vs {sat2_id}")
                return None
            
            # Calculate optimal maneuver
            maneuver = await self._calculate_optimal_maneuver(
                collision, maneuver_sat_id, closest_approach
            )
            
            if maneuver:
                # Add collision context to maneuver
                maneuver.update({
                    'collision_id': f"{sat1_id}_{sat2_id}_{closest_approach['time']}",
                    'satellite1_id': sat1_id,
                    'satellite2_id': sat2_id,
                    'risk_level': risk_level,
                    'planned_time': datetime.now().isoformat(),
                    'execution_priority': self._calculate_execution_priority(collision)
                })
            
            return maneuver
            
        except Exception as e:
            logger.error(f"❌ Error in single maneuver planning: {e}")
            return None
    
    def _select_maneuver_satellite(self, collision: Dict[str, Any]) -> Optional[str]:
        """
        Select which satellite to maneuver based on various factors
        """
        sat1_id = collision['satellite1_id']
        sat2_id = collision['satellite2_id']
        
        # Priority order:
        # 1. Active satellites over debris
        # 2. Lower altitude satellites (easier to maneuver)
        # 3. Satellites with more fuel/maneuver capability
        
        # For now, use simple heuristics
        # In production, this would consider:
        # - Satellite maneuverability
        # - Fuel levels
        # - Mission priority
        # - Operational constraints
        
        # Prefer maneuvering active satellites over debris
        if 'DEB' in collision['satellite1_name'] and 'DEB' not in collision['satellite2_name']:
            return sat2_id
        elif 'DEB' in collision['satellite2_name'] and 'DEB' not in collision['satellite1_name']:
            return sat1_id
        
        # If both are same type, prefer the one with lower altitude
        alt1 = collision['closest_approach']['position1']['altitude']
        alt2 = collision['closest_approach']['position2']['altitude']
        
        if alt1 < alt2:
            return sat1_id
        else:
            return sat2_id
    
    async def _calculate_optimal_maneuver(self, collision: Dict[str, Any], 
                                        maneuver_sat_id: str,
                                        closest_approach: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Calculate optimal collision avoidance maneuver
        
        Args:
            collision: Collision data
            maneuver_sat_id: ID of satellite to maneuver
            closest_approach: Closest approach data
            
        Returns:
            Optimal maneuver parameters
        """
        try:
            # Get current orbital state
            if maneuver_sat_id == collision['satellite1_id']:
                current_pos = closest_approach['position1']
            else:
                current_pos = closest_approach['position2']
            
            # Calculate required position change to avoid collision
            required_displacement = self._calculate_required_displacement(
                collision, maneuver_sat_id, closest_approach
            )
            
            if not required_displacement:
                return None
            
            # Optimize maneuver for minimum fuel consumption
            optimal_maneuver = self._optimize_maneuver(
                current_pos, required_displacement, closest_approach
            )
            
            if optimal_maneuver:
                # Calculate maneuver execution time
                execution_time = self._calculate_execution_time(
                    closest_approach['time'], optimal_maneuver
                )
                
                optimal_maneuver.update({
                    'execution_time': execution_time,
                    'maneuver_satellite_id': maneuver_sat_id,
                    'maneuver_type': self._classify_maneuver_type(optimal_maneuver),
                    'fuel_consumption': self._estimate_fuel_consumption(optimal_maneuver),
                    'safety_margin': self._calculate_safety_margin(optimal_maneuver, collision)
                })
            
            return optimal_maneuver
            
        except Exception as e:
            logger.error(f"❌ Error calculating optimal maneuver: {e}")
            return None
    
    def _calculate_required_displacement(self, collision: Dict[str, Any], 
                                       maneuver_sat_id: str,
                                       closest_approach: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """
        Calculate required displacement to avoid collision
        """
        try:
            # Get positions at closest approach
            pos1 = closest_approach['position1']
            pos2 = closest_approach['position2']
            
            # Calculate current separation vector
            separation_vector = {
                'x': pos1['x'] - pos2['x'],
                'y': pos1['y'] - pos2['y'],
                'z': pos1['z'] - pos2['z']
            }
            
            # Normalize separation vector
            separation_magnitude = np.sqrt(
                separation_vector['x']**2 + 
                separation_vector['y']**2 + 
                separation_vector['z']**2
            )
            
            if separation_magnitude == 0:
                return None
            
            # Calculate required displacement to achieve minimum safe distance
            current_distance = separation_magnitude
            required_distance = self.min_safety_distance
            
            if current_distance >= required_distance:
                return None  # Already safe
            
            # Calculate displacement needed
            displacement_magnitude = required_distance - current_distance
            
            # Direction of displacement (away from other satellite)
            if maneuver_sat_id == collision['satellite1_id']:
                # Move satellite 1 away from satellite 2
                displacement_direction = {
                    'x': separation_vector['x'] / separation_magnitude,
                    'y': separation_vector['y'] / separation_magnitude,
                    'z': separation_vector['z'] / separation_magnitude
                }
            else:
                # Move satellite 2 away from satellite 1
                displacement_direction = {
                    'x': -separation_vector['x'] / separation_magnitude,
                    'y': -separation_vector['y'] / separation_magnitude,
                    'z': -separation_vector['z'] / separation_magnitude
                }
            
            # Calculate required displacement vector
            required_displacement = {
                'x': displacement_direction['x'] * displacement_magnitude,
                'y': displacement_direction['y'] * displacement_magnitude,
                'z': displacement_direction['z'] * displacement_magnitude
            }
            
            return required_displacement
            
        except Exception as e:
            logger.error(f"❌ Error calculating required displacement: {e}")
            return None
    
    def _optimize_maneuver(self, current_pos: Dict[str, float], 
                          required_displacement: Dict[str, float],
                          closest_approach: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Optimize maneuver for minimum fuel consumption
        """
        try:
            # Extract current velocity
            current_velocity = current_pos['velocity']
            
            # Calculate required velocity change (delta-v)
            # This is a simplified calculation - in reality would use orbital mechanics
            time_to_closest = self._calculate_time_to_closest(closest_approach['time'])
            
            if time_to_closest <= 0:
                return None
            
            # Calculate required velocity change to achieve displacement
            required_delta_v = {
                'x': required_displacement['x'] / time_to_closest,
                'y': required_displacement['y'] / time_to_closest,
                'z': required_displacement['z'] / time_to_closest
            }
            
            # Calculate total delta-v magnitude
            delta_v_magnitude = np.sqrt(
                required_delta_v['x']**2 + 
                required_delta_v['y']**2 + 
                required_delta_v['z']**2
            )
            
            # Check if maneuver is feasible
            if delta_v_magnitude > self.max_delta_v:
                logger.warning(f"⚠️ Required delta-v ({delta_v_magnitude:.2f} m/s) exceeds maximum capability ({self.max_delta_v} m/s)")
                return None
            
            # Optimize maneuver timing and direction
            optimized_maneuver = self._optimize_timing_and_direction(
                current_pos, required_displacement, delta_v_magnitude, time_to_closest
            )
            
            return optimized_maneuver
            
        except Exception as e:
            logger.error(f"❌ Error optimizing maneuver: {e}")
            return None
    
    def _optimize_timing_and_direction(self, current_pos: Dict[str, float],
                                     required_displacement: Dict[str, float],
                                     delta_v_magnitude: float,
                                     time_to_closest: float) -> Dict[str, Any]:
        """
        Optimize maneuver timing and direction for minimum fuel consumption
        """
        try:
            # For simplicity, use immediate maneuver
            # In production, this would optimize the timing based on:
            # - Orbital dynamics
            # - Fuel efficiency
            # - Mission constraints
            
            # Calculate optimal burn direction
            # In Hohmann transfer, burns are typically in the orbital plane
            # For collision avoidance, we want to maximize separation
            
            # Simple optimization: maximize displacement in the direction of required movement
            displacement_magnitude = np.sqrt(required_displacement['x']**2 + required_displacement['y']**2 + required_displacement['z']**2)
            
            if displacement_magnitude == 0:
                # If no displacement needed, use default direction
                optimal_direction = {'x': 1.0, 'y': 0.0, 'z': 0.0}
            else:
                optimal_direction = {
                    'x': required_displacement['x'] / displacement_magnitude,
                    'y': required_displacement['y'] / displacement_magnitude,
                    'z': required_displacement['z'] / displacement_magnitude
                }
            
            return {
                'delta_v_magnitude': delta_v_magnitude,
                'delta_v_direction': optimal_direction,
                'burn_duration': self._calculate_burn_duration(delta_v_magnitude),
                'maneuver_timing': 'immediate',  # Simplified
                'estimated_effectiveness': self._estimate_maneuver_effectiveness(delta_v_magnitude, time_to_closest)
            }
            
        except Exception as e:
            logger.error(f"❌ Error optimizing timing and direction: {e}")
            return None
    
    def _calculate_burn_duration(self, delta_v_magnitude: float) -> float:
        """Calculate burn duration based on delta-v and typical thruster performance"""
        # Typical thruster acceleration: 0.1-1.0 m/s²
        # For simplicity, assume 0.5 m/s²
        typical_acceleration = 0.5  # m/s²
        return delta_v_magnitude / typical_acceleration  # seconds
    
    def _estimate_maneuver_effectiveness(self, delta_v_magnitude: float, time_to_closest: float) -> float:
        """Estimate how effective the maneuver will be"""
        # Effectiveness based on:
        # - Delta-v magnitude (higher = more effective)
        # - Time to closest approach (more time = more effective)
        
        # Normalize factors
        delta_v_factor = min(1.0, delta_v_magnitude / self.max_delta_v)
        time_factor = min(1.0, time_to_closest / 24.0)  # 24 hours as reference
        
        # Combined effectiveness score
        effectiveness = 0.7 * delta_v_factor + 0.3 * time_factor
        
        return min(1.0, effectiveness)
    
    def _calculate_execution_time(self, closest_approach_time: str, maneuver: Dict[str, Any]) -> str:
        """Calculate when the maneuver should be executed"""
        try:
            closest_dt = datetime.fromisoformat(closest_approach_time)
            
            # Execute maneuver 1 hour before closest approach
            # In production, this would be optimized based on orbital dynamics
            execution_dt = closest_dt - timedelta(hours=1)
            
            # Ensure execution time is not in the past
            if execution_dt < datetime.now():
                execution_dt = datetime.now() + timedelta(minutes=30)
            
            return execution_dt.isoformat()
            
        except Exception as e:
            logger.error(f"❌ Error calculating execution time: {e}")
            return (datetime.now() + timedelta(minutes=30)).isoformat()
    
    def _calculate_time_to_closest(self, closest_time: str) -> float:
        """Calculate time to closest approach in seconds"""
        try:
            closest_dt = datetime.fromisoformat(closest_time)
            current_dt = datetime.now()
            time_diff = closest_dt - current_dt
            return time_diff.total_seconds()
        except:
            return 3600.0  # Default to 1 hour
    
    def _classify_maneuver_type(self, maneuver: Dict[str, Any]) -> str:
        """Classify the type of maneuver"""
        delta_v = maneuver['delta_v_magnitude']
        
        if delta_v < 1.0:
            return 'fine_adjustment'
        elif delta_v < 10.0:
            return 'minor_maneuver'
        elif delta_v < 50.0:
            return 'major_maneuver'
        else:
            return 'emergency_maneuver'
    
    def _estimate_fuel_consumption(self, maneuver: Dict[str, Any]) -> float:
        """Estimate fuel consumption for the maneuver"""
        # Simplified fuel estimation
        # In production, this would use specific thruster characteristics
        
        delta_v = maneuver['delta_v_magnitude']
        burn_duration = maneuver['burn_duration']
        
        # Assume specific impulse of 300 seconds (typical for chemical thrusters)
        specific_impulse = 300.0  # seconds
        g0 = 9.81  # m/s²
        
        # Tsiolkovsky rocket equation (simplified)
        # delta_v = Isp * g0 * ln(m0/mf)
        # For small maneuvers, fuel consumption ≈ delta_v / (Isp * g0)
        
        fuel_consumption = delta_v / (specific_impulse * g0)  # kg per kg of satellite mass
        
        return fuel_consumption
    
    def _calculate_safety_margin(self, maneuver: Dict[str, Any], collision: Dict[str, Any]) -> float:
        """Calculate safety margin after maneuver"""
        # Safety margin = how much extra distance we'll have beyond minimum safe distance
        current_distance = collision['closest_approach']['distance']
        required_distance = self.min_safety_distance
        
        # Estimate new distance after maneuver
        effectiveness = maneuver['estimated_effectiveness']
        displacement = required_distance - current_distance
        
        estimated_new_distance = current_distance + (displacement * effectiveness)
        safety_margin = estimated_new_distance - required_distance
        
        return max(0.0, safety_margin)
    
    def _calculate_execution_priority(self, collision: Dict[str, Any]) -> int:
        """Calculate execution priority for the maneuver"""
        # Priority factors:
        # - Risk level (high=1, medium=2, low=3)
        # - Time to closest approach (less time = higher priority)
        # - Collision probability
        
        risk_priority = {'high': 1, 'medium': 2, 'low': 3}
        base_priority = risk_priority.get(collision['risk_level'], 3)
        
        # Adjust for time to closest approach
        time_to_closest = collision['time_to_closest_approach']
        if time_to_closest < 1.0:  # Less than 1 hour
            time_factor = 3
        elif time_to_closest < 6.0:  # Less than 6 hours
            time_factor = 2
        else:
            time_factor = 1
        
        # Adjust for collision probability
        prob_factor = int(collision['collision_probability'] * 10) + 1
        
        # Final priority (lower number = higher priority)
        priority = base_priority * time_factor * prob_factor
        
        return priority
    
    def validate_maneuver(self, maneuver: Dict[str, Any]) -> bool:
        """Validate that a maneuver is safe and feasible"""
        try:
            # Check delta-v limits
            if maneuver['delta_v_magnitude'] > self.max_delta_v:
                return False
            
            # Check execution time
            execution_time = datetime.fromisoformat(maneuver['execution_time'])
            if execution_time < datetime.now():
                return False
            
            # Check safety margin
            if maneuver['safety_margin'] < 0.5:  # At least 0.5 km safety margin
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating maneuver: {e}")
            return False
