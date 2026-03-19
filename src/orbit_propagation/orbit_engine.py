"""
Orbit Propagation Engine
Calculates future satellite positions using orbital mechanics
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging
from sgp4.api import Satrec, SGP4_ERRORS
from sgp4.earth_gravity import wgs72

logger = logging.getLogger(__name__)

class OrbitPropagationEngine:
    """
    Orbit propagation engine using SGP4 and orbital mechanics
    Calculates future positions of satellites and debris
    """
    
    def __init__(self):
        self.earth_radius = 6378.137  # km
        self.mu_earth = 398600.4418  # km³/s² (Earth's gravitational parameter)
        self.propagation_horizon = 7  # days
        
    async def propagate_orbits(self, satellite_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Propagate orbits for all satellites to predict future positions
        
        Args:
            satellite_data: Dictionary of satellite data
            
        Returns:
            Dictionary with future positions for each satellite
        """
        logger.info(f"🔮 Propagating orbits for {len(satellite_data)} objects...")
        
        future_positions = {}
        
        for satellite_id, sat_data in satellite_data.items():
            try:
                # Propagate orbit for this satellite
                positions = await self._propagate_single_orbit(satellite_id, sat_data)
                future_positions[satellite_id] = positions
                
            except Exception as e:
                logger.warning(f"⚠️ Error propagating orbit for {satellite_id}: {e}")
                continue
        
        logger.info(f"✅ Orbit propagation complete for {len(future_positions)} objects")
        return future_positions
    
    async def _propagate_single_orbit(self, satellite_id: str, sat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Propagate orbit for a single satellite
        
        Args:
            satellite_id: Satellite identifier
            sat_data: Satellite orbital data
            
        Returns:
            Dictionary with future positions and times
        """
        try:
            # Check if this is real-time data
            if sat_data.get('real_time', False):
                return await self._propagate_realtime(satellite_id, sat_data)
            
            # Try SGP4 propagation if TLE data is available
            elif 'tle_line1' in sat_data and 'tle_line2' in sat_data:
                return await self._propagate_sgp4(satellite_id, sat_data)
            else:
                # Use simplified orbital mechanics for sample data
                return await self._propagate_simplified(satellite_id, sat_data)
                
        except Exception as e:
            logger.error(f"❌ Error in orbit propagation for {satellite_id}: {e}")
            return self._generate_fallback_positions(satellite_id, sat_data)
    
    async def _propagate_realtime(self, satellite_id: str, sat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Propagate real-time satellite positions"""
        try:
            positions = []
            current_time = datetime.now()
            
            # Get current position from real-time data
            if 'latitude' in sat_data and 'longitude' in sat_data:
                # Convert lat/lon to cartesian coordinates
                lat = np.radians(sat_data['latitude'])
                lon = np.radians(sat_data['longitude'])
                alt = sat_data.get('altitude', 408)  # km
                
                # Convert to cartesian coordinates
                radius = self.earth_radius + alt
                x = radius * np.cos(lat) * np.cos(lon)
                y = radius * np.cos(lat) * np.sin(lon)
                z = radius * np.sin(lat)
                
                # Add current position
                positions.append({
                    'time': current_time.isoformat(),
                    'x': x,
                    'y': y,
                    'z': z,
                    'latitude': sat_data['latitude'],
                    'longitude': sat_data['longitude'],
                    'altitude': alt,
                    'velocity': 7.66  # Typical orbital velocity for ISS
                })
                
                # Generate future positions based on orbital period
                period = sat_data.get('period', 92.7)  # minutes
                period_seconds = period * 60
                
                for i in range(1, self.propagation_horizon * 24 * 4):  # Every 15 minutes
                    future_time = current_time + timedelta(minutes=i * 15)
                    
                    # Simple orbital motion (circular orbit approximation)
                    angle_change = (i * 15 * 60) / period_seconds * 2 * np.pi
                    
                    # Rotate position around Earth's axis
                    new_lon = (lon + angle_change) % (2 * np.pi)
                    
                    # Convert to cartesian
                    new_x = radius * np.cos(lat) * np.cos(new_lon)
                    new_y = radius * np.cos(lat) * np.sin(new_lon)
                    new_z = radius * np.sin(lat)
                    
                    positions.append({
                        'time': future_time.isoformat(),
                        'x': new_x,
                        'y': new_y,
                        'z': new_z,
                        'latitude': np.degrees(lat),
                        'longitude': np.degrees(new_lon),
                        'altitude': alt,
                        'velocity': 7.66
                    })
            
            return {
                'satellite_id': satellite_id,
                'name': sat_data.get('name', 'Unknown'),
                'positions': positions,
                'propagation_method': 'Real-time',
                'last_updated': current_time.isoformat(),
                'data_source': sat_data.get('data_source', 'Real-time API')
            }
            
        except Exception as e:
            logger.error(f"❌ Real-time propagation error for {satellite_id}: {e}")
            return self._generate_fallback_positions(satellite_id, sat_data)
    
    async def _propagate_sgp4(self, satellite_id: str, sat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Propagate using SGP4 algorithm with TLE data"""
        try:
            # Create SGP4 satellite object
            sat = Satrec.twoline2rv(sat_data['tle_line1'], sat_data['tle_line2'], wgs72)
            
            if sat.error != 0:
                raise ValueError(f"SGP4 error: {SGP4_ERRORS[sat.error]}")
            
            # Generate future positions
            positions = []
            current_time = datetime.now()
            
            for hours in range(0, self.propagation_horizon * 24, 6):  # Every 6 hours
                future_time = current_time + timedelta(hours=hours)
                
                # Convert to Julian date
                jd = self._datetime_to_jd(future_time)
                
                # Propagate position
                e, r, v = sat.sgp4(jd, 0.0)
                
                if e == 0:  # No error
                    # Convert to cartesian coordinates (km)
                    x, y, z = r[0], r[1], r[2]
                    
                    # Convert to spherical coordinates
                    lat, lon, alt = self._cartesian_to_spherical(x, y, z)
                    
                    positions.append({
                        'time': future_time.isoformat(),
                        'x': x,
                        'y': y,
                        'z': z,
                        'latitude': lat,
                        'longitude': lon,
                        'altitude': alt,
                        'velocity': np.linalg.norm(v)
                    })
            
            return {
                'satellite_id': satellite_id,
                'name': sat_data.get('name', 'Unknown'),
                'positions': positions,
                'propagation_method': 'SGP4',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ SGP4 propagation error for {satellite_id}: {e}")
            return self._generate_fallback_positions(satellite_id, sat_data)
    
    async def _propagate_simplified(self, satellite_id: str, sat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Propagate using simplified orbital mechanics for sample data"""
        try:
            # Extract orbital elements
            altitude = sat_data.get('altitude', 500)  # km
            period = sat_data.get('period', 95)  # minutes
            inclination = np.radians(sat_data.get('inclination', 45))
            
            # Calculate orbital parameters
            semi_major_axis = self.earth_radius + altitude
            mean_motion = 2 * np.pi / (period * 60)  # rad/s
            
            positions = []
            current_time = datetime.now()
            
            for hours in range(0, self.propagation_horizon * 24, 6):  # Every 6 hours
                future_time = current_time + timedelta(hours=hours)
                
                # Calculate mean anomaly
                time_diff = hours * 3600  # seconds
                mean_anomaly = mean_motion * time_diff
                
                # Simplified position calculation (circular orbit approximation)
                # For more accuracy, we'd solve Kepler's equation
                true_anomaly = mean_anomaly
                
                # Calculate position in orbital plane
                r = semi_major_axis
                x_orbital = r * np.cos(true_anomaly)
                y_orbital = r * np.sin(true_anomaly)
                z_orbital = 0
                
                # Transform to Earth-fixed coordinates (simplified)
                # In reality, we'd need proper coordinate transformations
                x = x_orbital * np.cos(inclination)
                y = y_orbital
                z = x_orbital * np.sin(inclination)
                
                # Convert to spherical coordinates
                lat, lon, alt = self._cartesian_to_spherical(x, y, z)
                
                positions.append({
                    'time': future_time.isoformat(),
                    'x': x,
                    'y': y,
                    'z': z,
                    'latitude': lat,
                    'longitude': lon,
                    'altitude': alt,
                    'velocity': np.sqrt(self.mu_earth / r)  # Orbital velocity
                })
            
            return {
                'satellite_id': satellite_id,
                'name': sat_data.get('name', 'Unknown'),
                'positions': positions,
                'propagation_method': 'Simplified',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Simplified propagation error for {satellite_id}: {e}")
            return self._generate_fallback_positions(satellite_id, sat_data)
    
    def _generate_fallback_positions(self, satellite_id: str, sat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback positions when propagation fails"""
        positions = []
        current_time = datetime.now()
        
        for hours in range(0, self.propagation_horizon * 24, 6):
            future_time = current_time + timedelta(hours=hours)
            
            # Generate random positions as fallback
            positions.append({
                'time': future_time.isoformat(),
                'x': np.random.uniform(-8000, 8000),
                'y': np.random.uniform(-8000, 8000),
                'z': np.random.uniform(-8000, 8000),
                'latitude': np.random.uniform(-90, 90),
                'longitude': np.random.uniform(-180, 180),
                'altitude': sat_data.get('altitude', 500),
                'velocity': np.random.uniform(7, 8)  # km/s
            })
        
        return {
            'satellite_id': satellite_id,
            'name': sat_data.get('name', 'Unknown'),
            'positions': positions,
            'propagation_method': 'Fallback',
            'last_updated': datetime.now().isoformat()
        }
    
    def _datetime_to_jd(self, dt: datetime) -> float:
        """Convert datetime to Julian date"""
        # Simplified conversion - for production use astropy.time
        year = dt.year
        month = dt.month
        day = dt.day
        hour = dt.hour
        minute = dt.minute
        second = dt.second
        
        if month <= 2:
            year -= 1
            month += 12
        
        a = int(year / 100)
        b = 2 - a + int(a / 4)
        
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
        jd += hour / 24.0 + minute / 1440.0 + second / 86400.0
        
        return jd
    
    def _cartesian_to_spherical(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Convert cartesian coordinates to spherical (lat, lon, alt)"""
        # Calculate latitude, longitude, and altitude
        r = np.sqrt(x**2 + y**2 + z**2)
        lat = np.arcsin(z / r)  # Latitude
        lon = np.arctan2(y, x)  # Longitude
        alt = r - self.earth_radius  # Altitude
        
        # Convert to degrees
        lat_deg = np.degrees(lat)
        lon_deg = np.degrees(lon)
        
        return lat_deg, lon_deg, alt
    
    def calculate_distance(self, pos1: Dict[str, float], pos2: Dict[str, float]) -> float:
        """Calculate distance between two positions"""
        dx = pos1['x'] - pos2['x']
        dy = pos1['y'] - pos2['y']
        dz = pos1['z'] - pos2['z']
        
        return np.sqrt(dx**2 + dy**2 + dz**2)
    
    def get_closest_approach(self, sat1_positions: List[Dict], sat2_positions: List[Dict]) -> Dict[str, Any]:
        """Find the closest approach between two satellites"""
        min_distance = float('inf')
        closest_time = None
        closest_pos1 = None
        closest_pos2 = None
        
        for pos1 in sat1_positions:
            for pos2 in sat2_positions:
                if pos1['time'] == pos2['time']:  # Same time
                    distance = self.calculate_distance(pos1, pos2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_time = pos1['time']
                        closest_pos1 = pos1
                        closest_pos2 = pos2
        
        return {
            'distance': min_distance,
            'time': closest_time,
            'position1': closest_pos1,
            'position2': closest_pos2
        }
