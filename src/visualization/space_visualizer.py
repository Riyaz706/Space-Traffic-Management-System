"""
Space Visualization Module
Provides 3D plots and real-time monitoring of satellite positions and collision risks
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)

class SpaceVisualizer:
    """
    Interactive 3D visualization system for space traffic monitoring
    """
    
    def __init__(self):
        self.earth_radius = 6378.137  # km
        self.colors = {
            'satellite': '#00ff00',  # Green for active satellites
            'debris': '#ff0000',     # Red for debris
            'collision_high': '#ff0000',    # Red for high risk
            'collision_medium': '#ffaa00',  # Orange for medium risk
            'collision_low': '#ffff00',     # Yellow for low risk
            'maneuver': '#0000ff',   # Blue for maneuvers
            'earth': '#0066cc',      # Blue for Earth
            'moon': '#c0c0c0',       # Silver for Moon
            'sun': '#ffff00',        # Yellow for Sun
            'stars': '#ffffff',      # White for stars
            'space_bg': '#000000'    # Black for space background
        }
        
        # Store visualization data
        self.current_data = {
            'satellites': {},
            'collisions': [],
            'maneuvers': []
        }
    
    async def update_visualization(self, satellites: Dict[str, Any], 
                                 collisions: List[Dict[str, Any]] = None,
                                 maneuvers: List[Dict[str, Any]] = None):
        """
        Update visualization with new data
        
        Args:
            satellites: Current satellite positions
            collisions: Detected collisions
            maneuvers: Planned maneuvers
        """
        try:
            # Update stored data
            self.current_data['satellites'] = satellites
            if collisions:
                self.current_data['collisions'] = collisions
            if maneuvers:
                self.current_data['maneuvers'] = maneuvers
            
            logger.info("📊 Visualization data updated")
            
        except Exception as e:
            logger.error(f"❌ Error updating visualization: {e}")
    
    def create_3d_space_plot(self) -> go.Figure:
        """
        Create interactive 3D plot of satellite positions and Earth with enhanced space view
        
        Returns:
            Plotly figure object
        """
        try:
            # Create figure
            fig = go.Figure()
            
            # Add space background elements
            self._add_space_background(fig)
            self._add_sun_to_plot(fig)
            self._add_moon_to_plot(fig)
            
            # Add Earth with enhanced appearance
            self._add_earth_to_plot(fig)
            
            # Add satellites (keep original trajectory system)
            self._add_satellites_to_plot(fig)
            
            # Add collision indicators
            self._add_collision_indicators(fig)
            
            # Add maneuver trajectories
            self._add_maneuver_trajectories(fig)
            
            # Update layout with space theme
            self._update_3d_layout(fig)
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Error creating 3D plot: {e}")
            return self._create_error_plot()
    
    def create_dashboard_plots(self) -> Dict[str, go.Figure]:
        """
        Create multiple dashboard plots for monitoring
        
        Returns:
            Dictionary of plotly figures
        """
        try:
            plots = {}
            
            # Satellite distribution plot
            plots['satellite_distribution'] = self._create_satellite_distribution_plot()
            
            # Collision risk timeline
            plots['collision_timeline'] = self._create_collision_timeline_plot()
            
            # Maneuver summary
            plots['maneuver_summary'] = self._create_maneuver_summary_plot()
            
            # Altitude distribution
            plots['altitude_distribution'] = self._create_altitude_distribution_plot()
            
            return plots
            
        except Exception as e:
            logger.error(f"❌ Error creating dashboard plots: {e}")
            return {}
    
    def _add_earth_to_plot(self, fig: go.Figure):
        """Add enhanced Earth sphere to the 3D plot"""
        try:
            # Create Earth sphere with higher resolution
            phi = np.linspace(0, 2*np.pi, 120)
            theta = np.linspace(-np.pi/2, np.pi/2, 60)
            phi, theta = np.meshgrid(phi, theta)
            
            x = self.earth_radius * np.cos(theta) * np.cos(phi)
            y = self.earth_radius * np.cos(theta) * np.sin(phi)
            z = self.earth_radius * np.sin(theta)
            
            # Create realistic Earth colorscale
            earth_colorscale = [
                [0.0, '#1e3a8a'],  # Deep ocean blue
                [0.2, '#3b82f6'],  # Ocean blue
                [0.4, '#60a5fa'],  # Light blue
                [0.6, '#22c55e'],  # Green land
                [0.8, '#16a34a'],  # Dark green
                [1.0, '#15803d']   # Forest green
            ]
            
            fig.add_trace(go.Surface(
                x=x, y=y, z=z,
                colorscale=earth_colorscale,
                showscale=False,
                name='Earth',
                opacity=0.9,
                lighting=dict(
                    ambient=0.3,
                    diffuse=0.8,
                    specular=0.1,
                    roughness=0.8
                )
            ))
            
            # Add subtle atmosphere glow
            atmosphere_radius = self.earth_radius * 1.02
            x_atm = atmosphere_radius * np.cos(theta) * np.cos(phi)
            y_atm = atmosphere_radius * np.cos(theta) * np.sin(phi)
            z_atm = atmosphere_radius * np.sin(theta)
            
            fig.add_trace(go.Surface(
                x=x_atm, y=y_atm, z=z_atm,
                colorscale=[[0, 'rgba(135, 206, 250, 0.1)'], [1, 'rgba(135, 206, 250, 0.05)']],
                showscale=False,
                name='Atmosphere',
                opacity=0.2
            ))
            
        except Exception as e:
            logger.error(f"❌ Error adding Earth to plot: {e}")
    
    def _add_space_background(self, fig: go.Figure):
        """Add space background with stars"""
        try:
            # Generate random star field
            num_stars = 150
            star_distances = np.random.uniform(30000, 80000, num_stars)  # km
            star_angles_phi = np.random.uniform(0, 2*np.pi, num_stars)
            star_angles_theta = np.random.uniform(-np.pi/2, np.pi/2, num_stars)
            
            star_x = star_distances * np.cos(star_angles_theta) * np.cos(star_angles_phi)
            star_y = star_distances * np.cos(star_angles_theta) * np.sin(star_angles_phi)
            star_z = star_distances * np.sin(star_angles_theta)
            
            fig.add_trace(go.Scatter3d(
                x=star_x,
                y=star_y,
                z=star_z,
                mode='markers',
                marker=dict(
                    size=0.8,
                    color=self.colors['stars'],
                    opacity=0.6
                ),
                name='Stars',
                showlegend=False
            ))
            
        except Exception as e:
            logger.error(f"❌ Error adding space background: {e}")
    
    def _add_sun_to_plot(self, fig: go.Figure):
        """Add Sun to the plot (scaled for visibility)"""
        try:
            # Scale down Sun for visualization
            scaled_radius = 3000  # km
            scaled_distance = 80000  # km
            
            # Position Sun at a fixed location
            sun_x = scaled_distance
            sun_y = 0
            sun_z = 0
            
            # Create Sun sphere
            phi = np.linspace(0, 2*np.pi, 40)
            theta = np.linspace(-np.pi/2, np.pi/2, 20)
            phi, theta = np.meshgrid(phi, theta)
            
            x = sun_x + scaled_radius * np.cos(theta) * np.cos(phi)
            y = sun_y + scaled_radius * np.cos(theta) * np.sin(phi)
            z = sun_z + scaled_radius * np.sin(theta)
            
            fig.add_trace(go.Surface(
                x=x, y=y, z=z,
                colorscale=[[0, '#ffff00'], [0.5, '#ffaa00'], [1, '#ff6600']],
                showscale=False,
                name='Sun',
                opacity=0.8
            ))
            
        except Exception as e:
            logger.error(f"❌ Error adding Sun to plot: {e}")
    
    def _add_moon_to_plot(self, fig: go.Figure):
        """Add Moon to the plot"""
        try:
            # Moon parameters
            moon_distance = 384400  # km from Earth
            moon_radius = 1737.4    # km
            
            # Calculate Moon position (simplified)
            import time
            current_time = time.time()
            moon_angle = (current_time / (27.3 * 24 * 3600)) * 2 * np.pi  # 27.3 day period
            
            moon_x = moon_distance * np.cos(moon_angle)
            moon_y = moon_distance * np.sin(moon_angle)
            moon_z = 0
            
            # Create Moon sphere
            phi = np.linspace(0, 2*np.pi, 25)
            theta = np.linspace(-np.pi/2, np.pi/2, 12)
            phi, theta = np.meshgrid(phi, theta)
            
            x = moon_x + moon_radius * np.cos(theta) * np.cos(phi)
            y = moon_y + moon_radius * np.cos(theta) * np.sin(phi)
            z = moon_z + moon_radius * np.sin(theta)
            
            fig.add_trace(go.Surface(
                x=x, y=y, z=z,
                colorscale=[[0, '#c0c0c0'], [1, '#808080']],
                showscale=False,
                name='Moon',
                opacity=0.7
            ))
            
        except Exception as e:
            logger.error(f"❌ Error adding Moon to plot: {e}")
    
    def _add_satellites_to_plot(self, fig: go.Figure):
        """Add satellite positions to the 3D plot"""
        try:
            for sat_id, sat_data in self.current_data['satellites'].items():
                # Get current position (first position in the list)
                if 'positions' in sat_data and sat_data['positions']:
                    current_pos = sat_data['positions'][0]
                    
                    # Determine color and marker based on object type and data source
                    object_type = sat_data.get('object_type', 'satellite')
                    is_realtime = sat_data.get('real_time', False)
                    data_source = sat_data.get('data_source', 'Unknown')
                    
                    if is_realtime:
                        color = '#00ffff'  # Cyan for real-time satellites
                        symbol = 'star'
                        size = 8
                        name_prefix = "🛰️ LIVE "
                    else:
                        color = self.colors.get(object_type, self.colors['satellite'])
                        symbol = 'diamond'
                        size = 5
                        name_prefix = ""
                    
                    # Add satellite marker
                    fig.add_trace(go.Scatter3d(
                        x=[current_pos['x']],
                        y=[current_pos['y']],
                        z=[current_pos['z']],
                        mode='markers',
                        marker=dict(
                            size=size,
                            color=color,
                            symbol=symbol,
                            line=dict(width=2, color='white') if is_realtime else dict(width=1, color='black')
                        ),
                        name=f"{name_prefix}{sat_data.get('name', f'Satellite {sat_id}')}",
                        text=f"{sat_data.get('name', 'Unknown')}<br>Altitude: {current_pos['altitude']:.1f} km<br>Velocity: {current_pos['velocity']:.1f} km/s<br>Source: {data_source}<br>Real-time: {'Yes' if is_realtime else 'No'}",
                        hovertemplate='%{text}<extra></extra>'
                    ))
                    
                    # Add orbit trace (simplified)
                    if len(sat_data['positions']) > 1:
                        orbit_x = [pos['x'] for pos in sat_data['positions']]
                        orbit_y = [pos['y'] for pos in sat_data['positions']]
                        orbit_z = [pos['z'] for pos in sat_data['positions']]
                        
                        # Different line styles for real-time vs simulated satellites
                        if is_realtime:
                            line_style = dict(
                                color=color,
                                width=2,
                                dash='solid'
                            )
                            opacity = 0.6
                        else:
                            line_style = dict(
                                color=color,
                                width=1,
                                dash='dot'
                            )
                            opacity = 0.3
                        
                        fig.add_trace(go.Scatter3d(
                            x=orbit_x,
                            y=orbit_y,
                            z=orbit_z,
                            mode='lines',
                            line=line_style,
                            name=f"Orbit {sat_id}",
                            showlegend=False,
                            opacity=opacity
                        ))
            
        except Exception as e:
            logger.error(f"❌ Error adding satellites to plot: {e}")
    
    def _add_collision_indicators(self, fig: go.Figure):
        """Add collision risk indicators to the 3D plot"""
        try:
            for collision in self.current_data['collisions']:
                closest_approach = collision['closest_approach']
                pos1 = closest_approach['position1']
                pos2 = closest_approach['position2']
                
                # Determine color based on risk level
                risk_level = collision['risk_level']
                color = self.colors.get(f'collision_{risk_level}', self.colors['collision_medium'])
                
                # Add collision point marker
                mid_x = (pos1['x'] + pos2['x']) / 2
                mid_y = (pos1['y'] + pos2['y']) / 2
                mid_z = (pos1['z'] + pos2['z']) / 2
                
                fig.add_trace(go.Scatter3d(
                    x=[mid_x],
                    y=[mid_y],
                    z=[mid_z],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=color,
                        symbol='x'
                    ),
                    name=f"Collision Risk: {collision['satellite1_name']} vs {collision['satellite2_name']}",
                    text=f"Risk: {risk_level.upper()}<br>Distance: {closest_approach['distance']:.2f} km<br>Probability: {collision['collision_probability']:.3f}",
                    hovertemplate='%{text}<extra></extra>'
                ))
                
                # Add line connecting colliding satellites
                fig.add_trace(go.Scatter3d(
                    x=[pos1['x'], pos2['x']],
                    y=[pos1['y'], pos2['y']],
                    z=[pos1['z'], pos2['z']],
                    mode='lines',
                    line=dict(
                        color=color,
                        width=3
                    ),
                    name=f"Collision Path {collision['satellite1_id']}-{collision['satellite2_id']}",
                    showlegend=False
                ))
                
        except Exception as e:
            logger.error(f"❌ Error adding collision indicators: {e}")
    
    def _add_maneuver_trajectories(self, fig: go.Figure):
        """Add maneuver trajectories to the 3D plot"""
        try:
            for maneuver in self.current_data['maneuvers']:
                # Add maneuver execution point
                if 'execution_time' in maneuver:
                    # This would show where the maneuver will be executed
                    # For now, just add a marker
                    fig.add_trace(go.Scatter3d(
                        x=[0],  # Placeholder
                        y=[0],  # Placeholder
                        z=[0],  # Placeholder
                        mode='markers',
                        marker=dict(
                            size=6,
                            color=self.colors['maneuver'],
                            symbol='star'
                        ),
                        name=f"Maneuver: {maneuver.get('maneuver_satellite_id', 'Unknown')}",
                        text=f"Type: {maneuver.get('maneuver_type', 'Unknown')}<br>Delta-V: {maneuver.get('delta_v_magnitude', 0):.2f} m/s<br>Execution: {maneuver.get('execution_time', 'Unknown')}",
                        hovertemplate='%{text}<extra></extra>'
                    ))
                    
        except Exception as e:
            logger.error(f"❌ Error adding maneuver trajectories: {e}")
    
    def _update_3d_layout(self, fig: go.Figure):
        """Update 3D plot layout with space theme"""
        fig.update_layout(
            title=dict(
                text="🌌 Space Traffic Management - 3D View",
                font=dict(size=18, color='white'),
                x=0.5
            ),
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color='white'),
            scene=dict(
                xaxis=dict(
                    title=dict(text="X (km)", font=dict(color='white')),
                    tickfont=dict(color='white'),
                    gridcolor='rgba(255,255,255,0.1)',
                    backgroundcolor='black'
                ),
                yaxis=dict(
                    title=dict(text="Y (km)", font=dict(color='white')),
                    tickfont=dict(color='white'),
                    gridcolor='rgba(255,255,255,0.1)',
                    backgroundcolor='black'
                ),
                zaxis=dict(
                    title=dict(text="Z (km)", font=dict(color='white')),
                    tickfont=dict(color='white'),
                    gridcolor='rgba(255,255,255,0.1)',
                    backgroundcolor='black'
                ),
                bgcolor='black',
                aspectmode='data',
                camera=dict(
                    eye=dict(x=1.8, y=1.8, z=1.2),
                    center=dict(x=0, y=0, z=0),
                    up=dict(x=0, y=0, z=1)
                )
            ),
            width=1100,
            height=850,
            showlegend=True,
            legend=dict(
                bgcolor='rgba(0,0,0,0.7)',
                font=dict(color='white'),
                x=0.02,
                y=0.98
            )
        )
    
    def _create_satellite_distribution_plot(self) -> go.Figure:
        """Create satellite distribution by type plot"""
        try:
            satellite_types = {}
            for sat_data in self.current_data['satellites'].values():
                sat_type = sat_data.get('object_type', 'satellite')
                satellite_types[sat_type] = satellite_types.get(sat_type, 0) + 1
            
            fig = px.pie(
                values=list(satellite_types.values()),
                names=list(satellite_types.keys()),
                title="Satellite Distribution by Type",
                color_discrete_map={
                    'satellite': self.colors['satellite'],
                    'debris': self.colors['debris']
                }
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Error creating satellite distribution plot: {e}")
            return self._create_error_plot()
    
    def _create_collision_timeline_plot(self) -> go.Figure:
        """Create collision risk timeline plot"""
        try:
            if not self.current_data['collisions']:
                # Create empty plot
                fig = go.Figure()
                fig.add_annotation(
                    text="No collisions detected",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                fig.update_layout(title="Collision Risk Timeline")
                return fig
            
            # Extract collision data
            times = []
            distances = []
            risk_levels = []
            
            for collision in self.current_data['collisions']:
                closest_time = collision['closest_approach']['time']
                distance = collision['closest_approach']['distance']
                risk_level = collision['risk_level']
                
                times.append(closest_time)
                distances.append(distance)
                risk_levels.append(risk_level)
            
            # Create scatter plot
            fig = px.scatter(
                x=times,
                y=distances,
                color=risk_levels,
                title="Collision Risk Timeline",
                labels={'x': 'Time', 'y': 'Distance (km)', 'color': 'Risk Level'},
                color_discrete_map={
                    'high': self.colors['collision_high'],
                    'medium': self.colors['collision_medium'],
                    'low': self.colors['collision_low']
                }
            )
            
            # Add safety threshold line
            fig.add_hline(y=5, line_dash="dash", line_color="red", annotation_text="Safety Threshold")
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Error creating collision timeline plot: {e}")
            return self._create_error_plot()
    
    def _create_maneuver_summary_plot(self) -> go.Figure:
        """Create maneuver summary plot"""
        try:
            if not self.current_data['maneuvers']:
                # Create empty plot
                fig = go.Figure()
                fig.add_annotation(
                    text="No maneuvers planned",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                fig.update_layout(title="Maneuver Summary")
                return fig
            
            # Extract maneuver data
            maneuver_types = {}
            delta_v_values = []
            
            for maneuver in self.current_data['maneuvers']:
                maneuver_type = maneuver.get('maneuver_type', 'unknown')
                delta_v = maneuver.get('delta_v_magnitude', 0)
                
                maneuver_types[maneuver_type] = maneuver_types.get(maneuver_type, 0) + 1
                delta_v_values.append(delta_v)
            
            # Create subplots
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Maneuver Types', 'Delta-V Distribution'),
                specs=[[{"type": "pie"}, {"type": "histogram"}]]
            )
            
            # Add pie chart
            fig.add_trace(
                go.Pie(
                    labels=list(maneuver_types.keys()),
                    values=list(maneuver_types.values()),
                    name="Maneuver Types"
                ),
                row=1, col=1
            )
            
            # Add histogram
            fig.add_trace(
                go.Histogram(
                    x=delta_v_values,
                    name="Delta-V Distribution",
                    nbinsx=10
                ),
                row=1, col=2
            )
            
            fig.update_layout(title="Maneuver Summary")
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Error creating maneuver summary plot: {e}")
            return self._create_error_plot()
    
    def _create_altitude_distribution_plot(self) -> go.Figure:
        """Create altitude distribution plot"""
        try:
            altitudes = []
            object_types = []
            
            for sat_data in self.current_data['satellites'].values():
                if 'positions' in sat_data and sat_data['positions']:
                    altitude = sat_data['positions'][0]['altitude']
                    object_type = sat_data.get('object_type', 'satellite')
                    
                    altitudes.append(altitude)
                    object_types.append(object_type)
            
            if not altitudes:
                # Create empty plot
                fig = go.Figure()
                fig.add_annotation(
                    text="No satellite data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                fig.update_layout(title="Altitude Distribution")
                return fig
            
            # Create histogram
            fig = px.histogram(
                x=altitudes,
                color=object_types,
                title="Altitude Distribution",
                labels={'x': 'Altitude (km)', 'y': 'Count', 'color': 'Object Type'},
                color_discrete_map={
                    'satellite': self.colors['satellite'],
                    'debris': self.colors['debris']
                }
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Error creating altitude distribution plot: {e}")
            return self._create_error_plot()
    
    def _create_error_plot(self) -> go.Figure:
        """Create error plot when visualization fails"""
        fig = go.Figure()
        fig.add_annotation(
            text="Error creating visualization",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="Visualization Error")
        return fig
    
    def export_visualization_data(self, format: str = 'json') -> str:
        """
        Export visualization data for external use
        
        Args:
            format: Export format ('json', 'csv')
            
        Returns:
            Exported data as string
        """
        try:
            if format.lower() == 'json':
                return json.dumps(self.current_data, indent=2, default=str)
            elif format.lower() == 'csv':
                # Convert to CSV format
                # This would need more complex logic for nested data
                return "CSV export not implemented yet"
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"❌ Error exporting visualization data: {e}")
            return ""
    
    def get_visualization_stats(self) -> Dict[str, Any]:
        """Get statistics about current visualization data"""
        try:
            stats = {
                'total_satellites': len(self.current_data['satellites']),
                'active_satellites': 0,
                'debris_objects': 0,
                'total_collisions': len(self.current_data['collisions']),
                'high_risk_collisions': 0,
                'medium_risk_collisions': 0,
                'low_risk_collisions': 0,
                'total_maneuvers': len(self.current_data['maneuvers']),
                'last_update': datetime.now().isoformat()
            }
            
            # Count satellite types
            for sat_data in self.current_data['satellites'].values():
                object_type = sat_data.get('object_type', 'satellite')
                if object_type == 'satellite':
                    stats['active_satellites'] += 1
                elif object_type == 'debris':
                    stats['debris_objects'] += 1
            
            # Count collision risk levels
            for collision in self.current_data['collisions']:
                risk_level = collision['risk_level']
                if risk_level == 'high':
                    stats['high_risk_collisions'] += 1
                elif risk_level == 'medium':
                    stats['medium_risk_collisions'] += 1
                elif risk_level == 'low':
                    stats['low_risk_collisions'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting visualization stats: {e}")
            return {}
