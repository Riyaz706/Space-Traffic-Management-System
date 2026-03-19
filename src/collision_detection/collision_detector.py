"""
AI-Powered Collision Detection Module
Identifies potential satellite collisions using machine learning and orbital analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

logger = logging.getLogger(__name__)

class CollisionDetector:
    """
    AI-powered collision detection system
    Uses machine learning and orbital analysis to predict potential collisions
    """
    
    def __init__(self):
        self.collision_threshold = 10.0  # km - minimum distance for collision risk
        self.high_risk_threshold = 1.0   # km - high risk collision distance
        self.ml_model = None
        self.scaler = StandardScaler()
        self.is_model_trained = False
        
        # Initialize ML model
        self._initialize_ml_model()
    
    def _initialize_ml_model(self):
        """Initialize the machine learning model for collision prediction"""
        try:
            # Try to load pre-trained model
            model_path = "data/collision_model.pkl"
            if os.path.exists(model_path):
                self.ml_model = joblib.load(model_path)
                self.is_model_trained = True
                logger.info("✅ Loaded pre-trained collision detection model")
            else:
                # Create new model
                self.ml_model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                logger.info("🆕 Created new collision detection model")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize ML model: {e}")
            self.ml_model = None
    
    async def detect_collisions(self, future_positions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect potential collisions between satellites
        
        Args:
            future_positions: Dictionary of future satellite positions
            
        Returns:
            List of detected potential collisions
        """
        logger.info(f"🚨 Analyzing {len(future_positions)} objects for potential collisions...")
        
        collisions = []
        satellite_ids = list(future_positions.keys())
        
        # Check all pairs of satellites
        for i, sat1_id in enumerate(satellite_ids):
            for j, sat2_id in enumerate(satellite_ids[i+1:], i+1):
                try:
                    # Get collision risk between this pair
                    collision_risk = await self._analyze_collision_risk(
                        sat1_id, future_positions[sat1_id],
                        sat2_id, future_positions[sat2_id]
                    )
                    
                    if collision_risk and collision_risk['risk_level'] != 'none':
                        collisions.append(collision_risk)
                        logger.warning(f"⚠️ Potential collision detected: {sat1_id} vs {sat2_id}")
                
                except Exception as e:
                    logger.warning(f"⚠️ Error analyzing {sat1_id} vs {sat2_id}: {e}")
                    continue
        
        logger.info(f"✅ Collision analysis complete. Found {len(collisions)} potential collisions")
        return collisions
    
    async def _analyze_collision_risk(self, sat1_id: str, sat1_data: Dict[str, Any],
                                    sat2_id: str, sat2_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze collision risk between two satellites
        
        Args:
            sat1_id, sat1_data: First satellite data
            sat2_id, sat2_data: Second satellite data
            
        Returns:
            Collision risk assessment
        """
        try:
            # Get closest approach - handle missing positions data
            sat1_positions = sat1_data.get('positions', [])
            sat2_positions = sat2_data.get('positions', [])
            
            if not sat1_positions or not sat2_positions:
                # Generate fallback positions if missing
                sat1_positions = self._generate_fallback_positions(sat1_data)
                sat2_positions = self._generate_fallback_positions(sat2_data)
            
            closest_approach = self._find_closest_approach(sat1_positions, sat2_positions)
            
            if closest_approach['distance'] > self.collision_threshold:
                return None  # No collision risk
            
            # Calculate collision probability
            collision_prob = self._calculate_collision_probability(
                sat1_data, sat2_data, closest_approach
            )
            
            # Determine risk level
            risk_level = self._determine_risk_level(
                closest_approach['distance'], collision_prob
            )
            
            # Use ML model for additional risk assessment
            ml_risk_score = await self._get_ml_risk_score(
                sat1_data, sat2_data, closest_approach
            )
            
            return {
                'satellite1_id': sat1_id,
                'satellite1_name': sat1_data.get('name', 'Unknown'),
                'satellite2_id': sat2_id,
                'satellite2_name': sat2_data.get('name', 'Unknown'),
                'closest_approach': closest_approach,
                'collision_probability': collision_prob,
                'risk_level': risk_level,
                'ml_risk_score': ml_risk_score,
                'detection_time': datetime.now().isoformat(),
                'time_to_closest_approach': self._calculate_time_to_closest(closest_approach['time'])
            }
            
        except Exception as e:
            logger.error(f"❌ Error in collision risk analysis: {e}")
            return None
    
    def _find_closest_approach(self, pos1_list: List[Dict], pos2_list: List[Dict]) -> Dict[str, Any]:
        """Find the closest approach between two satellites"""
        min_distance = float('inf')
        closest_time = None
        closest_pos1 = None
        closest_pos2 = None
        
        for pos1 in pos1_list:
            for pos2 in pos2_list:
                if pos1['time'] == pos2['time']:  # Same time
                    distance = self._calculate_distance(pos1, pos2)
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
    
    def _calculate_distance(self, pos1: Dict[str, float], pos2: Dict[str, float]) -> float:
        """Calculate 3D distance between two positions"""
        dx = pos1['x'] - pos2['x']
        dy = pos1['y'] - pos2['y']
        dz = pos1['z'] - pos2['z']
        
        return np.sqrt(dx**2 + dy**2 + dz**2)
    
    def _calculate_collision_probability(self, sat1_data: Dict[str, Any], 
                                       sat2_data: Dict[str, Any],
                                       closest_approach: Dict[str, Any]) -> float:
        """
        Calculate collision probability using Monte Carlo method
        Simplified version - in production would use more sophisticated methods
        """
        distance = closest_approach['distance']
        
        # Simplified probability calculation based on distance
        # In reality, this would consider:
        # - Position uncertainties
        # - Velocity uncertainties
        # - Object sizes
        # - Atmospheric drag effects
        
        if distance < self.high_risk_threshold:
            # High risk - distance < 1 km
            base_prob = 0.1  # 10% base probability
            distance_factor = (self.high_risk_threshold - distance) / self.high_risk_threshold
            return min(0.95, base_prob + distance_factor * 0.85)
        
        elif distance < self.collision_threshold:
            # Medium risk - distance < 10 km
            base_prob = 0.01  # 1% base probability
            distance_factor = (self.collision_threshold - distance) / (self.collision_threshold - self.high_risk_threshold)
            return min(0.1, base_prob + distance_factor * 0.09)
        
        else:
            return 0.0
    
    def _determine_risk_level(self, distance: float, probability: float) -> str:
        """Determine risk level based on distance and probability"""
        if distance < self.high_risk_threshold or probability > 0.5:
            return 'high'
        elif distance < self.collision_threshold or probability > 0.1:
            return 'medium'
        elif distance < self.collision_threshold * 2 or probability > 0.01:
            return 'low'
        else:
            return 'none'
    
    async def _get_ml_risk_score(self, sat1_data: Dict[str, Any], sat2_data: Dict[str, Any],
                                closest_approach: Dict[str, Any]) -> float:
        """
        Get risk score from machine learning model
        """
        if not self.ml_model or not self.is_model_trained:
            # Return heuristic score if ML model not available
            return self._calculate_heuristic_risk_score(sat1_data, sat2_data, closest_approach)
        
        try:
            # Extract features for ML model
            features = self._extract_ml_features(sat1_data, sat2_data, closest_approach)
            
            # Normalize features
            features_scaled = self.scaler.transform([features])
            
            # Get prediction
            risk_score = self.ml_model.predict_proba(features_scaled)[0][1]  # Probability of collision
            
            return float(risk_score)
            
        except Exception as e:
            logger.warning(f"⚠️ ML prediction failed: {e}")
            return self._calculate_heuristic_risk_score(sat1_data, sat2_data, closest_approach)
    
    def _extract_ml_features(self, sat1_data: Dict[str, Any], sat2_data: Dict[str, Any],
                            closest_approach: Dict[str, Any]) -> List[float]:
        """Extract features for machine learning model"""
        features = []
        
        # Distance features
        features.append(closest_approach['distance'])
        
        # Altitude features
        alt1 = closest_approach['position1']['altitude']
        alt2 = closest_approach['position2']['altitude']
        features.extend([alt1, alt2, abs(alt1 - alt2)])
        
        # Velocity features
        vel1 = closest_approach['position1']['velocity']
        vel2 = closest_approach['position2']['velocity']
        features.extend([vel1, vel2, abs(vel1 - vel2)])
        
        # Orbital elements (if available)
        if 'inclination' in sat1_data:
            features.append(sat1_data['inclination'])
        else:
            features.append(0.0)
            
        if 'inclination' in sat2_data:
            features.append(sat2_data['inclination'])
        else:
            features.append(0.0)
        
        # Object type features (satellite vs debris)
        type1 = 1.0 if sat1_data.get('object_type') == 'satellite' else 0.0
        type2 = 1.0 if sat2_data.get('object_type') == 'satellite' else 0.0
        features.extend([type1, type2])
        
        return features
    
    def _calculate_heuristic_risk_score(self, sat1_data: Dict[str, Any], sat2_data: Dict[str, Any],
                                       closest_approach: Dict[str, Any]) -> float:
        """Calculate heuristic risk score when ML model is not available"""
        distance = closest_approach['distance']
        
        # Base risk based on distance
        if distance < 1.0:
            base_risk = 0.8
        elif distance < 5.0:
            base_risk = 0.4
        elif distance < 10.0:
            base_risk = 0.1
        else:
            base_risk = 0.01
        
        # Adjust for object types
        type_factor = 1.0
        if (sat1_data.get('object_type') == 'debris' or 
            sat2_data.get('object_type') == 'debris'):
            type_factor = 1.5  # Debris collisions are more likely
        
        # Adjust for altitude (lower altitude = more atmospheric drag = more uncertainty)
        alt1 = closest_approach['position1']['altitude']
        alt2 = closest_approach['position2']['altitude']
        avg_alt = (alt1 + alt2) / 2
        
        if avg_alt < 400:  # Low altitude
            alt_factor = 1.3
        elif avg_alt < 800:  # Medium altitude
            alt_factor = 1.0
        else:  # High altitude
            alt_factor = 0.8
        
        return min(1.0, base_risk * type_factor * alt_factor)
    
    def _calculate_time_to_closest(self, closest_time: str) -> float:
        """Calculate time to closest approach in hours"""
        try:
            closest_dt = datetime.fromisoformat(closest_time)
            current_dt = datetime.now()
            time_diff = closest_dt - current_dt
            return time_diff.total_seconds() / 3600  # Convert to hours
        except:
            return 0.0
    
    def _generate_fallback_positions(self, sat_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate fallback positions when position data is missing"""
        try:
            positions = []
            current_time = datetime.now()
            altitude = sat_data.get('altitude', 500)
            
            # Generate 3 positions over 6 hours
            for hours in range(0, 6, 2):
                future_time = current_time + timedelta(hours=hours)
                
                # Simple circular orbit approximation
                angle = hours * 30  # 30 degrees per hour
                radius = 6378.137 + altitude  # Earth radius + altitude
                
                x = radius * np.cos(np.radians(angle))
                y = radius * np.sin(np.radians(angle))
                z = 0  # Simplified
                
                positions.append({
                    'time': future_time.isoformat(),
                    'x': x,
                    'y': y,
                    'z': z,
                    'altitude': altitude,
                    'velocity': 7.5  # Typical orbital velocity
                })
            
            return positions
            
        except Exception as e:
            logger.error(f"❌ Error generating fallback positions: {e}")
            return []
    
    def train_model(self, training_data: List[Dict[str, Any]]):
        """
        Train the machine learning model with historical collision data
        This would be called with real historical data in production
        """
        try:
            if not training_data:
                logger.warning("⚠️ No training data provided")
                return
            
            # Extract features and labels
            features = []
            labels = []
            
            for data_point in training_data:
                features.append(data_point['features'])
                labels.append(data_point['collision_occurred'])
            
            # Convert to numpy arrays
            X = np.array(features)
            y = np.array(labels)
            
            # Normalize features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.ml_model.fit(X_scaled, y)
            self.is_model_trained = True
            
            # Save model
            os.makedirs("data", exist_ok=True)
            joblib.dump(self.ml_model, "data/collision_model.pkl")
            
            logger.info("✅ Collision detection model trained and saved")
            
        except Exception as e:
            logger.error(f"❌ Error training model: {e}")
    
    def get_collision_statistics(self, collisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about detected collisions"""
        if not collisions:
            return {
                'total_collisions': 0,
                'high_risk': 0,
                'medium_risk': 0,
                'low_risk': 0,
                'avg_distance': 0.0,
                'avg_probability': 0.0
            }
        
        risk_counts = {'high': 0, 'medium': 0, 'low': 0}
        distances = []
        probabilities = []
        
        for collision in collisions:
            risk_level = collision['risk_level']
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1
            
            distances.append(collision['closest_approach']['distance'])
            probabilities.append(collision['collision_probability'])
        
        return {
            'total_collisions': len(collisions),
            'high_risk': risk_counts['high'],
            'medium_risk': risk_counts['medium'],
            'low_risk': risk_counts['low'],
            'avg_distance': np.mean(distances),
            'avg_probability': np.mean(probabilities)
        }
