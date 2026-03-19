"""
Configuration Settings for Space Traffic Management System
"""

import os
from typing import Dict, Any

# System Configuration
SYSTEM_CONFIG = {
    'name': 'Space Traffic Management System',
    'version': '1.0.0',
    'description': 'AI-powered satellite collision avoidance system',
    'author': 'Space Traffic Team',
    'contact': 'contact@spacetraffic.com'
}

# Data Collection Settings
DATA_COLLECTION_CONFIG = {
    'update_frequency': 10,  # seconds
    'max_retries': 3,
    'timeout': 30,  # seconds
    'cache_duration': 300,  # seconds
    
    # API endpoints
    'celestrak_url': 'https://celestrak.org/NORAD/elements/',
    'space_track_url': 'https://www.space-track.org/api/',
    
    # Sample data settings
    'use_sample_data': True,  # Use sample data when APIs are unavailable
    'sample_satellite_count': 5
}

# Orbit Propagation Settings
ORBIT_PROPAGATION_CONFIG = {
    'propagation_horizon': 7,  # days
    'time_step': 6,  # hours between predictions
    'earth_radius': 6378.137,  # km
    'mu_earth': 398600.4418,  # km³/s²
    
    # Propagation methods
    'use_sgp4': True,
    'use_simplified': True,
    'use_fallback': True
}

# Collision Detection Settings
COLLISION_DETECTION_CONFIG = {
    'collision_threshold': 10.0,  # km - minimum distance for collision risk
    'high_risk_threshold': 1.0,   # km - high risk collision distance
    'medium_risk_threshold': 5.0, # km - medium risk collision distance
    
    # ML model settings
    'ml_model_path': 'data/collision_model.pkl',
    'use_ml_prediction': True,
    'confidence_threshold': 0.7,
    
    # Risk assessment
    'position_uncertainty': 0.1,  # km
    'velocity_uncertainty': 0.01, # km/s
    'object_size_factor': 1.0
}

# Maneuver Planning Settings
MANEUVER_PLANNING_CONFIG = {
    'max_delta_v': 100.0,  # m/s - maximum maneuver capability
    'min_safety_distance': 5.0,  # km - minimum safe distance after maneuver
    'fuel_efficiency_weight': 0.7,
    'safety_weight': 0.3,
    
    # Maneuver types
    'maneuver_types': {
        'fine_adjustment': {'max_delta_v': 1.0},
        'minor_maneuver': {'max_delta_v': 10.0},
        'major_maneuver': {'max_delta_v': 50.0},
        'emergency_maneuver': {'max_delta_v': 100.0}
    },
    
    # Execution settings
    'min_execution_time': 30,  # minutes before closest approach
    'max_execution_time': 24,  # hours before closest approach
    'execution_margin': 60,    # minutes
}

# Visualization Settings
VISUALIZATION_CONFIG = {
    'earth_radius': 6378.137,  # km
    'plot_width': 1000,
    'plot_height': 800,
    'update_frequency': 5,  # seconds
    
    # Colors
    'colors': {
        'satellite': '#00ff00',      # Green for active satellites
        'debris': '#ff0000',         # Red for debris
        'collision_high': '#ff0000', # Red for high risk
        'collision_medium': '#ffaa00', # Orange for medium risk
        'collision_low': '#ffff00',  # Yellow for low risk
        'maneuver': '#0000ff',       # Blue for maneuvers
        'earth': '#0066cc'           # Blue for Earth
    },
    
    # Display settings
    'show_orbits': True,
    'show_collision_paths': True,
    'show_maneuver_trajectories': True,
    'show_earth': True
}

# Dashboard Settings
DASHBOARD_CONFIG = {
    'title': 'Space Traffic Management System',
    'page_icon': '🚀',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
    
    # Update settings
    'auto_refresh': True,
    'refresh_interval': 10,  # seconds
    
    # Display settings
    'show_3d_view': True,
    'show_analytics': True,
    'show_alerts': True,
    'show_maneuvers': True,
    
    # Export settings
    'export_formats': ['json', 'csv'],
    'export_directory': 'exports/'
}

# API Settings
API_CONFIG = {
    'host': '0.0.0.0',
    'port': 8000,
    'debug': True,
    'reload': True,
    
    # CORS settings
    'cors_origins': ['*'],
    'cors_methods': ['GET', 'POST', 'PUT', 'DELETE'],
    'cors_headers': ['*']
}

# Database Settings
DATABASE_CONFIG = {
    'type': 'sqlite',  # sqlite, postgresql, mysql
    'host': 'localhost',
    'port': 5432,
    'database': 'space_traffic.db',
    'username': '',
    'password': '',
    
    # Connection settings
    'pool_size': 10,
    'max_overflow': 20,
    'pool_timeout': 30,
    'pool_recycle': 3600
}

# Logging Settings
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/space_traffic.log',
    'max_size': 10 * 1024 * 1024,  # 10 MB
    'backup_count': 5
}

# Alert Settings
ALERT_CONFIG = {
    'email_enabled': False,
    'email_smtp_server': 'smtp.gmail.com',
    'email_smtp_port': 587,
    'email_username': '',
    'email_password': '',
    'email_recipients': [],
    
    'slack_enabled': False,
    'slack_webhook_url': '',
    'slack_channel': '#space-traffic',
    
    'notification_levels': ['high', 'medium'],  # Which risk levels to notify
    'notification_frequency': 300  # seconds between notifications
}

# Security Settings
SECURITY_CONFIG = {
    'api_key_required': False,
    'api_key_header': 'X-API-Key',
    'rate_limit_enabled': True,
    'rate_limit_requests': 100,
    'rate_limit_window': 3600,  # seconds
    
    'cors_enabled': True,
    'authentication_enabled': False
}

# Performance Settings
PERFORMANCE_CONFIG = {
    'max_concurrent_requests': 100,
    'request_timeout': 30,  # seconds
    'cache_enabled': True,
    'cache_ttl': 300,  # seconds
    
    'background_tasks': True,
    'task_queue_size': 1000,
    'worker_processes': 4
}

# Development Settings
DEVELOPMENT_CONFIG = {
    'debug_mode': True,
    'use_mock_data': True,
    'log_level': 'DEBUG',
    'auto_reload': True,
    
    # Testing
    'test_mode': False,
    'test_data_size': 10,
    'test_timeout': 30
}

def get_config() -> Dict[str, Any]:
    """Get complete configuration"""
    return {
        'system': SYSTEM_CONFIG,
        'data_collection': DATA_COLLECTION_CONFIG,
        'orbit_propagation': ORBIT_PROPAGATION_CONFIG,
        'collision_detection': COLLISION_DETECTION_CONFIG,
        'maneuver_planning': MANEUVER_PLANNING_CONFIG,
        'visualization': VISUALIZATION_CONFIG,
        'dashboard': DASHBOARD_CONFIG,
        'api': API_CONFIG,
        'database': DATABASE_CONFIG,
        'logging': LOGGING_CONFIG,
        'alert': ALERT_CONFIG,
        'security': SECURITY_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'development': DEVELOPMENT_CONFIG
    }

def get_setting(category: str, key: str, default: Any = None) -> Any:
    """Get a specific setting value"""
    config = get_config()
    return config.get(category, {}).get(key, default)

def update_setting(category: str, key: str, value: Any) -> bool:
    """Update a specific setting value"""
    try:
        config = get_config()
        if category in config and key in config[category]:
            config[category][key] = value
            return True
        return False
    except Exception:
        return False
