import math
from typing import Dict, List, Any, Tuple

import numpy as np
import plotly.graph_objects as go
import plotly.express as px


class TrajectoryVisualizer:
    """Enhanced 3D visualization of spacecraft and debris trajectories with realistic orbital mechanics.

    Features:
    - Realistic Earth with continents and atmosphere
    - Improved orbital mechanics with eccentricity and RAAN
    - Collision prediction visualization
    - Enhanced color coding and sizing
    - Real-time trajectory tracking
    """

    def __init__(self, earth_radius_km: float = 6371.0):
        self.earth_radius_km = earth_radius_km
        self.gravitational_constant = 398600.4418  # km³/s² (Earth's GM)

    def _calculate_orbital_period(self, semi_major_axis_km: float) -> float:
        """Calculate orbital period using Kepler's Third Law."""
        return 2 * math.pi * math.sqrt((semi_major_axis_km ** 3) / self.gravitational_constant)

    def _simulate_realistic_orbit(self, altitude_km: float, inclination_deg: float,
                                 eccentricity: float = 0.0, raan_deg: float = 0.0,
                                 num_points: int = 72, phase_offset: float = 0.0) -> np.ndarray:
        """Simulate realistic orbital motion with proper coordinate alignment."""
        try:
            # Calculate orbital parameters
            semi_major_axis = self.earth_radius_km + altitude_km
            period = self._calculate_orbital_period(semi_major_axis)
            
            # Convert angles to radians
            inclination = math.radians(inclination_deg)
            raan = math.radians(raan_deg)
            
            # True anomaly array (one complete orbit)
            true_anomaly = np.linspace(0.0 + phase_offset, 2.0 * math.pi + phase_offset, num_points)
            
            # Calculate radius at each point (Kepler's First Law)
            radius = semi_major_axis * (1 - eccentricity**2) / (1 + eccentricity * np.cos(true_anomaly))
            
            # Simplified orbital plane coordinates (no complex perturbations for better alignment)
            x_orbital = radius * np.cos(true_anomaly)
            y_orbital = radius * np.sin(true_anomaly)
            z_orbital = np.zeros_like(true_anomaly)
            
            # Proper rotation matrices for inclination and RAAN
            cos_i, sin_i = np.cos(inclination), np.sin(inclination)
            cos_raan, sin_raan = np.cos(raan), np.sin(raan)
            
            # Apply rotations in correct order: RAAN first, then inclination
            # RAAN rotation around z-axis
            x_raan = x_orbital * cos_raan - y_orbital * sin_raan
            y_raan = x_orbital * sin_raan + y_orbital * cos_raan
            z_raan = z_orbital
            
            # Inclination rotation around x-axis
            x = x_raan
            y = y_raan * cos_i - z_raan * sin_i
            z = y_raan * sin_i + z_raan * cos_i
            
            return np.vstack([x, y, z]).T
            
        except Exception as e:
            print(f"Error in orbit simulation: {e}")
            # Return a simple circular orbit as fallback
            radius = self.earth_radius_km + altitude_km
            theta = np.linspace(0, 2 * np.pi, num_points)
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            z = np.zeros_like(theta)
            return np.vstack([x, y, z]).T

    def _create_realistic_earth(self) -> List[go.Surface]:
        """Create a simplified Earth visualization for better performance."""
        earth_surfaces = []
        
        # Reduced resolution for better performance
        u = np.linspace(0, 2 * np.pi, 50)   # longitude (reduced from 200)
        v = np.linspace(0, np.pi, 25)       # latitude (reduced from 100)
        x = self.earth_radius_km * np.outer(np.cos(u), np.sin(v))
        y = self.earth_radius_km * np.outer(np.sin(u), np.sin(v))
        z = self.earth_radius_km * np.outer(np.ones_like(u), np.cos(v))
        
        # Create simplified color map for Earth (reduced complexity)
        colors = np.zeros_like(x)
        # np.outer creates (len(u), len(v)) shape, so colors.shape is (50, 25)
        for i in range(50):   # u dimension (longitude) - reduced from 200
            for j in range(25):   # v dimension (latitude) - reduced from 100
                # Convert array indices to lat/lon (adjusted for reduced resolution)
                lat = 90 - (j * 180 / 24)  # 90 to -90 (latitude) - adjusted for 25 points
                lon = i * 360 / 49 - 180   # -180 to 180 (longitude) - adjusted for 50 points
                
                # Realistic continent patterns based on actual Earth geography
                # North America
                if (-140 <= lon <= -50) and (25 <= lat <= 75):
                    colors[i, j] = 0.4  # Land
                # South America
                elif (-80 <= lon <= -35) and (-55 <= lat <= 15):
                    colors[i, j] = 0.4  # Land
                # Europe and Asia
                elif (-10 <= lon <= 180) and (35 <= lat <= 75):
                    colors[i, j] = 0.4  # Land
                # Africa
                elif (-20 <= lon <= 50) and (-35 <= lat <= 35):
                    colors[i, j] = 0.4  # Land
                # Australia
                elif (110 <= lon <= 155) and (-45 <= lat <= -10):
                    colors[i, j] = 0.4  # Land
                # Antarctica
                elif lat < -60:
                    colors[i, j] = 0.6  # Ice/white
                # Greenland
                elif (-75 <= lon <= -10) and (60 <= lat <= 85):
                    colors[i, j] = 0.6  # Ice/white
                # Islands and smaller landmasses
                elif (abs(lat) > 60 and abs(lon) > 150) or \
                     (abs(lat) > 60 and abs(lon) < 30) or \
                     (abs(lat) < 30 and abs(lon) > 150):
                    colors[i, j] = 0.4  # Land
                else:
                    colors[i, j] = 0.8  # Ocean (deeper blue)
        
        earth_surfaces.append(go.Surface(
            x=x, y=y, z=z,
            surfacecolor=colors,
            colorscale='Earth',
            showscale=False,
            opacity=0.9
        ))
        
        # Atmosphere layer
        atm_radius = self.earth_radius_km + 100
        x_atm = atm_radius * np.outer(np.cos(u), np.sin(v))
        y_atm = atm_radius * np.outer(np.sin(u), np.sin(v))
        z_atm = atm_radius * np.outer(np.ones_like(u), np.cos(v))
        
        earth_surfaces.append(go.Surface(
            x=x_atm, y=y_atm, z=z_atm,
            colorscale='Blues',
            showscale=False,
            opacity=0.1
        ))
        
        return earth_surfaces

    def _build_enhanced_frames(self, labels: List[str], trajectories_xyz: Dict[str, np.ndarray],
                              collision_points: List[Dict] = None, collision_effects: List[Dict] = None) -> List[go.Frame]:
        """Create enhanced animation frames with collision indicators."""
        if not labels:
            return []
        
        try:
            num_points = min(trajectories_xyz[labels[0]].shape[0], 72)  # Reduced from 360
            frames = []
        except (KeyError, IndexError, AttributeError) as e:
            print(f"Error building frames: {e}")
            return []
        
        for i in range(num_points):
            scatters = []
            
            # Add trajectory points
            for name in labels:
                traj = trajectories_xyz[name]
                j = min(i, traj.shape[0] - 1)
                
                # Get object metadata for realistic sizing
                object_type = 'satellite'  # Default
                if hasattr(self, '_objects_metadata') and name in self._objects_metadata:
                    object_type = self._objects_metadata[name].get('object_type', 'satellite')
                
                # Get realistic marker size
                marker_size = self._get_object_size(name, object_type)
                
                scatters.append(go.Scatter3d(
                    x=[traj[j, 0]], y=[traj[j, 1]], z=[traj[j, 2]],
                    mode='markers',
                    marker=dict(
                        size=marker_size,
                        color=self._color_for_name(name),
                        line=dict(width=2, color='white'),
                        symbol='circle'
                    ),
                    name=name,
                    showlegend=False
                ))
            
            # Add collision indicators if any
            if collision_points:
                for collision in collision_points:
                    if collision.get('frame_index', 0) == i:
                        # Main collision point
                        scatters.append(go.Scatter3d(
                            x=[collision['x']], y=[collision['y']], z=[collision['z']],
                            mode='markers',
                            marker=dict(
                                size=25,
                                symbol='x',
                                color='red',
                                line=dict(width=4, color='white')
                            ),
                            name='COLLISION',
                            showlegend=False
                        ))
                        
                        # Add explosion effect (larger red sphere)
                        scatters.append(go.Scatter3d(
                            x=[collision['x']], y=[collision['y']], z=[collision['z']],
                            mode='markers',
                            marker=dict(
                                size=40,
                                symbol='circle',
                                color='rgba(255, 0, 0, 0.3)',
                                line=dict(width=2, color='red')
                            ),
                            name='EXPLOSION',
                            showlegend=False
                        ))
            
            # Add collision debris effects
            if collision_effects:
                for effect in collision_effects:
                    if effect.get('frame_index', 0) == i:
                        scatters.append(go.Scatter3d(
                            x=[effect['x']], y=[effect['y']], z=[effect['z']],
                            mode='markers',
                            marker=dict(
                                size=effect['size'],
                                symbol='circle',
                                color='rgba(255, 165, 0, 0.7)',  # Orange debris
                                line=dict(width=1, color='orange')
                            ),
                            name='DEBRIS',
                            showlegend=False
                        ))
            
            frames.append(go.Frame(data=scatters, name=f"frame_{i}"))
        
        return frames

    def _color_for_name(self, name: str) -> str:
        """Enhanced color coding for different object types with realistic variations."""
        n = name.upper()
        if 'DEBRIS' in n or 'COSMOS' in n:
            # Vary debris colors slightly for more realism
            debris_colors = ['#d32f2f', '#c62828', '#b71c1c', '#d84315']
            return debris_colors[hash(n) % len(debris_colors)]
        if 'STARLINK' in n:
            return '#1976d2'  # Blue for Starlink
        if 'GPS' in n:
            return '#388e3c'  # Green for GPS
        if 'ISS' in n:
            return '#7b1fa2'  # Purple for ISS
        if 'GALILEO' in n:
            return '#f57c00'  # Orange for Galileo
        if 'ONEWEB' in n:
            return '#00acc1'  # Cyan for OneWeb
        if 'BEIDOU' in n:
            return '#ff6f00'  # Amber for BeiDou
        if 'GLONASS' in n:
            return '#6a1b9a'  # Deep purple for GLONASS
        return '#424242'  # Gray for others

    def _get_object_size(self, name: str, object_type: str) -> float:
        """Get realistic object sizes based on type and name."""
        n = name.upper()
        
        # Base sizes in km (scaled for visualization)
        if object_type == 'satellite':
            if 'ISS' in n:
                return 20  # ISS is large
            elif 'STARLINK' in n:
                return 8   # Small satellites
            elif 'GPS' in n or 'GALILEO' in n:
                return 12  # Medium satellites
            else:
                return 10  # Default satellite size
        else:  # debris
            if 'COSMOS' in n:
                return 6   # Large debris
            else:
                return 3   # Small debris

    def _calculate_collision_points(self, trajectories_xyz: Dict[str, np.ndarray],
                                   collision_data: List[Dict]) -> List[Dict]:
        """Calculate 3D positions of predicted collision points with proper alignment."""
        collision_points = []
        
        try:
            for collision in collision_data:
                sat1_name = collision.get('satellite1_name')
                sat2_name = collision.get('satellite2_name')
                
                if sat1_name in trajectories_xyz and sat2_name in trajectories_xyz:
                    # Find the closest approach point
                    traj1 = trajectories_xyz[sat1_name]
                    traj2 = trajectories_xyz[sat2_name]
                    
                    # Ensure trajectories have the same length
                    min_length = min(len(traj1), len(traj2))
                    if min_length == 0:
                        continue
                    
                    # Calculate distances between trajectories
                    min_dist = float('inf')
                    collision_idx = 0
                    
                    for i in range(min_length):
                        try:
                            dist = np.linalg.norm(traj1[i] - traj2[i])
                            if dist < min_dist:
                                min_dist = dist
                                collision_idx = i
                        except (IndexError, ValueError) as e:
                            print(f"Error calculating distance at index {i}: {e}")
                            continue
                    
                    # Add collision point if distance is small enough
                    if min_dist < 50:  # Increased threshold for better detection
                        collision_points.append({
                            'x': (traj1[collision_idx, 0] + traj2[collision_idx, 0]) / 2,
                            'y': (traj1[collision_idx, 1] + traj2[collision_idx, 1]) / 2,
                            'z': (traj1[collision_idx, 2] + traj2[collision_idx, 2]) / 2,
                            'frame_index': collision_idx,
                            'distance': min_dist
                        })
        except Exception as e:
            print(f"Error calculating collision points: {e}")
        
        return collision_points

    def create_enhanced_animated_figure(
        self,
        objects: Dict[str, Dict[str, Any]],
        collision_data: List[Dict] = None,
        time_series_positions: Dict[str, np.ndarray] = None,
        num_points: int = 72  # Reduced from 360 for better performance
    ) -> go.Figure:
        """Create an enhanced animated 3D figure with realistic orbital mechanics.

        Args:
            objects: Dictionary mapping object names to metadata
            collision_data: List of collision predictions
            time_series_positions: Real propagated positions (optional)
            num_points: Number of points per orbit
        """
        try:
            labels = list(objects.keys())
            if not labels:
                print("No objects provided for trajectory visualization")
                return go.Figure()
            
            trajectories_xyz = {}
        except Exception as e:
            print(f"Error initializing trajectory visualization: {e}")
            return go.Figure()

        # Build enhanced trajectories with consistent coordinate system
        for idx, (name, meta) in enumerate(objects.items()):
            try:
                if time_series_positions and name in time_series_positions:
                    traj = time_series_positions[name]
                else:
                    # Enhanced orbital parameters with proper defaults
                    alt = float(meta.get('altitude', 500.0))
                    inc = float(meta.get('inclination', 0.0))
                    ecc = float(meta.get('eccentricity', 0.0))
                    raan = float(meta.get('raan', idx * 30.0))  # Reduced stagger for better alignment
                    
                    traj = self._simulate_realistic_orbit(
                        altitude_km=alt,
                        inclination_deg=inc,
                        eccentricity=ecc,
                        raan_deg=raan,
                        num_points=num_points,
                        phase_offset=idx * 0.1  # Reduced phase offset for better alignment
                    )
                
                # Ensure trajectory has correct shape
                if traj.shape[0] != num_points:
                    print(f"Warning: Trajectory for {name} has {traj.shape[0]} points, expected {num_points}")
                    # Pad or truncate to match expected length
                    if traj.shape[0] < num_points:
                        # Pad with last point
                        last_point = traj[-1:].repeat(num_points - traj.shape[0], axis=0)
                        traj = np.vstack([traj, last_point])
                    else:
                        # Truncate
                        traj = traj[:num_points]
                
                trajectories_xyz[name] = traj
                
            except Exception as e:
                print(f"Error processing trajectory for {name}: {e}")
                # Create a simple fallback trajectory
                radius = self.earth_radius_km + 500
                theta = np.linspace(0, 2 * np.pi, num_points)
                x = radius * np.cos(theta)
                y = radius * np.sin(theta)
                z = np.zeros_like(theta)
                trajectories_xyz[name] = np.vstack([x, y, z]).T

        # Store object metadata for realistic sizing
        self._objects_metadata = objects
        
        # Calculate collision points with enhanced effects
        collision_points = []
        collision_effects = []  # For explosion/debris effects
        if collision_data:
            collision_points = self._calculate_collision_points(trajectories_xyz, collision_data)
            
            # Add realistic collision effects (debris clouds)
            for collision in collision_points:
                # Create debris cloud around collision point
                num_debris = 15
                for k in range(num_debris):
                    angle = k * 2 * np.pi / num_debris
                    distance = 2 + np.random.random() * 3  # 2-5 km spread
                    collision_effects.append({
                        'x': collision['x'] + distance * np.cos(angle),
                        'y': collision['y'] + distance * np.sin(angle),
                        'z': collision['z'] + (np.random.random() - 0.5) * 2,
                        'frame_index': collision['frame_index'],
                        'size': 1 + np.random.random() * 2
                    })

        # Create Earth visualization
        earth_surfaces = self._create_realistic_earth()

        # Static trajectory paths with enhanced styling
        path_traces = []
        for name in labels:
            traj = trajectories_xyz[name]
            path_traces.append(go.Scatter3d(
                x=traj[:, 0], y=traj[:, 1], z=traj[:, 2],
                mode='lines',
                line=dict(
                    width=3,
                    color=self._color_for_name(name),
                    dash='solid'
                ),
                name=f"{name} orbit",
                opacity=0.7
            ))

        # Initial positions with realistic markers
        init_markers = []
        for name in labels:
            p0 = trajectories_xyz[name][0]
            
            # Get realistic marker size
            object_type = objects[name].get('object_type', 'satellite')
            marker_size = self._get_object_size(name, object_type)
            
            init_markers.append(go.Scatter3d(
                x=[p0[0]], y=[p0[1]], z=[p0[2]],
                mode='markers',
                marker=dict(
                    size=marker_size,
                    color=self._color_for_name(name),
                    line=dict(width=2, color='white'),
                    symbol='circle'
                ),
                name=name
            ))

        # Compose enhanced figure
        fig = go.Figure(data=[*earth_surfaces, *path_traces, *init_markers])
        
        fig.update_layout(
            title=dict(
                text='Realistic Space Traffic Visualization',
                x=0.5,
                font=dict(size=20, color='white')
            ),
            scene=dict(
                xaxis_title='X (km)', yaxis_title='Y (km)', zaxis_title='Z (km)',
                aspectmode='data',
                xaxis=dict(
                    showgrid=True, zeroline=False,
                    gridcolor='rgba(255,255,255,0.1)',
                    showbackground=True,
                    backgroundcolor='rgba(0,0,0,0.8)'
                ),
                yaxis=dict(
                    showgrid=True, zeroline=False,
                    gridcolor='rgba(255,255,255,0.1)',
                    showbackground=True,
                    backgroundcolor='rgba(0,0,0,0.8)'
                ),
                zaxis=dict(
                    showgrid=True, zeroline=False,
                    gridcolor='rgba(255,255,255,0.1)',
                    showbackground=True,
                    backgroundcolor='rgba(0,0,0,0.8)'
                ),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            showlegend=True,
            legend=dict(
                x=0.02, y=0.98,
                bgcolor='rgba(0,0,0,0.8)',
                bordercolor='rgba(255,255,255,0.3)',
                borderwidth=1
            ),
            margin=dict(l=20, r=20, t=80, b=20),
            paper_bgcolor='black',
            plot_bgcolor='black',
            autosize=True,
            width=None,
            height=600,
            updatemenus=[
                dict(
                    type='buttons',
                    showactive=False,
                    x=0.05, y=1.05, xanchor='left', yanchor='top',
                    buttons=[
                        dict(
                            label='▶️ Play',
                            method='animate',
                            args=[
                                None,
                                {
                                    'frame': {'duration': 100, 'redraw': True},
                                    'fromcurrent': True,
                                    'transition': {'duration': 50}
                                }
                            ]
                        ),
                        dict(
                            label='⏸️ Pause',
                            method='animate',
                            args=[
                                None,
                                {
                                    'frame': {'duration': 0, 'redraw': False},
                                    'mode': 'immediate',
                                    'transition': {'duration': 0}
                                }
                            ]
                        ),
                        dict(
                            label='🔄 Reset',
                            method='animate',
                            args=[
                                [None],
                                {
                                    'frame': {'duration': 0, 'redraw': False},
                                    'mode': 'immediate',
                                    'transition': {'duration': 0}
                                }
                            ]
                        )
                    ]
                )
            ]
        )

        # Enhanced animation frames
        frames = self._build_enhanced_frames(labels, trajectories_xyz, collision_points, collision_effects)
        fig.frames = frames

        return fig

    # Backward compatibility
    def create_animated_figure(self, *args, **kwargs):
        return self.create_enhanced_animated_figure(*args, **kwargs)


