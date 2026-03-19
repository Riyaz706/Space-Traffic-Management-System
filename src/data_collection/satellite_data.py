"""
Satellite Data Collection Module
Fetches real-time satellite data from various APIs and sources
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SatelliteDataCollector:
    """
    Collects satellite data from various sources including:
    - Space-Track API (NORAD TLE data)
    - Celestrak API
    - Simulated data for development
    """
    
    def __init__(self):
        self.session = None
        self.base_urls = {
            'celestrak': 'https://celestrak.org/NORAD/elements/',
            'space_track': 'https://www.space-track.org/api/',
        }
        
        # Sample satellite data for development (when APIs are not available)
        self.sample_satellites = self._generate_sample_data()
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def collect_data(self) -> Dict[str, Any]:
        """
        Collect satellite data from all available sources
        Returns: Dictionary of satellite data
        """
        try:
            # First try to load data from JSON file
            json_data = await self._load_json_data()
            if json_data:
                logger.info(f"📡 Loaded {len(json_data)} objects from JSON file")
                return json_data
            
            # Try to get real data from APIs
            real_data = await self._fetch_real_data()
            if real_data:
                return real_data
            
            # Fall back to sample data for development
            logger.info("📡 Using sample satellite data for development")
            return self.sample_satellites
            
        except Exception as e:
            logger.error(f"❌ Error collecting satellite data: {e}")
            return self.sample_satellites
    
    async def _load_json_data(self) -> Optional[Dict[str, Any]]:
        """Load satellite data from JSON file (processed preferred)."""
        try:
            import json
            import os
            
            # Try multiple possible paths for the JSON file
            json_paths = [
                "data/processed_satellite_data.json",  # preferred live processed
                "data/fake_satellite_data.json",
                "../data/fake_satellite_data.json",
                "fake_satellite_data.json"
            ]
            
            for json_path in json_paths:
                if os.path.exists(json_path):
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                        if 'satellites' in data:
                            logger.info(f"✅ Successfully loaded data from {json_path}")
                            return data['satellites']
            
            logger.warning("⚠️ JSON data file not found in any expected location")
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Error loading JSON data: {e}")
            return None
    
    async def _fetch_real_data(self) -> Optional[Dict[str, Any]]:
        """Fetch real satellite data from APIs"""
        try:
            # Try multiple real-time data sources
            real_data = {}
            
            # Try Celestrak API (public, no authentication required)
            celestrak_data = await self._fetch_celestrak_data()
            if celestrak_data:
                real_data.update(celestrak_data)
            
            # Try N2YO API for additional real-time data
            n2yo_data = await self._fetch_n2yo_data()
            if n2yo_data:
                real_data.update(n2yo_data)
            
            # Add real-time ISS data
            iss_data = await self._fetch_iss_data()
            if iss_data:
                real_data.update(iss_data)
            
            if real_data:
                return real_data
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch real data: {e}")
            return None
    
    async def _fetch_celestrak_data(self) -> Optional[Dict[str, Any]]:
        """Fetch data from Celestrak API"""
        if not self.session:
            return None
            
        try:
            # Fetch active satellites TLE data
            url = f"{self.base_urls['celestrak']}active.txt"
            async with self.session.get(url) as response:
                if response.status == 200:
                    tle_data = await response.text()
                    return self._parse_tle_data(tle_data)
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Celestrak API error: {e}")
            return None
    
    def _parse_tle_data(self, tle_data: str) -> Dict[str, Any]:
        """Parse TLE (Two-Line Element) data"""
        satellites = {}
        lines = tle_data.strip().split('\n')
        
        for i in range(0, len(lines), 3):
            if i + 2 < len(lines):
                name = lines[i].strip()
                line1 = lines[i + 1].strip()
                line2 = lines[i + 2].strip()
                
                # Extract basic orbital elements from TLE
                satellite_id = line1[2:7].strip()
                
                satellites[satellite_id] = {
                    'name': name,
                    'satellite_id': satellite_id,
                    'tle_line1': line1,
                    'tle_line2': line2,
                    'epoch': self._extract_epoch(line1),
                    'inclination': float(line2[8:16]),
                    'raan': float(line2[17:25]),
                    'eccentricity': float('0.' + line2[26:33]),
                    'arg_perigee': float(line2[34:42]),
                    'mean_anomaly': float(line2[43:51]),
                    'mean_motion': float(line2[52:63]),
                    'last_updated': datetime.now().isoformat()
                }
        
        return satellites
    
    async def _fetch_n2yo_data(self) -> Optional[Dict[str, Any]]:
        """Fetch real-time satellite data from N2YO API"""
        if not self.session:
            return None
            
        try:
            # N2YO API endpoints for real-time data
            n2yo_endpoints = [
                'https://api.n2yo.com/rest/v1/satellite/above/0/0/0/70/&apiKey=demo',  # Demo key
                'https://api.n2yo.com/rest/v1/satellite/visualpasses/25544/0/0/1/1/&apiKey=demo'  # ISS passes
            ]
            
            satellites = {}
            
            for endpoint in n2yo_endpoints:
                try:
                    async with self.session.get(endpoint, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            # Process N2YO data format
                            if 'above' in data:
                                for sat in data['above']:
                                    sat_id = str(sat['satid'])
                                    satellites[sat_id] = {
                                        'name': sat['satname'],
                                        'satellite_id': sat_id,
                                        'altitude': sat.get('satalt', 500),
                                        'inclination': sat.get('inclination', 45),
                                        'eccentricity': sat.get('eccentricity', 0.001),
                                        'raan': sat.get('raan', 0),
                                        'arg_perigee': sat.get('argperigee', 0),
                                        'mean_anomaly': sat.get('meananomaly', 0),
                                        'period': sat.get('period', 95),
                                        'status': 'active',
                                        'last_updated': datetime.now().isoformat(),
                                        'object_type': 'satellite',
                                        'data_source': 'N2YO'
                                    }
                except Exception as e:
                    logger.warning(f"⚠️ N2YO API error: {e}")
                    continue
            
            return satellites if satellites else None
            
        except Exception as e:
            logger.warning(f"⚠️ N2YO data fetch error: {e}")
            return None
    
    async def _fetch_iss_data(self) -> Optional[Dict[str, Any]]:
        """Fetch real-time ISS position data"""
        if not self.session:
            return None
            
        try:
            # Open Notify API for ISS real-time position
            iss_url = "http://api.open-notify.org/iss-now.json"
            
            async with self.session.get(iss_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'iss_position' in data:
                        iss_pos = data['iss_position']
                        timestamp = data['timestamp']
                        
                        # Convert timestamp to datetime
                        iss_time = datetime.fromtimestamp(timestamp)
                        
                        # Create ISS satellite data
                        iss_data = {
                            '25544': {  # ISS NORAD ID
                                'name': 'International Space Station (ISS)',
                                'satellite_id': '25544',
                                'latitude': float(iss_pos['latitude']),
                                'longitude': float(iss_pos['longitude']),
                                'altitude': 408,  # Average ISS altitude
                                'inclination': 51.6,
                                'eccentricity': 0.001,
                                'raan': 0.0,
                                'arg_perigee': 0.0,
                                'mean_anomaly': 0.0,
                                'period': 92.7,
                                'status': 'active',
                                'last_updated': iss_time.isoformat(),
                                'object_type': 'satellite',
                                'data_source': 'Open Notify',
                                'real_time': True
                            }
                        }
                        
                        logger.info("✅ Fetched real-time ISS position data")
                        return iss_data
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ ISS data fetch error: {e}")
            return None
    
    def _extract_epoch(self, line1: str) -> str:
        """Extract epoch from TLE line 1"""
        year = int(line1[18:20])
        day = float(line1[20:32])
        
        # Convert to full year and date
        full_year = 2000 + year if year < 50 else 1900 + year
        epoch_date = datetime(full_year, 1, 1) + timedelta(days=day-1)
        
        return epoch_date.isoformat()
    
    def _generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample satellite data for development and testing"""
        satellites = {}
        
        # Sample satellites with realistic orbital parameters
        sample_sats = [
            {
                'name': 'ISS (ZARYA)',
                'satellite_id': '25544',
                'inclination': 51.6,
                'altitude': 408,  # km
                'period': 92.7,   # minutes
            },
            {
                'name': 'STARLINK-1234',
                'satellite_id': '44713',
                'inclination': 53.0,
                'altitude': 550,
                'period': 95.0,
            },
            {
                'name': 'COSMOS 2251 DEB',
                'satellite_id': '33759',
                'inclination': 74.0,
                'altitude': 800,
                'period': 101.0,
            },
            {
                'name': 'IRIDIUM 33 DEB',
                'satellite_id': '33758',
                'inclination': 86.4,
                'altitude': 780,
                'period': 100.0,
            },
            {
                'name': 'HST (HUBBLE)',
                'satellite_id': '20580',
                'inclination': 28.5,
                'altitude': 540,
                'period': 95.0,
            }
        ]
        
        for sat in sample_sats:
            # Generate realistic orbital elements
            eccentricity = 0.001  # Nearly circular orbits for LEO
            raan = np.random.uniform(0, 360)  # Random right ascension
            arg_perigee = np.random.uniform(0, 360)  # Random argument of perigee
            mean_anomaly = np.random.uniform(0, 360)  # Random mean anomaly
            
            satellites[sat['satellite_id']] = {
                'name': sat['name'],
                'satellite_id': sat['satellite_id'],
                'inclination': sat['inclination'],
                'altitude': sat['altitude'],
                'period': sat['period'],
                'eccentricity': eccentricity,
                'raan': raan,
                'arg_perigee': arg_perigee,
                'mean_anomaly': mean_anomaly,
                'epoch': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'is_active': True,
                'object_type': 'satellite' if 'DEB' not in sat['name'] else 'debris'
            }
        
        return satellites
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    def get_satellite_count(self) -> int:
        """Get the number of satellites being tracked"""
        return len(self.sample_satellites)
    
    def get_satellite_by_id(self, satellite_id: str) -> Optional[Dict[str, Any]]:
        """Get specific satellite data by ID"""
        return self.sample_satellites.get(satellite_id)
    
    def get_active_satellites(self) -> Dict[str, Any]:
        """Get only active satellites (excluding debris)"""
        return {
            sat_id: sat_data 
            for sat_id, sat_data in self.sample_satellites.items()
            if sat_data.get('object_type') == 'satellite'
        }
    
    def get_debris_objects(self) -> Dict[str, Any]:
        """Get only debris objects"""
        return {
            sat_id: sat_data 
            for sat_id, sat_data in self.sample_satellites.items()
            if sat_data.get('object_type') == 'debris'
        }
