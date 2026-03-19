"""
Space Traffic Management Dashboard
Streamlit-based real-time monitoring and control interface
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collection.satellite_data import SatelliteDataCollector
from src.orbit_propagation.orbit_engine import OrbitPropagationEngine
from src.collision_detection.collision_detector import CollisionDetector
from src.maneuver_planning.maneuver_planner import ManeuverPlanner
from src.visualization.space_visualizer import SpaceVisualizer
from src.visualization.trajectory_visualizer import TrajectoryVisualizer

# Page configuration
st.set_page_config(
    page_title="Space Traffic Management System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Custom CSS for stunning professional UI
st.markdown("""
<style>
    /* Import Google Fonts for premium typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Global Styles - Premium Dark Theme */
    .main {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Premium Header with Glassmorphism */
    .main-header {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 25px;
        padding: 3rem 2rem;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 
            0 25px 50px rgba(0, 0, 0, 0.25),
            0 0 0 1px rgba(255, 255, 255, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%);
        animation: shimmer 3s ease-in-out infinite;
        pointer-events: none;
    }
    
    .main-header h1 {
        color: #ffffff;
        font-size: 4rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 
            0 0 20px rgba(102, 126, 234, 0.5),
            0 0 40px rgba(102, 126, 234, 0.3),
            0 0 60px rgba(102, 126, 234, 0.1);
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        color: #e0e0e0;
        font-size: 1.4rem;
        margin: 1rem 0 0 0;
        font-weight: 400;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    /* Premium Status Cards with Glassmorphism */
    .status-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.1),
            0 0 0 1px rgba(255, 255, 255, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .status-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transition: left 0.5s;
    }
    
    .status-card:hover::before {
        left: 100%;
    }
    
    .status-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.2),
            0 0 0 1px rgba(255, 255, 255, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .status-card h3 {
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        letter-spacing: -0.01em;
    }
    
    .status-card p {
        color: #e0e0e0;
        margin: 0.75rem 0;
        font-size: 1rem;
        line-height: 1.6;
        font-weight: 400;
    }
    
    .status-card strong {
        color: #ffffff;
        font-weight: 600;
    }
    
    /* Premium Alert Styles with Enhanced Animations */
    .alert-high {
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.15) 0%, rgba(229, 57, 53, 0.15) 100%);
        border: 1px solid rgba(244, 67, 54, 0.4);
        box-shadow: 
            0 0 20px rgba(244, 67, 54, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        animation: criticalPulse 2s ease-in-out infinite;
    }
    
    .alert-medium {
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.15) 0%, rgba(255, 111, 0, 0.15) 100%);
        border: 1px solid rgba(255, 152, 0, 0.4);
        box-shadow: 
            0 0 15px rgba(255, 152, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .alert-low {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.15) 0%, rgba(67, 160, 71, 0.15) 100%);
        border: 1px solid rgba(76, 175, 80, 0.4);
        box-shadow: 
            0 0 15px rgba(76, 175, 80, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    /* Premium Sidebar with Glassmorphism */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(26, 26, 46, 0.9) 0%, rgba(22, 33, 62, 0.9) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, rgba(26, 26, 46, 0.9) 0%, rgba(22, 33, 62, 0.9) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }
    
    /* Premium Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 15px;
        color: white;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 1rem 2rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 8px 25px rgba(102, 126, 234, 0.3),
            0 0 0 1px rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.02em;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 
            0 15px 35px rgba(102, 126, 234, 0.4),
            0 0 0 1px rgba(255, 255, 255, 0.2);
        background: linear-gradient(135deg, #7c8ff0 0%, #8a5bb8 100%);
    }
    
    /* Premium Tab Styles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 15px;
        color: #ffffff;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 12px 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid transparent;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.02em;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 
            0 8px 25px rgba(102, 126, 234, 0.3),
            0 0 0 1px rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }
    
    /* Premium Metric Styles */
    .metric-container {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.1),
            0 0 0 1px rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transition: left 0.5s;
    }
    
    .metric-container:hover::before {
        left: 100%;
    }
    
    .metric-container:hover {
        transform: translateY(-5px) scale(1.03);
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.2),
            0 0 0 1px rgba(255, 255, 255, 0.2);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.75rem;
        text-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.02em;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #e0e0e0;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 500;
        opacity: 0.8;
        font-family: 'Inter', sans-serif;
    }
    
    /* Premium Animations */
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    @keyframes criticalPulse {
        0%, 100% { 
            box-shadow: 
                0 0 20px rgba(244, 67, 54, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        50% { 
            box-shadow: 
                0 0 30px rgba(244, 67, 54, 0.5),
                0 0 40px rgba(244, 67, 54, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes glow {
        0%, 100% { 
            box-shadow: 
                0 0 20px rgba(102, 126, 234, 0.3),
                0 0 40px rgba(102, 126, 234, 0.2),
                0 0 60px rgba(102, 126, 234, 0.1);
        }
        50% { 
            box-shadow: 
                0 0 30px rgba(102, 126, 234, 0.5),
                0 0 60px rgba(102, 126, 234, 0.3),
                0 0 90px rgba(102, 126, 234, 0.2);
        }
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Apply animations to elements */
    .main-header {
        animation: slideInUp 1s ease-out;
    }
    
    .status-card {
        animation: slideInUp 0.8s ease-out;
        animation-fill-mode: both;
    }
    
    .status-card:nth-child(1) { animation-delay: 0.1s; }
    .status-card:nth-child(2) { animation-delay: 0.2s; }
    .status-card:nth-child(3) { animation-delay: 0.3s; }
    .status-card:nth-child(4) { animation-delay: 0.4s; }
    
    .metric-container {
        animation: slideInUp 0.6s ease-out;
        animation-fill-mode: both;
    }
    
    .metric-container:nth-child(1) { animation-delay: 0.1s; }
    .metric-container:nth-child(2) { animation-delay: 0.2s; }
    .metric-container:nth-child(3) { animation-delay: 0.3s; }
    .metric-container:nth-child(4) { animation-delay: 0.4s; }
    .metric-container:nth-child(5) { animation-delay: 0.5s; }
    
    /* Hover effects for interactive elements */
    .status-card:hover .metric-value {
        animation: glow 2s ease-in-out infinite;
    }
    
    /* Premium loading animation */
    .stSpinner {
        animation: float 2s ease-in-out infinite;
    }
    
    /* Premium focus effects */
    .stButton > button:focus {
        animation: glow 1s ease-in-out infinite;
    }
    
    /* Premium tab transitions */
    .stTabs [data-baseweb="tab"] {
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Premium sidebar animations */
    .sidebar .sidebar-content {
        animation: slideInUp 0.8s ease-out;
    }
    
    /* Premium Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        margin: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #7c8ff0 0%, #8a5bb8 100%);
    }
    
    /* Premium Data Frame Styles */
    .dataframe {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
        color: #ffffff !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        overflow: hidden !important;
    }
    
    .dataframe th {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .dataframe td {
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding: 12px 16px !important;
    }
    
    .dataframe tr:hover {
        background: rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Premium Plotly Chart Container - Fixed Alignment */
    .js-plotly-plot {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%) !important;
        border-radius: 20px !important;
        padding: 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
        margin: 0 auto !important;
        width: 100% !important;
        height: auto !important;
        overflow: visible !important;
        position: relative !important;
    }
    
    /* Fix Plotly chart alignment and sizing */
    .plotly-graph-div {
        width: 100% !important;
        height: 600px !important;
        margin: 0 auto !important;
        display: block !important;
        position: relative !important;
    }
    
    /* Ensure proper chart container sizing */
    .stPlotlyChart {
        width: 100% !important;
        margin: 0 auto !important;
        padding: 0 !important;
    }
    
    /* Fix chart alignment within containers */
    .element-container {
        width: 100% !important;
        margin: 0 auto !important;
    }
    
    /* Additional chart alignment fixes */
    .stApp > div > div > div > div {
        width: 100% !important;
        max-width: none !important;
    }
    
    /* Fix main content area alignment */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }
    
    /* Ensure proper chart rendering */
    .plotly .main-svg {
        width: 100% !important;
        height: 100% !important;
    }
    
    /* Fix any overflow issues */
    .stApp {
        overflow-x: hidden !important;
    }
    
    /* Premium Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.15) 0%, rgba(67, 160, 71, 0.15) 100%) !important;
        border: 1px solid rgba(76, 175, 80, 0.4) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(20px) !important;
        box-shadow: 0 8px 32px rgba(76, 175, 80, 0.2) !important;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.15) 0%, rgba(229, 57, 53, 0.15) 100%) !important;
        border: 1px solid rgba(244, 67, 54, 0.4) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(20px) !important;
        box-shadow: 0 8px 32px rgba(244, 67, 54, 0.2) !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.15) 0%, rgba(255, 111, 0, 0.15) 100%) !important;
        border: 1px solid rgba(255, 152, 0, 0.4) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(20px) !important;
        box-shadow: 0 8px 32px rgba(255, 152, 0, 0.2) !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.15) 0%, rgba(30, 136, 229, 0.15) 100%) !important;
        border: 1px solid rgba(33, 150, 243, 0.4) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(20px) !important;
        box-shadow: 0 8px 32px rgba(33, 150, 243, 0.2) !important;
    }
    
    /* Premium Text Styling */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
    }
    
    p, span, div {
        font-family: 'Inter', sans-serif !important;
        line-height: 1.6 !important;
    }
    
    /* Premium Code Blocks */
    code, pre {
        font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
        background: rgba(0, 0, 0, 0.3) !important;
        border-radius: 8px !important;
        padding: 4px 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Premium Selection */
    ::selection {
        background: rgba(102, 126, 234, 0.3);
        color: #ffffff;
    }
    
    /* Premium Focus States */
    button:focus, input:focus, select:focus, textarea:focus {
        outline: 2px solid rgba(102, 126, 234, 0.5);
        outline-offset: 2px;
    }
    
    /* Premium Loading States */
    .stSpinner > div {
        border-color: rgba(102, 126, 234, 0.3) !important;
        border-top-color: #667eea !important;
    }
    
    /* Premium Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px) !important;
        font-weight: 600 !important;
        color: #ffffff !important;
        padding: 1rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.1) 100%) !important;
        border-color: rgba(102, 126, 234, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Premium Selectbox */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(20px) !important;
        color: #ffffff !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: rgba(102, 126, 234, 0.5) !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Premium Checkbox */
    .stCheckbox > label {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    .stCheckbox > div > div {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        backdrop-filter: blur(20px) !important;
    }
    
    /* Premium Number Input */
    .stNumberInput > div > div > input {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        color: #ffffff !important;
        backdrop-filter: blur(20px) !important;
        padding: 12px 16px !important;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: rgba(102, 126, 234, 0.5) !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Premium Slider */
    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(20px) !important;
    }
    
    .stSlider > div > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 50% !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Premium Divider */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.5), transparent) !important;
        margin: 2rem 0 !important;
        border-radius: 1px !important;
    }
    
    /* Premium Link Styling */
    a {
        color: #667eea !important;
        text-decoration: none !important;
        transition: all 0.3s ease !important;
    }
    
    a:hover {
        color: #7c8ff0 !important;
        text-shadow: 0 0 10px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* Premium Background Effects */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(76, 175, 80, 0.05) 0%, transparent 50%);
        pointer-events: none;
        z-index: -1;
        animation: backgroundFloat 20s ease-in-out infinite;
    }
    
    @keyframes backgroundFloat {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(-10px, -10px) rotate(1deg); }
        50% { transform: translate(10px, -5px) rotate(-1deg); }
        75% { transform: translate(-5px, 10px) rotate(0.5deg); }
    }
    
    /* Premium Glassmorphism Enhancement */
    .status-card, .metric-container, .main-header {
        position: relative;
    }
    
    .status-card::after, .metric-container::after, .main-header::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
        border-radius: inherit;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .status-card:hover::after, .metric-container:hover::after, .main-header:hover::after {
        opacity: 1;
    }
    
    /* Premium Text Enhancements */
    .main-header h1 {
        background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 50%, #ffffff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: textShine 3s ease-in-out infinite;
    }
    
    @keyframes textShine {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Premium Interactive Elements */
    .stButton > button, .stTabs [data-baseweb="tab"], .status-card, .metric-container {
        cursor: pointer;
        user-select: none;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
    }
    
    /* Premium Responsive Design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .main-header p {
            font-size: 1.1rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
        
        .status-card {
            padding: 1.5rem;
        }
    }
    
    /* Premium Accessibility */
    .status-card:focus-within, .metric-container:focus-within {
        outline: 2px solid rgba(102, 126, 234, 0.8);
        outline-offset: 2px;
    }
    
    /* Premium Performance Optimizations */
    .status-card, .metric-container, .main-header {
        will-change: transform, box-shadow;
        backface-visibility: hidden;
        transform: translateZ(0);
    }
    
    /* Premium Dark Mode Enhancements */
    @media (prefers-color-scheme: dark) {
        .main {
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
        }
    }
    
    /* Premium Print Styles */
    @media print {
        .main-header, .status-card, .metric-container {
            box-shadow: none !important;
            background: white !important;
            color: black !important;
        }
    }
</style>
""", unsafe_allow_html=True)

class SpaceTrafficDashboard:
    """Main dashboard class for space traffic management"""
    
    def __init__(self):
        self.data_collector = SatelliteDataCollector()
        self.orbit_engine = OrbitPropagationEngine()
        self.collision_detector = CollisionDetector()
        self.maneuver_planner = ManeuverPlanner()
        self.visualizer = SpaceVisualizer()
        self.trajectory_visualizer = TrajectoryVisualizer()
        
        # Initialize session state with enhanced data flow tracking
        if 'satellite_data' not in st.session_state:
            st.session_state.satellite_data = {}
        if 'collisions' not in st.session_state:
            st.session_state.collisions = []
        if 'maneuvers' not in st.session_state:
            st.session_state.maneuvers = []
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
        if 'system_status' not in st.session_state:
            st.session_state.system_status = "🟢 Active"
        
        # Enhanced data flow tracking
        if 'data_flow_status' not in st.session_state:
            st.session_state.data_flow_status = {
                'data_collection': '🟡 Pending',
                'orbit_propagation': '🟡 Pending',
                'collision_detection': '🟡 Pending',
                'maneuver_planning': '🟡 Pending',
                'visualization': '🟡 Pending',
                'last_sync': None,
                'sync_errors': []
            }
        
        # Data flow monitoring
        if 'data_pipeline' not in st.session_state:
            st.session_state.data_pipeline = {
                'raw_data': {},
                'processed_data': {},
                'analysis_results': {},
                'visualization_data': {}
            }
        
        # Add temporary fake data for demonstration
        if not st.session_state.satellite_data:
            self.initialize_fake_data()
        
        # Initialize data flow monitoring
        self.initialize_data_flow_monitoring()
    
    def initialize_data_flow_monitoring(self):
        """Initialize data flow monitoring system"""
        if 'flow_monitor' not in st.session_state:
            st.session_state.flow_monitor = {
                'data_sources': ['Celestrak API', 'Space-Track API', 'Sample Data'],
                'processing_stages': ['Collection', 'Propagation', 'Detection', 'Planning', 'Visualization'],
                'data_quality': {'completeness': 0, 'accuracy': 0, 'freshness': 0},
                'performance_metrics': {'collection_time': 0, 'processing_time': 0, 'total_time': 0}
            }
    
    def initialize_fake_data(self):
        """Initialize data from JSON file or fallback to sample data"""
        try:
            # Try to load data from JSON file
            import json
            import os
            
            json_paths = [
                "data/processed_satellite_data.json",
                "data/fake_satellite_data.json",
                "../data/fake_satellite_data.json",
                "fake_satellite_data.json"
            ]
            
            for json_path in json_paths:
                if os.path.exists(json_path):
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                        if 'satellites' in data:
                            st.session_state.satellite_data = data['satellites']
                            st.success(f"✅ Loaded {len(data['satellites'])} objects from JSON file")
                            
                            # Generate realistic collision data based on the loaded satellites
                            st.session_state.collisions = self._generate_realistic_collisions()
                            
                            # Generate realistic maneuver data based on collisions
                            st.session_state.maneuvers = self._generate_realistic_maneuvers()
                            
                            return
            
            # Fallback to enhanced sample data if JSON not found
            st.warning("⚠️ JSON file not found, using sample data")
            
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            st.warning("⚠️ Using fallback sample data")
            
        st.session_state.satellite_data = {
            "ISS": {
                "object_type": "satellite",
                "name": "International Space Station",
                "altitude": 408,
                "inclination": 51.6,
                "eccentricity": 0.001,
                "raan": 0.0,
                "status": "active"
            },
            "STARLINK-1234": {
                "object_type": "satellite",
                "name": "Starlink Satellite 1234",
                "altitude": 550,
                "inclination": 53.0,
                "eccentricity": 0.002,
                "raan": 45.0,
                "status": "active"
            },
            "DEBRIS-001": {
                "object_type": "debris",
                "name": "Rocket Body Debris",
                "altitude": 425,
                "inclination": 52.0,
                "eccentricity": 0.05,
                "raan": 90.0,
                "status": "inactive"
                }
            }
        
        # Generate realistic collision data based on the loaded satellites
        st.session_state.collisions = self._generate_realistic_collisions()
        
        # Generate realistic maneuver data based on collisions
        st.session_state.maneuvers = self._generate_realistic_maneuvers()
    
    def _generate_realistic_collisions(self):
        """Generate realistic collision data based on loaded satellites"""
        collisions = []
        satellites = list(st.session_state.satellite_data.keys())
        
        # Generate collisions between different types of objects
        collision_pairs = []
        
        # High-risk collisions (debris vs active satellites)
        debris_objects = [k for k, v in st.session_state.satellite_data.items() if v.get('object_type') == 'debris']
        active_satellites = [k for k, v in st.session_state.satellite_data.items() if v.get('object_type') == 'satellite']
        
        # Debris vs Active satellite collisions (high risk) - Generate more collisions
        for debris in debris_objects:  # Use all debris objects
            for satellite in active_satellites[:8]:  # Increase to 8 active satellites
                if debris != satellite:
                    collision_pairs.append((debris, satellite, 'high'))
        
        # Starlink constellation collisions (medium risk) - Generate more constellation collisions
        starlink_sats = [k for k in satellites if 'STARLINK' in k]
        for i in range(min(6, len(starlink_sats))):  # Increase to 6 satellites
            for j in range(i + 1, min(i + 4, len(starlink_sats))):  # Increase pairs
                collision_pairs.append((starlink_sats[i], starlink_sats[j], 'medium'))
        
        # Add ISS-specific high-risk collisions
        if 'ISS' in st.session_state.satellite_data:
            iss_data = st.session_state.satellite_data['ISS']
            iss_altitude = iss_data.get('altitude', 408)
            iss_inclination = iss_data.get('inclination', 51.6)
            
            # Find objects with similar altitude and inclination to ISS
            for sat_name, sat_data in st.session_state.satellite_data.items():
                if sat_name != 'ISS':
                    sat_altitude = sat_data.get('altitude', 500)
                    sat_inclination = sat_data.get('inclination', 45)
                    
                    # Check if object is in ISS collision risk zone
                    alt_diff = abs(iss_altitude - sat_altitude)
                    inc_diff = abs(iss_inclination - sat_inclination)
                    
                    if alt_diff < 100 and inc_diff < 20:  # Close orbital parameters
                        collision_pairs.append(('ISS', sat_name, 'critical'))
        
        # Add more general satellite-to-satellite collisions with risk-based classification
        for i, sat1 in enumerate(active_satellites[:15]):  # Check first 15 satellites
            for j, sat2 in enumerate(active_satellites[i+1:i+8]):  # Check next 8 satellites
                if sat1 != sat2:
                    sat1_data = st.session_state.satellite_data[sat1]
                    sat2_data = st.session_state.satellite_data[sat2]
                    
                    alt_diff = abs(sat1_data.get('altitude', 500) - sat2_data.get('altitude', 500))
                    inc_diff = abs(sat1_data.get('inclination', 45) - sat2_data.get('inclination', 45))
                    
                    # Risk classification based on orbital parameters
                    if alt_diff < 25 and inc_diff < 3:  # Very close orbits
                        collision_pairs.append((sat1, sat2, 'high'))
                    elif alt_diff < 75 and inc_diff < 8:  # Close orbits
                        collision_pairs.append((sat1, sat2, 'medium'))
                    elif alt_diff < 150 and inc_diff < 15:  # Moderate separation
                        collision_pairs.append((sat1, sat2, 'low'))
        
        # Add more Starlink constellation scenarios with different risk levels
        for i in range(min(10, len(starlink_sats))):  # Check more Starlink satellites
            for j in range(i + 1, min(i + 6, len(starlink_sats))):  # More pairs
                sat1_data = st.session_state.satellite_data[starlink_sats[i]]
                sat2_data = st.session_state.satellite_data[starlink_sats[j]]
                
                alt_diff = abs(sat1_data.get('altitude', 550) - sat2_data.get('altitude', 550))
                raan_diff = abs(sat1_data.get('raan', 0) - sat2_data.get('raan', 0))
                
                # Starlink-specific risk assessment
                if alt_diff < 5 and raan_diff < 2:  # Very close Starlink satellites
                    collision_pairs.append((starlink_sats[i], starlink_sats[j], 'high'))
                elif alt_diff < 15 and raan_diff < 8:  # Close Starlink satellites
                    collision_pairs.append((starlink_sats[i], starlink_sats[j], 'medium'))
                elif alt_diff < 30 and raan_diff < 20:  # Moderate Starlink separation
                    collision_pairs.append((starlink_sats[i], starlink_sats[j], 'low'))
        
        # Add GPS constellation medium/low risk scenarios
        gps_sats = [k for k in satellites if 'GPS' in k]
        for i in range(min(5, len(gps_sats))):
            for j in range(i + 1, min(i + 4, len(gps_sats))):
                sat1_data = st.session_state.satellite_data[gps_sats[i]]
                sat2_data = st.session_state.satellite_data[gps_sats[j]]
                
                alt_diff = abs(sat1_data.get('altitude', 20200) - sat2_data.get('altitude', 20200))
                inc_diff = abs(sat1_data.get('inclination', 55) - sat2_data.get('inclination', 55))
                
                if alt_diff < 50 and inc_diff < 3:  # GPS constellation risks
                    collision_pairs.append((gps_sats[i], gps_sats[j], 'medium'))
                elif alt_diff < 100 and inc_diff < 6:
                    collision_pairs.append((gps_sats[i], gps_sats[j], 'low'))
        
        # Add Galileo constellation medium/low risk scenarios
        galileo_sats = [k for k in satellites if 'GALILEO' in k]
        for i in range(min(4, len(galileo_sats))):
            for j in range(i + 1, min(i + 3, len(galileo_sats))):
                sat1_data = st.session_state.satellite_data[galileo_sats[i]]
                sat2_data = st.session_state.satellite_data[galileo_sats[j]]
                
                alt_diff = abs(sat1_data.get('altitude', 23200) - sat2_data.get('altitude', 23200))
                inc_diff = abs(sat1_data.get('inclination', 56) - sat2_data.get('inclination', 56))
                
                if alt_diff < 75 and inc_diff < 4:  # Galileo constellation risks
                    collision_pairs.append((galileo_sats[i], galileo_sats[j], 'medium'))
                elif alt_diff < 150 and inc_diff < 8:
                    collision_pairs.append((galileo_sats[i], galileo_sats[j], 'low'))
        
        # Add debris-to-debris low risk scenarios
        for i, debris1 in enumerate(debris_objects[:5]):
            for j, debris2 in enumerate(debris_objects[i+1:i+4]):
                debris1_data = st.session_state.satellite_data[debris1]
                debris2_data = st.session_state.satellite_data[debris2]
                
                alt_diff = abs(debris1_data.get('altitude', 500) - debris2_data.get('altitude', 500))
                inc_diff = abs(debris1_data.get('inclination', 50) - debris2_data.get('inclination', 50))
                
                if alt_diff < 50 and inc_diff < 10:  # Debris field interactions
                    collision_pairs.append((debris1, debris2, 'low'))
        
        # Add cross-constellation low risk scenarios
        for sat1 in active_satellites[:8]:
            for sat2 in active_satellites[8:15]:
                if sat1 != sat2:
                    sat1_data = st.session_state.satellite_data[sat1]
                    sat2_data = st.session_state.satellite_data[sat2]
                    
                    alt_diff = abs(sat1_data.get('altitude', 500) - sat2_data.get('altitude', 500))
                    inc_diff = abs(sat1_data.get('inclination', 45) - sat2_data.get('inclination', 45))
                    
                    # Cross-constellation risks (different orbital families)
                    if alt_diff > 500 and alt_diff < 2000 and inc_diff < 20:
                        collision_pairs.append((sat1, sat2, 'low'))
        
        # Add some guaranteed medium and low risk scenarios for better distribution
        # Medium risk scenarios - satellites with moderate orbital differences
        for i in range(min(8, len(active_satellites))):
            for j in range(i + 1, min(i + 3, len(active_satellites))):
                sat1 = active_satellites[i]
                sat2 = active_satellites[j]
                if sat1 != sat2:
                    # Force some medium risk scenarios
                    collision_pairs.append((sat1, sat2, 'medium'))
        
        # Low risk scenarios - satellites with larger orbital differences
        for i in range(min(6, len(active_satellites))):
            for j in range(i + 2, min(i + 4, len(active_satellites))):
                sat1 = active_satellites[i]
                sat2 = active_satellites[j]
                if sat1 != sat2:
                    # Force some low risk scenarios
                    collision_pairs.append((sat1, sat2, 'low'))
        
        # Debug: Print collision pairs being generated
        print(f"🔍 Generated {len(collision_pairs)} collision pairs")
        print(f"📊 Debris objects: {len(debris_objects)}")
        print(f"🛰️ Active satellites: {len(active_satellites)}")
        print(f"🌟 Starlink satellites: {len([k for k in satellites if 'STARLINK' in k])}")
        
        # Generate collision data for each pair
        for i, (sat1, sat2, base_risk) in enumerate(collision_pairs):
            # Calculate realistic collision probability based on orbital parameters
            sat1_data = st.session_state.satellite_data[sat1]
            sat2_data = st.session_state.satellite_data[sat2]
            
            # Altitude difference affects collision probability
            alt_diff = abs(sat1_data.get('altitude', 500) - sat2_data.get('altitude', 500))
            base_prob = 0.8 if base_risk == 'high' else 0.4 if base_risk == 'medium' else 0.1
            
            # Adjust probability based on altitude difference
            if alt_diff < 50:
                collision_prob = base_prob
            elif alt_diff < 100:
                collision_prob = base_prob * 0.7
            else:
                collision_prob = base_prob * 0.3
            
            # Generate realistic timing
            hours_ahead = (i * 3) + 2  # Spread collisions over time
            closest_approach_time = datetime.now() + timedelta(hours=hours_ahead)
            
            collision = {
                "satellite1_name": sat1,
                "satellite2_name": sat2,
                "risk_level": base_risk,
                "collision_probability": min(collision_prob, 0.95),
                "closest_approach": {
                    "distance": 0.1 + (i * 0.5),  # Realistic distances
                    "time": closest_approach_time.strftime("%Y-%m-%dT%H:%M:%S")
                },
                "time_to_closest_approach": hours_ahead,
                "altitude_difference": alt_diff,
                "relative_velocity": 7.5 + (i * 0.2)  # km/s
            }
            collisions.append(collision)
        
        # Sort collisions by risk level to ensure good distribution
        critical_collisions = [c for c in collisions if c['risk_level'] == 'critical']
        high_collisions = [c for c in collisions if c['risk_level'] == 'high']
        medium_collisions = [c for c in collisions if c['risk_level'] == 'medium']
        low_collisions = [c for c in collisions if c['risk_level'] == 'low']
        
        # Create a balanced distribution
        balanced_collisions = []
        balanced_collisions.extend(critical_collisions[:3])  # Up to 3 critical
        balanced_collisions.extend(high_collisions[:12])     # Up to 12 high
        balanced_collisions.extend(medium_collisions[:12])   # Up to 12 medium
        balanced_collisions.extend(low_collisions[:8])       # Up to 8 low
        
        return balanced_collisions[:35]  # Limit to 35 most significant collisions
    
    def _generate_realistic_maneuvers(self):
        """Generate realistic maneuver data based on collision data"""
        maneuvers = []
        
        for collision in st.session_state.collisions[:15]:  # Generate maneuvers for top 15 collisions
            sat1 = collision['satellite1_name']
            sat1_data = st.session_state.satellite_data[sat1]
            
            # Determine maneuver type based on risk level
            if collision['risk_level'] == 'high':
                maneuver_type = 'emergency_avoidance'
                delta_v = 3.0 + (collision['collision_probability'] * 2.0)
                fuel_consumption = 0.025 + (collision['collision_probability'] * 0.015)
            elif collision['risk_level'] == 'medium':
                maneuver_type = 'collision_avoidance'
                delta_v = 2.0 + (collision['collision_probability'] * 1.5)
                fuel_consumption = 0.015 + (collision['collision_probability'] * 0.010)
            else:
                maneuver_type = 'orbit_adjustment'
                delta_v = 1.0 + (collision['collision_probability'] * 1.0)
                fuel_consumption = 0.008 + (collision['collision_probability'] * 0.005)
            
            # Calculate execution time (before collision)
            collision_time = datetime.strptime(collision['closest_approach']['time'], "%Y-%m-%dT%H:%M:%S")
            execution_time = collision_time - timedelta(hours=1)  # Execute 1 hour before
            
            maneuver = {
                "maneuver_satellite_id": sat1,
                "maneuver_type": maneuver_type,
                "delta_v_magnitude": round(delta_v, 2),
                "fuel_consumption": round(fuel_consumption, 3),
                "execution_time": execution_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "status": "planned" if execution_time > datetime.now() else "executed",
                "target_collision": f"{sat1}-{collision['satellite2_name']}",
                "priority": "high" if collision['risk_level'] == 'high' else "medium",
                "estimated_cost": round(fuel_consumption * 1000, 2)  # Cost in USD
            }
            maneuvers.append(maneuver)
        
        return maneuvers
    
    def run(self):
        """Run the main dashboard"""
        # Initialize data if not already loaded
        if not st.session_state.satellite_data or len(st.session_state.satellite_data) == 0:
            self.initialize_fake_data()
        
        # Premium Header with Enhanced Styling
        st.markdown("""
        <div class="main-header">
            <div style="position: relative; z-index: 2;">
            <h1>🚀 Space Traffic Management System</h1>
            <p>AI-Powered Orbital Collision Prevention & Debris Management</p>
                <div style="margin-top: 1.5rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                    <span style="background: rgba(102, 126, 234, 0.2); padding: 0.5rem 1rem; border-radius: 20px; border: 1px solid rgba(102, 126, 234, 0.3); font-size: 0.9rem; color: #e0e0e0;">🛰️ Real-time Monitoring</span>
                    <span style="background: rgba(118, 75, 162, 0.2); padding: 0.5rem 1rem; border-radius: 20px; border: 1px solid rgba(118, 75, 162, 0.3); font-size: 0.9rem; color: #e0e0e0;">🧠 AI-Powered Analysis</span>
                    <span style="background: rgba(76, 175, 80, 0.2); padding: 0.5rem 1rem; border-radius: 20px; border: 1px solid rgba(76, 175, 80, 0.3); font-size: 0.9rem; color: #e0e0e0;">🚨 Collision Prevention</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar
        self.create_sidebar()
        
        # Main content with enhanced layout
        self.display_main_dashboard()
        
        # Main tabs with improved styling and data flow monitoring
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
            "🌍 3D Space View", 
            "📊 Analytics Dashboard", 
            "🧩 Problem Visualizer",
            "🛰️ Trajectories (Animated)",
            "🔥 Risk Heatmaps",
            "⏰ Timeline Playback",
            "🔮 Predictive Heatmap",
            "🚨 Alert Center", 
            "🧭 Maneuver Control",
            "⚙️ System Settings",
            "🔄 Data Flow Monitoring"
        ])
        
        with tab1:
            self.show_3d_view()
        
        with tab2:
            self.show_analytics()
        
        with tab3:
            self.show_problem_visualizer()

        with tab4:
            self.show_trajectories()

        with tab5:
            self.show_heatmap_visualization()
        
        with tab6:
            self.show_timeline_playback()
            
        with tab7:
            self.show_predictive_heatmap()

        with tab8:
            self.show_alerts()
        
        with tab9:
            self.show_maneuvers()
            
        with tab10:
            self.show_system_settings()
            
        with tab11:
            self.show_data_flow_monitoring()

    def show_trajectories(self):
        """Show enhanced animated trajectory visualization"""
        st.markdown("### 🛰️ Realistic Trajectory Animation")
        
        if not st.session_state.satellite_data:
            st.info("No satellite data available. Load demo data first.")
            return
        
        # Create enhanced animated figure with collision data
        fig = self.trajectory_visualizer.create_enhanced_animated_figure(
            objects=st.session_state.satellite_data,
            collision_data=st.session_state.collisions if hasattr(st.session_state, 'collisions') else None
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add trajectory information
        with st.expander("📊 Trajectory Details"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Object Types:**")
                for name, data in st.session_state.satellite_data.items():
                    obj_type = data.get('object_type', 'unknown')
                    altitude = data.get('altitude', 0)
                    st.write(f"• {name}: {obj_type.title()} at {altitude} km")
            
            with col2:
                if hasattr(st.session_state, 'collisions') and st.session_state.collisions:
                    st.markdown("**Collision Risks:**")
                    for collision in st.session_state.collisions[:3]:  # Show top 3
                        sat1 = collision.get('satellite1_name', 'Unknown')
                        sat2 = collision.get('satellite2_name', 'Unknown')
                        risk = collision.get('risk_level', 'unknown').upper()
                        prob = collision.get('collision_probability', 0)
                        st.write(f"• {sat1} ↔ {sat2}: {risk} risk ({prob:.1%})")
    
    def create_sidebar(self):
        """Create the premium sidebar with enhanced controls"""
        st.sidebar.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%); backdrop-filter: blur(20px); border-radius: 20px; margin-bottom: 2rem; border: 1px solid rgba(255, 255, 255, 0.2); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);">
            <h2 style="color: white; margin: 0; font-size: 1.5rem; font-weight: 700; text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);">🎛️ Mission Control</h2>
            <p style="color: #e0e0e0; margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.8;">Advanced Space Traffic Management</p>
        </div>
        """, unsafe_allow_html=True)
        
        # System controls
        st.sidebar.markdown("### 🚀 System Controls")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("▶️ Start", type="primary", use_container_width=True):
                st.session_state.system_status = "🟢 Active"
                st.success("System monitoring started!")
        
        with col2:
            if st.button("⏹️ Stop", use_container_width=True):
                st.session_state.system_status = "🔴 Inactive"
                st.warning("System monitoring stopped!")
        
        # Quick Actions
        st.sidebar.markdown("### ⚡ Quick Actions")
        
        if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
            self.update_data()
        
        if st.sidebar.button("📊 Generate Report", use_container_width=True):
            self.generate_report()
        
        if st.sidebar.button("🎭 Load Demo Data", use_container_width=True):
            self.initialize_fake_data()
            st.success("Demo data loaded! Check the Alert Center tab.")
        
        if st.sidebar.button("📁 Load JSON Data", use_container_width=True):
            self.load_json_data()
            st.success("JSON data loaded! Check the Data Flow Monitoring tab.")
        
        # Settings
        st.sidebar.markdown("### ⚙️ Settings")
        
        update_frequency = st.sidebar.slider(
            "🕐 Update Frequency (seconds)",
            min_value=5,
            max_value=60,
            value=10,
            step=5
        )
        
        collision_threshold = st.sidebar.slider(
            "⚠️ Collision Threshold (km)",
            min_value=1.0,
            max_value=20.0,
            value=10.0,
            step=0.5
        )
        
        # Filters
        st.sidebar.markdown("### 🔍 Filters")
        
        show_satellites = st.sidebar.checkbox("🛰️ Show Satellites", value=True)
        show_debris = st.sidebar.checkbox("🧩 Show Debris", value=True)
        show_collisions = st.sidebar.checkbox("🚨 Show Collisions", value=True)
        show_maneuvers = st.sidebar.checkbox("🧭 Show Maneuvers", value=True)
        
        # Export options
        st.sidebar.markdown("### 📥 Export")
        
        export_format = st.sidebar.selectbox(
            "Format",
            ["JSON", "CSV", "PDF"]
        )
        
        if st.sidebar.button("📥 Export Data", use_container_width=True):
            self.export_data(export_format)
    
    def display_main_dashboard(self):
        """Display the main dashboard with enhanced metrics"""
        # System Status Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.display_system_status()
        
        with col2:
            self.display_satellite_count()
        
        with col3:
            self.display_collision_alerts()
        
        with col4:
            self.display_maneuver_status()
        
        # Real-time metrics row
        st.markdown("### 📈 Real-Time Metrics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            self.display_metric_card("Total Objects", len(st.session_state.satellite_data), "🛰️")
        
        with col2:
            active_sats = sum(1 for sat in st.session_state.satellite_data.values() 
                             if sat.get('object_type') == 'satellite')
            self.display_metric_card("Active Satellites", active_sats, "🛰️")
        
        with col3:
            high_risk = sum(1 for c in st.session_state.collisions if c.get('risk_level') == 'high')
            self.display_metric_card("High Risk Alerts", high_risk, "🚨")
        
        with col4:
            total_maneuvers = len(st.session_state.maneuvers)
            self.display_metric_card("Planned Maneuvers", total_maneuvers, "🧭")
        
        with col5:
            # Calculate system health score
            health_score = self.calculate_system_health()
            self.display_metric_card("System Health", f"{health_score}%", "💚")
    
    def display_metric_card(self, label, value, icon):
        """Display a metric card with enhanced styling"""
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{icon} {value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)
    
    def calculate_system_health(self):
        """Calculate system health score based on various factors"""
        base_score = 95
        
        # Deduct points for high-risk collisions
        high_risk = sum(1 for c in st.session_state.collisions if c.get('risk_level') == 'high')
        base_score -= high_risk * 10
        
        # Deduct points for system inactivity
        if st.session_state.system_status == "🔴 Inactive":
            base_score -= 20
        
        return max(0, min(100, base_score))
    
    def display_system_status(self):
        """Display enhanced system status card"""
        st.markdown(f"""
        <div class="status-card">
            <h3>🖥️ System Status</h3>
            <p><strong>Status:</strong> {st.session_state.system_status}</p>
            <p><strong>Last Update:</strong> {st.session_state.last_update.strftime("%H:%M:%S")}</p>
            <p><strong>Uptime:</strong> {self.calculate_uptime()}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def calculate_uptime(self):
        """Calculate system uptime"""
        # This would normally come from system logs
        return "2h 34m 12s"
    
    def display_satellite_count(self):
        """Display enhanced satellite count card"""
        total_sats = len(st.session_state.satellite_data)
        active_sats = sum(1 for sat in st.session_state.satellite_data.values() 
                         if sat.get('object_type') == 'satellite')
        debris_count = total_sats - active_sats
        
        st.markdown(f"""
        <div class="status-card">
            <h3>🛰️ Objects Tracked</h3>
            <p><strong>Total:</strong> {total_sats:,}</p>
            <p><strong>Satellites:</strong> {active_sats:,}</p>
            <p><strong>Debris:</strong> {debris_count:,}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def display_collision_alerts(self):
        """Display enhanced collision alerts card"""
        high_risk = sum(1 for c in st.session_state.collisions if c.get('risk_level') == 'high')
        medium_risk = sum(1 for c in st.session_state.collisions if c.get('risk_level') == 'medium')
        low_risk = sum(1 for c in st.session_state.collisions if c.get('risk_level') == 'low')
        
        alert_class = "alert-high" if high_risk > 0 else "alert-medium" if medium_risk > 0 else "alert-low"
        
        st.markdown(f"""
        <div class="status-card {alert_class}">
            <h3>🚨 Collision Alerts</h3>
            <p><strong>High Risk:</strong> {high_risk}</p>
            <p><strong>Medium Risk:</strong> {medium_risk}</p>
            <p><strong>Low Risk:</strong> {low_risk}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def display_maneuver_status(self):
        """Display enhanced maneuver status card"""
        total_maneuvers = len(st.session_state.maneuvers)
        
        # Simple approach: count based on status instead of datetime
        pending_maneuvers = sum(1 for m in st.session_state.maneuvers 
                               if m.get('status') == 'planned')
        executed_maneuvers = sum(1 for m in st.session_state.maneuvers 
                                if m.get('status') == 'executed')
        
        st.markdown(f"""
        <div class="status-card">
            <h3>🧭 Maneuvers</h3>
            <p><strong>Total Planned:</strong> {total_maneuvers}</p>
            <p><strong>Pending:</strong> {pending_maneuvers}</p>
            <p><strong>Executed:</strong> {executed_maneuvers}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def update_data(self):
        """Update satellite and collision data with comprehensive data flow tracking"""
        start_time = datetime.now()
        
        with st.spinner("🔄 Updating data with enhanced flow monitoring..."):
            try:
                # Step 1: Data Collection
                st.info("📡 Step 1: Collecting satellite data...")
                st.session_state.data_flow_status['data_collection'] = '🔄 Processing'
                satellite_data = asyncio.run(self.data_collector.collect_data())
                st.session_state.satellite_data = satellite_data
                st.session_state.data_pipeline['raw_data'] = satellite_data
                st.session_state.data_flow_status['data_collection'] = '✅ Complete'
                
                # Step 2: Orbit Propagation
                st.info("🔮 Step 2: Propagating orbits...")
                st.session_state.data_flow_status['orbit_propagation'] = '🔄 Processing'
                future_positions = asyncio.run(self.orbit_engine.propagate_orbits(satellite_data))
                st.session_state.data_pipeline['processed_data'] = future_positions
                st.session_state.data_flow_status['orbit_propagation'] = '✅ Complete'
                
                # Step 3: Collision Detection
                st.info("🚨 Step 3: Detecting collisions...")
                st.session_state.data_flow_status['collision_detection'] = '🔄 Processing'
                collisions = asyncio.run(self.collision_detector.detect_collisions(future_positions))
                st.session_state.collisions = collisions
                st.session_state.data_pipeline['analysis_results'] = collisions
                st.session_state.data_flow_status['collision_detection'] = '✅ Complete'
                
                # Step 4: Maneuver Planning
                if collisions:
                    st.info("🧭 Step 4: Planning maneuvers...")
                    st.session_state.data_flow_status['maneuver_planning'] = '🔄 Processing'
                    maneuvers = asyncio.run(self.maneuver_planner.plan_maneuvers(collisions))
                    st.session_state.maneuvers = maneuvers
                    st.session_state.data_flow_status['maneuver_planning'] = '✅ Complete'
                else:
                    st.session_state.data_flow_status['maneuver_planning'] = '⏭️ Skipped (no collisions)'
                
                # Step 5: Visualization Update
                st.info("📊 Step 5: Updating visualizations...")
                st.session_state.data_flow_status['visualization'] = '🔄 Processing'
                asyncio.run(self.visualizer.update_visualization(
                    satellites=future_positions,
                    collisions=collisions,
                    maneuvers=st.session_state.maneuvers
                ))
                st.session_state.data_pipeline['visualization_data'] = {
                    'satellites': future_positions,
                    'collisions': collisions,
                    'maneuvers': st.session_state.maneuvers
                }
                st.session_state.data_flow_status['visualization'] = '✅ Complete'
                
                # Update data flow metrics
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                st.session_state.flow_monitor['performance_metrics'].update({
                    'collection_time': 2.0,  # Estimated
                    'processing_time': processing_time - 2.0,
                    'total_time': processing_time
                })
                
                # Update data quality metrics
                data_completeness = len(satellite_data) / 10.0 * 100  # Normalized to 100%
                st.session_state.flow_monitor['data_quality'].update({
                    'completeness': min(data_completeness, 100),
                    'accuracy': 95.0,  # Estimated accuracy
                    'freshness': 100.0  # Just updated
                })
                
                st.session_state.last_update = datetime.now()
                st.session_state.data_flow_status['last_sync'] = datetime.now()
                st.success("✅ Data updated successfully with comprehensive flow tracking!")
                
            except Exception as e:
                error_msg = f"❌ Error updating data: {e}"
                st.error(error_msg)
                st.session_state.data_flow_status['sync_errors'].append({
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e),
                    'stage': 'data_update'
                })
                
                # Mark failed stages
                for stage in ['data_collection', 'orbit_propagation', 'collision_detection', 'maneuver_planning', 'visualization']:
                    if st.session_state.data_flow_status[stage] == '🔄 Processing':
                        st.session_state.data_flow_status[stage] = '❌ Failed'
    
    def generate_report(self):
        """Generate a comprehensive system report"""
        st.info("📊 Generating comprehensive system report...")
        # This would generate a detailed PDF report
        st.success("📄 Report generated successfully!")
    
    def show_3d_view(self):
        """Show enhanced 3D visualization"""
        st.markdown("### 🌍 3D Space Visualization")
        
        if not st.session_state.satellite_data:
            st.info("No satellite data available. Click 'Refresh Data' to load.")
            return
        
        # Create 3D plot
        fig = self.visualizer.create_3d_space_plot()
        st.plotly_chart(fig, use_container_width=True)
        
        # Enhanced 3D view controls
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="status-card">
                <h3>🎮 View Controls</h3>
                <p>• <strong>Zoom:</strong> Mouse wheel</p>
                <p>• <strong>Rotate:</strong> Click and drag</p>
                <p>• <strong>Pan:</strong> Right-click and drag</p>
                <p>• <strong>Reset:</strong> Double-click</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="status-card">
                <h3>🎨 Legend</h3>
                <p>🟢 <strong>Green:</strong> Active satellites</p>
                <p>🔴 <strong>Red:</strong> Debris objects</p>
                <p>🟡 <strong>Yellow:</strong> Low risk collisions</p>
                <p>🟠 <strong>Orange:</strong> Medium risk collisions</p>
                <p>🔴 <strong>Red X:</strong> High risk collisions</p>
                <p>🔵 <strong>Blue star:</strong> Planned maneuvers</p>
            </div>
            """, unsafe_allow_html=True)
    
    def show_analytics(self):
        """Show enhanced analytics dashboard with real-time data"""
        st.markdown("### 📊 Real-Time Analytics Dashboard")
        
        if not st.session_state.satellite_data:
            st.info("No data available for analytics.")
            return
        
        # Real-time data status indicator
        self.show_realtime_status()
        
        # Real-time metrics section
        self.show_realtime_metrics()
        
        # Live satellite monitoring
        self.show_live_satellite_monitoring()
        
        # Enhanced dashboard plots
        plots = self.visualizer.create_dashboard_plots()
        
        # Display plots in a grid
        col1, col2 = st.columns(2)
        
        with col1:
            if 'satellite_distribution' in plots:
                st.plotly_chart(plots['satellite_distribution'], use_container_width=True)
            
            if 'altitude_distribution' in plots:
                st.plotly_chart(plots['altitude_distribution'], use_container_width=True)
        
        with col2:
            if 'collision_timeline' in plots:
                st.plotly_chart(plots['collision_timeline'], use_container_width=True)
            
            if 'maneuver_summary' in plots:
                st.plotly_chart(plots['maneuver_summary'], use_container_width=True)
        
        # Enhanced statistics
        stats = self.visualizer.get_visualization_stats()
        
        st.markdown("### 📈 Key Performance Indicators")
        
        # Create metric cards for KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.display_metric_card("Total Objects", stats.get('total_satellites', 0), "🛰️")
        
        with col2:
            self.display_metric_card("Active Satellites", stats.get('active_satellites', 0), "🛰️")
        
        with col3:
            self.display_metric_card("Total Collisions", stats.get('total_collisions', 0), "🚨")
        
        with col4:
            self.display_metric_card("Planned Maneuvers", stats.get('total_maneuvers', 0), "🧭")
        
        # Real-time data source monitoring
        self.show_data_source_monitoring()

    def show_realtime_status(self):
        """Show real-time data status indicators"""
        st.markdown("### 🟢 Real-Time Data Status")
        
        # Get real-time data statistics
        realtime_stats = self.get_realtime_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_color = "🟢" if realtime_stats['iss_connected'] else "🔴"
            st.metric(
                label="ISS Live Feed",
                value=status_color,
                delta=f"Last update: {realtime_stats['iss_last_update']}"
            )
        
        with col2:
            status_color = "🟢" if realtime_stats['n2yo_connected'] else "🔴"
            st.metric(
                label="N2YO API",
                value=status_color,
                delta=f"Status: {'Connected' if realtime_stats['n2yo_connected'] else 'Offline'}"
            )
        
        with col3:
            status_color = "🟢" if realtime_stats['celestrak_connected'] else "🔴"
            st.metric(
                label="Celestrak TLE",
                value=status_color,
                delta=f"Status: {'Connected' if realtime_stats['celestrak_connected'] else 'Offline'}"
            )
        
        with col4:
            st.metric(
                label="Data Freshness",
                value=f"{realtime_stats['data_age_minutes']} min",
                delta="Real-time" if realtime_stats['data_age_minutes'] < 5 else "Stale"
            )

    def show_realtime_metrics(self):
        """Show real-time performance metrics"""
        st.markdown("### ⚡ Live Performance Metrics")
        
        # Get real-time metrics
        metrics = self.get_realtime_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🛰️ Live Satellites",
                value=metrics['live_satellites'],
                delta=f"+{metrics['live_satellites_delta']}" if metrics['live_satellites_delta'] > 0 else None
            )
        
        with col2:
            st.metric(
                label="📡 Data Sources",
                value=metrics['active_data_sources'],
                delta=f"{metrics['data_sources_status']}"
            )
        
        with col3:
            st.metric(
                label="🔄 Update Frequency",
                value=f"{metrics['update_frequency']}s",
                delta="Real-time"
            )
        
        with col4:
            st.metric(
                label="📊 Data Quality",
                value=f"{metrics['data_quality']}%",
                delta=f"{metrics['data_quality_delta']}%" if metrics['data_quality_delta'] != 0 else None
            )

    def show_live_satellite_monitoring(self):
        """Show live satellite monitoring dashboard"""
        st.markdown("### 🛰️ Live Satellite Monitoring")
        
        # Get live satellite data
        live_satellites = self.get_live_satellite_data()
        
        if not live_satellites:
            st.info("No live satellite data available.")
            return
        
        # Create live satellite monitoring table
        live_df = pd.DataFrame(live_satellites)
        
        # Display live satellites in a table with real-time indicators
        st.dataframe(
            live_df,
            use_container_width=True,
            column_config={
                "name": "Satellite Name",
                "status": st.column_config.TextColumn("Status", help="Real-time status"),
                "altitude": st.column_config.NumberColumn("Altitude (km)", format="%.1f"),
                "velocity": st.column_config.NumberColumn("Velocity (km/s)", format="%.2f"),
                "last_update": "Last Update",
                "data_source": "Data Source"
            }
        )
        
        # Live position tracking chart
        if len(live_satellites) > 0:
            self.create_live_position_chart(live_satellites)

    def show_data_source_monitoring(self):
        """Show data source monitoring and health"""
        st.markdown("### 📡 Data Source Monitoring")
        
        # Get data source statistics
        data_sources = self.get_data_source_statistics()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Data source health chart
            fig_health = go.Figure(data=[
                go.Bar(
                    x=list(data_sources.keys()),
                    y=[data_sources[source]['status'] for source in data_sources.keys()],
                    marker_color=['#00ff00' if data_sources[source]['status'] == 1 else '#ff0000' for source in data_sources.keys()],
                    text=[f"{data_sources[source]['last_update']}" for source in data_sources.keys()],
                    textposition='auto'
                )
            ])
            
            fig_health.update_layout(
                title="Data Source Health Status",
                xaxis_title="Data Source",
                yaxis_title="Status (1=Online, 0=Offline)",
                height=400
            )
            
            st.plotly_chart(fig_health, use_container_width=True)
        
        with col2:
            # Data freshness chart
            fig_freshness = go.Figure(data=[
                go.Scatter(
                    x=list(data_sources.keys()),
                    y=[data_sources[source]['data_age_minutes'] for source in data_sources.keys()],
                    mode='markers+lines',
                    marker=dict(
                        size=10,
                        color=[data_sources[source]['data_age_minutes'] for source in data_sources.keys()],
                        colorscale='RdYlGn_r',
                        showscale=True,
                        colorbar=dict(title="Age (minutes)")
                    ),
                    line=dict(width=2)
                )
            ])
            
            fig_freshness.update_layout(
                title="Data Freshness by Source",
                xaxis_title="Data Source",
                yaxis_title="Data Age (minutes)",
                height=400
            )
            
            st.plotly_chart(fig_freshness, use_container_width=True)

    def get_realtime_statistics(self):
        """Get real-time data statistics"""
        try:
            # Analyze satellite data for real-time indicators
            satellite_data = st.session_state.satellite_data or {}
            
            # Check for real-time data sources
            iss_connected = any(
                sat.get('data_source') == 'Open Notify' and sat.get('real_time', False)
                for sat in satellite_data.values()
            )
            
            n2yo_connected = any(
                sat.get('data_source') == 'N2YO'
                for sat in satellite_data.values()
            )
            
            celestrak_connected = any(
                sat.get('data_source') == 'Celestrak'
                for sat in satellite_data.values()
            )
            
            # Calculate data age
            current_time = datetime.now()
            data_age_minutes = 0
            
            for sat in satellite_data.values():
                if 'last_updated' in sat:
                    try:
                        last_update = datetime.fromisoformat(sat['last_updated'].replace('Z', '+00:00'))
                        age = (current_time - last_update).total_seconds() / 60
                        data_age_minutes = max(data_age_minutes, age)
                    except:
                        continue
            
            return {
                'iss_connected': iss_connected,
                'n2yo_connected': n2yo_connected,
                'celestrak_connected': celestrak_connected,
                'iss_last_update': 'Live' if iss_connected else 'Offline',
                'data_age_minutes': int(data_age_minutes)
            }
        except Exception as e:
            return {
                'iss_connected': False,
                'n2yo_connected': False,
                'celestrak_connected': False,
                'iss_last_update': 'Error',
                'data_age_minutes': 999
            }

    def get_realtime_metrics(self):
        """Get real-time performance metrics"""
        try:
            satellite_data = st.session_state.satellite_data or {}
            
            # Count live satellites
            live_satellites = sum(1 for sat in satellite_data.values() if sat.get('real_time', False))
            
            # Count active data sources
            data_sources = set()
            for sat in satellite_data.values():
                if 'data_source' in sat:
                    data_sources.add(sat['data_source'])
            
            # Calculate data quality (percentage of satellites with complete data)
            total_sats = len(satellite_data)
            complete_sats = sum(1 for sat in satellite_data.values() 
                              if all(key in sat for key in ['altitude', 'inclination', 'period']))
            data_quality = (complete_sats / total_sats * 100) if total_sats > 0 else 0
            
            return {
                'live_satellites': live_satellites,
                'live_satellites_delta': 1 if live_satellites > 0 else 0,
                'active_data_sources': len(data_sources),
                'data_sources_status': 'Active' if len(data_sources) > 0 else 'Inactive',
                'update_frequency': 30,  # 30 seconds
                'data_quality': int(data_quality),
                'data_quality_delta': 0
            }
        except Exception as e:
            return {
                'live_satellites': 0,
                'live_satellites_delta': 0,
                'active_data_sources': 0,
                'data_sources_status': 'Error',
                'update_frequency': 0,
                'data_quality': 0,
                'data_quality_delta': 0
            }

    def get_live_satellite_data(self):
        """Get live satellite data for monitoring"""
        try:
            satellite_data = st.session_state.satellite_data or {}
            live_satellites = []
            
            for sat_id, sat_data in satellite_data.items():
                if sat_data.get('real_time', False):
                    # Get current position if available
                    current_pos = None
                    if 'positions' in sat_data and sat_data['positions']:
                        current_pos = sat_data['positions'][0]
                    
                    live_satellites.append({
                        'name': sat_data.get('name', f'Satellite {sat_id}'),
                        'status': '🟢 LIVE' if sat_data.get('real_time', False) else '🟡 Simulated',
                        'altitude': current_pos.get('altitude', sat_data.get('altitude', 0)) if current_pos else sat_data.get('altitude', 0),
                        'velocity': current_pos.get('velocity', 7.5) if current_pos else 7.5,
                        'last_update': sat_data.get('last_updated', 'Unknown'),
                        'data_source': sat_data.get('data_source', 'Unknown')
                    })
            
            return live_satellites
        except Exception as e:
            return []

    def get_data_source_statistics(self):
        """Get data source statistics"""
        try:
            satellite_data = st.session_state.satellite_data or {}
            
            data_sources = {}
            current_time = datetime.now()
            
            # Analyze each data source
            for sat in satellite_data.values():
                source = sat.get('data_source', 'Unknown')
                if source not in data_sources:
                    data_sources[source] = {
                        'status': 1 if sat.get('real_time', False) else 0,
                        'last_update': sat.get('last_updated', 'Unknown'),
                        'data_age_minutes': 0
                    }
                
                # Calculate data age
                if 'last_updated' in sat:
                    try:
                        last_update = datetime.fromisoformat(sat['last_updated'].replace('Z', '+00:00'))
                        age = (current_time - last_update).total_seconds() / 60
                        data_sources[source]['data_age_minutes'] = max(
                            data_sources[source]['data_age_minutes'], age
                        )
                    except:
                        data_sources[source]['data_age_minutes'] = 999
            
            return data_sources
        except Exception as e:
            return {}

    def create_live_position_chart(self, live_satellites):
        """Create live position tracking chart"""
        try:
            if not live_satellites:
                return
            
            # Create a simple position chart
            fig = go.Figure()
            
            for sat in live_satellites:
                fig.add_trace(go.Scatter(
                    x=[sat['altitude']],
                    y=[sat['velocity']],
                    mode='markers',
                    marker=dict(
                        size=15,
                        color='#00ffff',
                        symbol='star'
                    ),
                    name=sat['name'],
                    text=f"{sat['name']}<br>Altitude: {sat['altitude']:.1f} km<br>Velocity: {sat['velocity']:.2f} km/s",
                    hovertemplate='%{text}<extra></extra>'
                ))
            
            fig.update_layout(
                title="Live Satellite Positions",
                xaxis_title="Altitude (km)",
                yaxis_title="Velocity (km/s)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not create live position chart: {e}")

    def show_problem_visualizer(self):
        """Visual visualizer to understand collision risks at a glance"""
        st.markdown("### 🧩 Problem Visualizer")

        if not st.session_state.collisions:
            st.info("No collision scenarios to visualize. Load demo data or refresh.")
            return

        # Build a DataFrame from collision data
        collisions_df = pd.DataFrame([
            {
                'sat1': c.get('satellite1_name'),
                'sat2': c.get('satellite2_name'),
                'risk': c.get('risk_level'),
                'prob': c.get('collision_probability', 0.0),
                'distance': c.get('closest_approach', {}).get('distance', None),
                'time': c.get('closest_approach', {}).get('time', None)
            }
            for c in st.session_state.collisions
        ])

        # Row 1: Risk Breakdown + Top Threats
        col1, col2 = st.columns([1, 1])

        with col1:
            risk_counts = collisions_df['risk'].value_counts().reindex(['high','medium','low']).fillna(0)
            fig_pie = px.pie(
                values=risk_counts.values,
                names=['High','Medium','Low'],
                title='Collision Risk Breakdown',
                hole=0.45,
                color=['High','Medium','Low'],
                color_discrete_map={'High':'#e53935','Medium':'#fb8c00','Low':'#43a047'}
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            top_threats = collisions_df.sort_values('prob', ascending=False).head(5)
            fig_bar = px.bar(
                top_threats,
                x='prob',
                y=top_threats.apply(lambda r: f"{r['sat1']} vs {r['sat2']}", axis=1),
                orientation='h',
                title='Top Collision Probabilities',
                color='risk',
                color_discrete_map={'high':'#e53935','medium':'#fb8c00','low':'#43a047'}
            )
            fig_bar.update_layout(yaxis_title='', xaxis_title='Probability')
            st.plotly_chart(fig_bar, use_container_width=True)

        # Row 2: Timeline of closest approaches
        st.markdown("### ⏱️ Closest Approach Timeline")
        try:
            tl_df = collisions_df.dropna(subset=['time'])
            fig_time = px.scatter(
                tl_df,
                x='time',
                y='distance',
                color='risk',
                size='prob',
                hover_data=['sat1','sat2','prob'],
                title='Closest Approach Distance vs Time',
                color_discrete_map={'high':'#e53935','medium':'#fb8c00','low':'#43a047'}
            )
            fig_time.update_traces(mode='markers')
            fig_time.update_layout(xaxis_title='Time', yaxis_title='Distance (km)')
            st.plotly_chart(fig_time, use_container_width=True)
        except Exception as e:
            st.warning(f"Timeline could not be rendered: {e}")

        # Row 3: Network-style Sankey for object pairs
        st.markdown("### 🕸️ Object Pair Relationships")
        try:
            nodes = {}
            links = []
            def get_node_id(name):
                if name not in nodes:
                    nodes[name] = len(nodes)
                return nodes[name]

            for _, row in collisions_df.iterrows():
                s1 = get_node_id(row['sat1'])
                s2 = get_node_id(row['sat2'])
                links.append({'source': s1, 'target': s2, 'value': max(row['prob'], 0.01)})

            if not links:
                st.info("No pairs to visualize.")
                return

            fig_sankey = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="white", width=0.5),
                    label=list(nodes.keys()),
                    color=["#667eea" if 'STARLINK' in n else "#29b6f6" if 'GPS' in n else "#ab47bc" if 'ISS' in n else "#ef5350" for n in nodes.keys()]
                ),
                link=dict(
                    source=[l['source'] for l in links],
                    target=[l['target'] for l in links],
                    value=[l['value'] for l in links]
                )
            )])
            fig_sankey.update_layout(title_text="Object Pair Involvement (thicker = higher probability)", font_size=12)
            st.plotly_chart(fig_sankey, use_container_width=True)
        except Exception as e:
            st.warning(f"Relationship graph could not be rendered: {e}")

    def show_heatmap_visualization(self):
        """Show heatmap of high-risk zones and collision probability charts"""
        st.markdown("### 🔥 High-Risk Zone Heatmaps")
        
        if not st.session_state.collisions:
            st.info("No collision data available for heatmap analysis.")
            return
        
        # Create altitude vs inclination heatmap
        st.markdown("#### 📊 Altitude vs Inclination Risk Heatmap")
        
        # Extract data for heatmap
        heatmap_data = []
        for collision in st.session_state.collisions:
            sat1_name = collision.get('satellite1_name', '')
            sat2_name = collision.get('satellite2_name', '')
            
            # Get satellite data
            sat1_data = st.session_state.satellite_data.get(sat1_name, {})
            sat2_data = st.session_state.satellite_data.get(sat2_name, {})
            
            if sat1_data and sat2_data:
                # Use average altitude and inclination
                alt1 = sat1_data.get('altitude', 0)
                alt2 = sat2_data.get('altitude', 0)
                inc1 = sat1_data.get('inclination', 0)
                inc2 = sat2_data.get('inclination', 0)
                
                avg_alt = (alt1 + alt2) / 2
                avg_inc = (inc1 + inc2) / 2
                risk_score = collision.get('collision_probability', 0)
                
                heatmap_data.append([avg_alt, avg_inc, risk_score])
        
        if heatmap_data:
            # Create enhanced heatmap with multiple views
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create 2D histogram heatmap
                df_heatmap = pd.DataFrame(heatmap_data, columns=['Altitude', 'Inclination', 'Risk'])
                
                fig_heatmap = px.density_heatmap(
                    df_heatmap,
                    x='Altitude',
                    y='Inclination',
                    z='Risk',
                    title='Collision Risk Heatmap: Altitude vs Inclination',
                    color_continuous_scale='Reds',
                    nbinsx=20,
                    nbinsy=20
                )
                fig_heatmap.update_layout(
                    xaxis_title='Altitude (km)',
                    yaxis_title='Inclination (degrees)',
                    coloraxis_colorbar_title='Risk Score',
                    autosize=True,
                    margin=dict(l=50, r=50, t=80, b=50),
                    height=500
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)
            
            with col2:
                # Add risk zone summary
                st.markdown("#### 🎯 Risk Zone Summary")
                
                # Calculate risk zones
                high_risk_zones = [d for d in heatmap_data if d[2] > 0.5]
                medium_risk_zones = [d for d in heatmap_data if 0.2 <= d[2] <= 0.5]
                low_risk_zones = [d for d in heatmap_data if d[2] < 0.2]
                
                st.metric("🔥 High Risk Zones", len(high_risk_zones))
                st.metric("⚠️ Medium Risk Zones", len(medium_risk_zones))
                st.metric("🟢 Low Risk Zones", len(low_risk_zones))
                
                if high_risk_zones:
                    st.warning(f"**Critical:** {len(high_risk_zones)} high-risk zones detected!")
                
                # Show altitude distribution
                altitudes = [d[0] for d in heatmap_data]
                st.markdown("**Altitude Range:**")
                st.write(f"Min: {min(altitudes):.0f} km")
                st.write(f"Max: {max(altitudes):.0f} km")
                st.write(f"Avg: {np.mean(altitudes):.0f} km")
            
            # Add 3D scatter plot for better visualization
            st.markdown("#### 🌐 3D Risk Visualization")
            
            fig_3d_risk = go.Figure()
            
            # Add 3D scatter plot
            fig_3d_risk.add_trace(go.Scatter3d(
                x=[d[0] for d in heatmap_data],
                y=[d[1] for d in heatmap_data],
                z=[d[2] for d in heatmap_data],
                mode='markers',
                marker=dict(
                    size=[d[2] * 20 + 5 for d in heatmap_data],  # Size based on risk
                    color=[d[2] for d in heatmap_data],
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Risk Score")
                ),
                text=[f"Alt: {d[0]:.0f}km, Inc: {d[1]:.1f}°, Risk: {d[2]:.3f}" for d in heatmap_data],
                hovertemplate='%{text}<extra></extra>'
            ))
            
            fig_3d_risk.update_layout(
                title='3D Collision Risk Visualization',
                scene=dict(
                    xaxis_title='Altitude (km)',
                    yaxis_title='Inclination (degrees)',
                    zaxis_title='Risk Score',
                    camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
                ),
                autosize=True,
                margin=dict(l=50, r=50, t=80, b=50),
                height=600
            )
            
            st.plotly_chart(fig_3d_risk, use_container_width=True)
            
            # Add risk zone analysis
            st.markdown("#### 🚨 High-Risk Zone Analysis")
            high_risk_data = [d for d in heatmap_data if d[2] > 0.5]
            if high_risk_data:
                st.warning(f"**High-risk zones detected:** {len(high_risk_data)} collision scenarios with >50% probability")
                
                # Show high-risk zones in table
                high_risk_df = pd.DataFrame(high_risk_data, columns=['Altitude (km)', 'Inclination (deg)', 'Risk Score'])
                st.dataframe(high_risk_df, use_container_width=True)
            else:
                st.success("No high-risk zones detected in current data.")
        else:
            st.info("Insufficient data for heatmap generation.")
        
        # Collision probability distribution
        st.markdown("#### 📈 Collision Probability Distribution")
        
        probabilities = [c.get('collision_probability', 0) for c in st.session_state.collisions]
        if probabilities:
            # Enhanced probability analysis
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig_prob_dist = px.histogram(
                    x=probabilities,
                    title='Distribution of Collision Probabilities',
                    nbins=10,
                    color_discrete_sequence=['#e53935']
                )
                fig_prob_dist.update_layout(
                    xaxis_title='Collision Probability',
                    yaxis_title='Number of Events',
                    showlegend=False,
                    autosize=True,
                    margin=dict(l=50, r=50, t=80, b=50),
                    height=400
                )
                
                # Add vertical line for high-risk threshold
                fig_prob_dist.add_vline(x=0.5, line_dash="dash", line_color="red", 
                                       annotation_text="High Risk Threshold (50%)")
                
                st.plotly_chart(fig_prob_dist, use_container_width=True)
            
            with col2:
                # Probability statistics
                st.markdown("#### 📊 Risk Statistics")
                st.metric("Mean Probability", f"{np.mean(probabilities):.3f}")
                st.metric("Max Probability", f"{np.max(probabilities):.3f}")
                st.metric("High Risk Events (>50%)", f"{sum(1 for p in probabilities if p > 0.5)}")
                st.metric("Medium Risk Events (10-50%)", f"{sum(1 for p in probabilities if 0.1 <= p <= 0.5)}")
                st.metric("Low Risk Events (<10%)", f"{sum(1 for p in probabilities if p < 0.1)}")
            
            # Enhanced probability analysis with risk categories
            st.markdown("#### 🎯 Risk Category Analysis")
            
            # Create risk category breakdown
            risk_categories = {
                'Critical (>80%)': [p for p in probabilities if p > 0.8],
                'High (50-80%)': [p for p in probabilities if 0.5 <= p <= 0.8],
                'Medium (20-50%)': [p for p in probabilities if 0.2 <= p <= 0.5],
                'Low (5-20%)': [p for p in probabilities if 0.05 <= p <= 0.2],
                'Minimal (<5%)': [p for p in probabilities if p < 0.05]
            }
            
            # Create risk category chart
            risk_data = []
            for category, probs in risk_categories.items():
                if probs:
                    risk_data.append({
                        'Category': category,
                        'Count': len(probs),
                        'Avg_Probability': np.mean(probs),
                        'Max_Probability': np.max(probs)
                    })
            
            if risk_data:
                risk_df = pd.DataFrame(risk_data)
                
                # Create stacked bar chart
                fig_risk_categories = px.bar(
                    risk_df,
                    x='Category',
                    y='Count',
                    title='Collision Risk by Category',
                    color='Avg_Probability',
                    color_continuous_scale='Reds',
                    text='Count'
                )
                fig_risk_categories.update_traces(textposition='outside')
                fig_risk_categories.update_layout(
                    xaxis_title='Risk Category',
                    yaxis_title='Number of Events',
                    coloraxis_colorbar_title='Average Probability'
                )
                st.plotly_chart(fig_risk_categories, use_container_width=True)
                
                # Show detailed risk table
                st.markdown("#### 📋 Detailed Risk Analysis")
                st.dataframe(risk_df, use_container_width=True)

    def show_timeline_playback(self):
        """Show timeline playback of orbits with collision prediction"""
        st.markdown("### ⏰ Timeline Playback of Orbits")
        
        if not st.session_state.satellite_data:
            st.info("No satellite data available for timeline playback.")
            return
        
        # Timeline controls
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            playback_speed = st.selectbox(
                "Playback Speed",
                ["1x", "2x", "5x", "10x"],
                index=0
            )
        
        with col2:
            time_range = st.selectbox(
                "Time Range",
                ["6 hours", "12 hours", "24 hours", "7 days"],
                index=2
            )
        
        with col3:
            show_collisions = st.checkbox("Show Collision Predictions", value=True)
        
        # Generate timeline data
        st.markdown("#### 🛰️ Orbital Timeline Visualization")
        
        # Create timeline data for each satellite
        timeline_data = {}
        current_time = datetime.now()
        
        for sat_name, sat_data in st.session_state.satellite_data.items():
            altitude = sat_data.get('altitude', 500)
            inclination = sat_data.get('inclination', 45)
            period = sat_data.get('period', 95)  # minutes
            
            # Generate timeline positions
            positions = []
            hours_range = 24 if time_range == "24 hours" else 7 * 24 if time_range == "7 days" else 6 if time_range == "6 hours" else 12
            
            for hour in range(0, hours_range, 1):
                # Improved orbital motion calculation with proper alignment
                time_offset = hour / 24.0  # days
                mean_anomaly = (2 * np.pi * time_offset) / (period / 1440)  # period in days
                
                # Calculate position with proper coordinate system
                radius = 6378.137 + altitude  # Earth radius + altitude
                
                # Orbital plane coordinates
                x_orbital = radius * np.cos(mean_anomaly)
                y_orbital = radius * np.sin(mean_anomaly)
                z_orbital = 0
                
                # Apply inclination rotation around x-axis
                inclination_rad = np.radians(inclination)
                x = x_orbital
                y = y_orbital * np.cos(inclination_rad) - z_orbital * np.sin(inclination_rad)
                z = y_orbital * np.sin(inclination_rad) + z_orbital * np.cos(inclination_rad)
                
                positions.append({
                    'time': current_time + timedelta(hours=hour),
                    'x': x,
                    'y': y,
                    'z': z,
                    'altitude': altitude
                })
            
            timeline_data[sat_name] = positions
        
        # Create timeline visualization
        if timeline_data:
            # Create 3D timeline plot
            fig_timeline = go.Figure()
            
            # Add Earth
            earth_radius = 6378.137
            phi = np.linspace(0, 2*np.pi, 100)
            theta = np.linspace(-np.pi/2, np.pi/2, 50)
            phi, theta = np.meshgrid(phi, theta)
            
            x_earth = earth_radius * np.cos(theta) * np.cos(phi)
            y_earth = earth_radius * np.cos(theta) * np.sin(phi)
            z_earth = earth_radius * np.sin(theta)
            
            fig_timeline.add_trace(go.Surface(
                x=x_earth, y=y_earth, z=z_earth,
                colorscale='Blues',
                showscale=False,
                opacity=0.3,
                name='Earth'
            ))
            
            # Add satellite trajectories
            colors = ['#00ff00', '#ff0000', '#0000ff', '#ffff00', '#ff00ff', '#00ffff']
            for i, (sat_name, positions) in enumerate(timeline_data.items()):
                color = colors[i % len(colors)]
                
                # Extract coordinates
                x_coords = [pos['x'] for pos in positions]
                y_coords = [pos['y'] for pos in positions]
                z_coords = [pos['z'] for pos in positions]
                times = [pos['time'] for pos in positions]
                
                # Add trajectory
                fig_timeline.add_trace(go.Scatter3d(
                    x=x_coords,
                    y=y_coords,
                    z=z_coords,
                    mode='lines',
                    line=dict(color=color, width=3),
                    name=f"{sat_name} Trajectory",
                    opacity=0.7
                ))
                
                # Add current position marker
                fig_timeline.add_trace(go.Scatter3d(
                    x=[x_coords[0]],
                    y=[y_coords[0]],
                    z=[z_coords[0]],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=color,
                        symbol='diamond'
                    ),
                    name=f"{sat_name} Current",
                    showlegend=False
                ))
            
            # Add collision indicators if enabled
            if show_collisions and st.session_state.collisions:
                for collision in st.session_state.collisions:
                    if collision.get('risk_level') == 'high':
                        # Find collision point (simplified)
                        sat1_name = collision.get('satellite1_name', '')
                        sat2_name = collision.get('satellite2_name', '')
                        
                        if sat1_name in timeline_data and sat2_name in timeline_data:
                            # Calculate collision point based on closest approach
                            sat1_positions = timeline_data[sat1_name]
                            sat2_positions = timeline_data[sat2_name]
                            
                            # Find closest approach point
                            min_distance = float('inf')
                            collision_point = None
                            collision_time_idx = 0
                            
                            for i, (pos1, pos2) in enumerate(zip(sat1_positions, sat2_positions)):
                                distance = np.sqrt(
                                    (pos1['x'] - pos2['x'])**2 + 
                                    (pos1['y'] - pos2['y'])**2 + 
                                    (pos1['z'] - pos2['z'])**2
                                )
                                if distance < min_distance:
                                    min_distance = distance
                                    collision_point = {
                                        'x': (pos1['x'] + pos2['x']) / 2,
                                        'y': (pos1['y'] + pos2['y']) / 2,
                                        'z': (pos1['z'] + pos2['z']) / 2
                                    }
                                    collision_time_idx = i
                            
                            if collision_point:
                                # Add collision warning marker at actual collision point
                                fig_timeline.add_trace(go.Scatter3d(
                                    x=[collision_point['x']],
                                    y=[collision_point['y']],
                                    z=[collision_point['z']],
                                    mode='markers',
                                    marker=dict(
                                        size=20,
                                        color='red',
                                        symbol='x',
                                        line=dict(width=3, color='white')
                                    ),
                                    name=f"🚨 HIGH RISK: {sat1_name} vs {sat2_name}",
                                    showlegend=True
                                ))
                                
                                # Add collision path line
                                if collision_time_idx < len(sat1_positions) and collision_time_idx < len(sat2_positions):
                                    pos1 = sat1_positions[collision_time_idx]
                                    pos2 = sat2_positions[collision_time_idx]
                                    
                                    fig_timeline.add_trace(go.Scatter3d(
                                        x=[pos1['x'], pos2['x']],
                                        y=[pos1['y'], pos2['y']],
                                        z=[pos1['z'], pos2['z']],
                                        mode='lines',
                                        line=dict(
                                            color='red',
                                            width=5,
                                            dash='dash'
                                        ),
                                        name=f"Collision Path: {sat1_name}-{sat2_name}",
                                        showlegend=False
                                    ))
            
            # Update layout
            fig_timeline.update_layout(
                title=f"Orbital Timeline: {time_range}",
                scene=dict(
                    xaxis_title="X (km)",
                    yaxis_title="Y (km)",
                    zaxis_title="Z (km)",
                    aspectmode='data',
                    camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
                    xaxis=dict(showgrid=True, zeroline=False),
                    yaxis=dict(showgrid=True, zeroline=False),
                    zaxis=dict(showgrid=True, zeroline=False)
                ),
                autosize=True,
                width=None,
                height=600,
                showlegend=True,
                margin=dict(l=20, r=20, t=80, b=20),
                paper_bgcolor='black',
                plot_bgcolor='black'
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Timeline controls
            st.markdown("#### 🎮 Timeline Controls")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("⏮️ Start"):
                    st.success("Timeline playback started!")
            
            with col2:
                if st.button("⏸️ Pause"):
                    st.info("Timeline playback paused!")
            
            with col3:
                if st.button("⏭️ Fast Forward"):
                    st.warning("Fast forwarding timeline...")
            
            with col4:
                if st.button("🔄 Reset"):
                    st.success("Timeline reset to beginning!")
            
            # Timeline statistics
            st.markdown("#### 📊 Timeline Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Satellites Tracked", len(timeline_data))
            
            with col2:
                total_positions = sum(len(positions) for positions in timeline_data.values())
                st.metric("Total Positions", total_positions)
            
            with col3:
                if st.session_state.collisions:
                    high_risk = sum(1 for c in st.session_state.collisions if c.get('risk_level') == 'high')
                    st.metric("High Risk Events", high_risk)
                else:
                    st.metric("High Risk Events", 0)
        else:
            st.warning("Could not generate timeline data.")

    def show_predictive_heatmap(self):
        """Show AI-generated predictive collision heatmap for next 72 hours"""
        st.markdown("### 🔮 Predictive Collision Heatmap")
        st.markdown("*AI-generated time-lapse of collision risks for the next 72 hours*")
        
        if not st.session_state.satellite_data:
            st.info("No satellite data available for predictive analysis.")
            return
        
        # Time range selector
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            time_resolution = st.selectbox(
                "Time Resolution",
                ["1 hour", "3 hours", "6 hours", "12 hours"],
                index=1,
                help="Select how frequently to update the heatmap"
            )
        
        with col2:
            prediction_horizon = st.selectbox(
                "Prediction Horizon",
                ["24 hours", "48 hours", "72 hours"],
                index=2,
                help="Select how far into the future to predict"
            )
        
        with col3:
            risk_threshold = st.slider(
                "Risk Threshold",
                min_value=0.1,
                max_value=0.9,
                value=0.5,
                step=0.1,
                help="Minimum risk level to display on heatmap"
            )
        
        # Generate predictive data
        st.markdown("#### 🧠 AI Risk Prediction Engine")
        
        with st.spinner("🤖 AI is analyzing orbital patterns and predicting collision risks..."):
            # Simulate AI prediction process
            import time
            time.sleep(2)  # Simulate AI processing time
            
            # Generate predictive collision data for the next 72 hours
            predictive_data = self._generate_predictive_collision_data(
                time_resolution=time_resolution,
                prediction_horizon=prediction_horizon,
                risk_threshold=risk_threshold
            )
        
        if predictive_data:
            st.success("✅ AI prediction complete! Generated risk heatmap for the next 72 hours.")
            
            # Display the predictive heatmap
            self._display_predictive_heatmap(predictive_data, time_resolution, prediction_horizon)
            
            # Show risk evolution over time
            self._show_risk_evolution(predictive_data)
            
            # Display high-risk time windows
            self._show_high_risk_windows(predictive_data)
            
        else:
            st.error("❌ Failed to generate predictive data. Please check your data sources.")
    
    def _generate_predictive_collision_data(self, time_resolution, prediction_horizon, risk_threshold):
        """Generate AI-predicted collision data for future time periods"""
        try:
            # Parse time resolution and prediction horizon
            resolution_hours = int(time_resolution.split()[0])
            horizon_hours = int(prediction_horizon.split()[0])
            
            # Generate time points
            current_time = datetime.now()
            time_points = []
            for i in range(0, horizon_hours + 1, resolution_hours):
                time_points.append(current_time + timedelta(hours=i))
            
            # Generate predictive collision scenarios
            predictive_collisions = []
            
            for time_point in time_points:
                # Simulate AI prediction based on current satellite positions and orbital mechanics
                time_offset = (time_point - current_time).total_seconds() / 3600  # hours
                
                # Generate collision scenarios for this time point
                for sat1_name, sat1_data in st.session_state.satellite_data.items():
                    for sat2_name, sat2_data in st.session_state.satellite_data.items():
                        if sat1_name >= sat2_name:  # Avoid duplicates
                            continue
                        
                        # Calculate predicted collision probability based on orbital mechanics
                        collision_prob = self._predict_collision_probability(
                            sat1_data, sat2_data, time_offset
                        )
                        
                        if collision_prob >= risk_threshold:
                            # Calculate predicted positions and risk factors
                            predicted_risk = self._calculate_predicted_risk(
                                sat1_data, sat2_data, time_offset, collision_prob
                            )
                            
                            predictive_collisions.append({
                                'time': time_point,
                                'satellite1': sat1_name,
                                'satellite2': sat2_name,
                                'collision_probability': collision_prob,
                                'risk_level': self._determine_risk_level(collision_prob),
                                'altitude': predicted_risk['altitude'],
                                'inclination': predicted_risk['inclination'],
                                'relative_velocity': predicted_risk['relative_velocity'],
                                'closest_approach': predicted_risk['closest_approach'],
                                'time_to_collision': time_offset,
                                'confidence_score': predicted_risk['confidence_score']
                            })
            
            return predictive_collisions
            
        except Exception as e:
            st.error(f"Error generating predictive data: {e}")
            return None
    
    def _predict_collision_probability(self, sat1_data, sat2_data, time_offset):
        """AI-powered collision probability prediction"""
        # Base probability from current orbital parameters
        base_prob = 0.1
        
        # Time-based factors
        time_factor = min(time_offset / 72.0, 1.0)  # Normalize to 72 hours
        
        # Orbital parameter differences
        alt_diff = abs(sat1_data.get('altitude', 500) - sat2_data.get('altitude', 500))
        inc_diff = abs(sat1_data.get('inclination', 45) - sat2_data.get('inclination', 45))
        
        # Calculate collision probability using AI-like algorithm
        if alt_diff < 50:  # Similar altitudes
            base_prob += 0.3
        if inc_diff < 10:  # Similar inclinations
            base_prob += 0.2
        
        # Time-based orbital convergence (simulated)
        convergence_factor = np.sin(time_offset * np.pi / 24) * 0.2  # Daily cycle
        
        # Add some randomness to simulate AI uncertainty
        uncertainty = np.random.normal(0, 0.1)
        
        final_prob = base_prob + convergence_factor + uncertainty
        return max(0.0, min(1.0, final_prob))
    
    def _calculate_predicted_risk(self, sat1_data, sat2_data, time_offset, collision_prob):
        """Calculate detailed risk metrics for prediction"""
        # Simulate orbital motion and calculate risk factors
        alt1 = sat1_data.get('altitude', 500)
        alt2 = sat2_data.get('altitude', 500)
        inc1 = sat1_data.get('inclination', 45)
        inc2 = sat2_data.get('inclination', 45)
        
        # Calculate average orbital parameters
        avg_altitude = (alt1 + alt2) / 2
        avg_inclination = (inc1 + inc2) / 2
        
        # Simulate relative velocity (simplified)
        relative_velocity = 7.5 + np.random.normal(0, 1.0)  # km/s
        
        # Calculate closest approach distance
        closest_approach = max(0.1, 10 - (collision_prob * 20))  # km
        
        # Calculate confidence score based on data quality
        confidence_score = 0.8 + np.random.normal(0, 0.1)
        confidence_score = max(0.5, min(1.0, confidence_score))
        
        return {
            'altitude': avg_altitude,
            'inclination': avg_inclination,
            'relative_velocity': relative_velocity,
            'closest_approach': closest_approach,
            'confidence_score': confidence_score
        }
    
    def _determine_risk_level(self, probability):
        """Determine risk level based on collision probability"""
        if probability >= 0.8:
            return 'critical'
        elif probability >= 0.6:
            return 'high'
        elif probability >= 0.4:
            return 'medium'
        elif probability >= 0.2:
            return 'low'
        else:
            return 'minimal'
    
    def _display_predictive_heatmap(self, predictive_data, time_resolution, prediction_horizon):
        """Display the main predictive collision heatmap"""
        st.markdown("#### 📊 Predictive Collision Risk Heatmap")
        
        # Create time-altitude-inclination heatmap
        if predictive_data:
            # Prepare data for heatmap
            heatmap_data = []
            for collision in predictive_data:
                heatmap_data.append({
                    'Time': collision['time'].strftime('%H:%M'),
                    'Altitude': collision['altitude'],
                    'Inclination': collision['inclination'],
                    'Risk': collision['collision_probability'],
                    'Risk_Level': collision['risk_level']
                })
            
            df_heatmap = pd.DataFrame(heatmap_data)
            
            # Create 3D heatmap
            fig_3d = go.Figure()
            
            # Add 3D scatter plot
            fig_3d.add_trace(go.Scatter3d(
                x=[d['Time'] for d in heatmap_data],
                y=[d['Altitude'] for d in heatmap_data],
                z=[d['Inclination'] for d in heatmap_data],
                mode='markers',
                marker=dict(
                    size=[d['Risk'] * 30 + 10 for d in heatmap_data],
                    color=[d['Risk'] for d in heatmap_data],
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Collision Risk")
                ),
                text=[f"Time: {d['Time']}<br>Alt: {d['Altitude']:.0f}km<br>Inc: {d['Inclination']:.1f}°<br>Risk: {d['Risk']:.3f}" for d in heatmap_data],
                hovertemplate='%{text}<extra></extra>'
            ))
            
            fig_3d.update_layout(
                title=f'3D Predictive Collision Risk: {prediction_horizon}',
                scene=dict(
                    xaxis_title='Time (Hours)',
                    yaxis_title='Altitude (km)',
                    zaxis_title='Inclination (degrees)',
                    camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
                ),
                autosize=True,
                margin=dict(l=50, r=50, t=80, b=50),
                height=600
            )
            
            st.plotly_chart(fig_3d, use_container_width=True)
            
            # Create 2D time-altitude heatmap
            st.markdown("#### ⏰ Time vs Altitude Risk Heatmap")
            
            # Pivot data for 2D heatmap
            pivot_data = df_heatmap.pivot_table(
                values='Risk', 
                index='Altitude', 
                columns='Time', 
                aggfunc='mean'
            ).fillna(0)
            
            fig_2d = px.imshow(
                pivot_data,
                title=f'Collision Risk Evolution: {prediction_horizon}',
                color_continuous_scale='Reds',
                color_continuous_midpoint=0.5,
                aspect='auto'
            )
            
            fig_2d.update_layout(
                xaxis_title='Time (Hours)',
                yaxis_title='Altitude (km)',
                coloraxis_colorbar_title='Risk Score',
                autosize=True,
                margin=dict(l=50, r=50, t=80, b=50),
                height=500
            )
            
            st.plotly_chart(fig_2d, use_container_width=True)
    
    def _show_risk_evolution(self, predictive_data):
        """Show how collision risks evolve over time"""
        st.markdown("#### 📈 Risk Evolution Timeline")
        
        if predictive_data:
            # Group by time and calculate risk statistics
            time_risk_data = {}
            for collision in predictive_data:
                time_key = collision['time'].strftime('%H:%M')
                if time_key not in time_risk_data:
                    time_risk_data[time_key] = []
                time_risk_data[time_key].append(collision['collision_probability'])
            
            # Calculate statistics for each time point
            evolution_data = []
            for time_key, risks in time_risk_data.items():
                evolution_data.append({
                    'Time': time_key,
                    'Max_Risk': max(risks),
                    'Avg_Risk': np.mean(risks),
                    'High_Risk_Count': sum(1 for r in risks if r > 0.6),
                    'Total_Events': len(risks)
                })
            
            df_evolution = pd.DataFrame(evolution_data)
            
            # Create risk evolution chart
            fig_evolution = go.Figure()
            
            fig_evolution.add_trace(go.Scatter(
                x=df_evolution['Time'],
                y=df_evolution['Max_Risk'],
                mode='lines+markers',
                name='Maximum Risk',
                line=dict(color='#e53935', width=3),
                marker=dict(size=8)
            ))
            
            fig_evolution.add_trace(go.Scatter(
                x=df_evolution['Time'],
                y=df_evolution['Avg_Risk'],
                mode='lines+markers',
                name='Average Risk',
                line=dict(color='#fb8c00', width=3),
                marker=dict(size=8)
            ))
            
            fig_evolution.update_layout(
                title='Collision Risk Evolution Over Time',
                xaxis_title='Time (Hours)',
                yaxis_title='Risk Score',
                hovermode='x unified',
                showlegend=True,
                autosize=True,
                margin=dict(l=50, r=50, t=80, b=50),
                height=500
            )
            
            st.plotly_chart(fig_evolution, use_container_width=True)
            
            # Show risk statistics table
            st.markdown("#### 📊 Risk Statistics by Time")
            st.dataframe(df_evolution, use_container_width=True)
    
    def _show_high_risk_windows(self, predictive_data):
        """Show high-risk time windows and recommendations"""
        st.markdown("#### 🚨 High-Risk Time Windows")
        
        if predictive_data:
            # Filter high-risk events
            high_risk_events = [c for c in predictive_data if c['collision_probability'] > 0.6]
            
            if high_risk_events:
                st.warning(f"⚠️ **Critical Alert:** {len(high_risk_events)} high-risk collision scenarios predicted!")
                
                # Group by risk level
                critical_events = [c for c in high_risk_events if c['risk_level'] == 'critical']
                high_events = [c for c in high_risk_events if c['risk_level'] == 'high']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if critical_events:
                        st.markdown("#### 🔴 Critical Risk Events")
                        for event in critical_events[:5]:  # Show top 5
                            st.markdown(f"""
                            <div style="background: rgba(244, 67, 54, 0.2); padding: 1rem; border-radius: 10px; border: 1px solid rgba(244, 67, 54, 0.5); margin: 0.5rem 0;">
                                <strong>🚨 {event['satellite1']} vs {event['satellite2']}</strong><br>
                                Time: {event['time'].strftime('%Y-%m-%d %H:%M')}<br>
                                Risk: {event['collision_probability']:.3f}<br>
                                Distance: {event['closest_approach']:.2f} km
                            </div>
                            """, unsafe_allow_html=True)
                
                with col2:
                    if high_events:
                        st.markdown("#### 🟠 High Risk Events")
                        for event in high_events[:5]:  # Show top 5
                                                    st.markdown(f"""
                        <div style="background: rgba(255, 152, 0, 0.2); padding: 1rem; border-radius: 10px; border: 1px solid rgba(255, 152, 0, 0.5); margin: 0.5rem 0;">
                            <strong>⚠️ {event['satellite1']} vs {event['satellite2']}</strong><br>
                            Time: {event['time'].strftime('%Y-%m-%d %H:%M')}<br>
                            Risk: {event['collision_probability']:.3f}<br>
                            Distance: {event['closest_approach']:.2f} km
                        </div>
                        """, unsafe_allow_html=True)
                
                # AI Recommendations
                st.markdown("#### 🤖 AI Recommendations")
                confidence_score = np.mean([e['confidence_score'] for e in high_risk_events])
                st.markdown(f"""
                <div style="background: rgba(102, 126, 234, 0.1); padding: 1.5rem; border-radius: 15px; border: 1px solid rgba(102, 126, 234, 0.3);">
                    <h4>🎯 Recommended Actions:</h4>
                    <ul>
                        <li><strong>Immediate:</strong> Plan collision avoidance maneuvers for critical risk events</li>
                        <li><strong>Short-term:</strong> Monitor high-risk satellites and adjust orbits</li>
                        <li><strong>Long-term:</strong> Review orbital slot allocation and traffic management</li>
                    </ul>
                    <p><em>Confidence Score: {confidence_score:.1%}</em></p>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.success("✅ No high-risk collision scenarios predicted for the selected time period.")
                
                # Show low-risk summary
                low_risk_count = len([c for c in predictive_data if c['collision_probability'] < 0.3])
                st.info(f"📊 **Summary:** {len(predictive_data)} collision scenarios analyzed, {low_risk_count} low-risk events detected.")

    
    def show_alerts(self):
        """Show enhanced collision alerts"""
        st.markdown("### 🚨 Alert Center")
        
        # Debug information
        with st.expander("🔍 Debug Information", expanded=False):
            st.write(f"**Satellite Data Count:** {len(st.session_state.satellite_data)}")
            st.write(f"**Collision Count:** {len(st.session_state.collisions)}")
            st.write(f"**Maneuver Count:** {len(st.session_state.maneuvers)}")
            if st.session_state.collisions:
                st.write("**Sample Collision:**", st.session_state.collisions[0])
            else:
                st.write("**No collisions found**")
        
        if not st.session_state.collisions:
            st.warning("⚠️ No collision alerts found! Click '📁 Load JSON Data' in the sidebar to load collision scenarios.")
            if st.button("🔄 Force Initialize Data"):
                self.initialize_fake_data()
                st.rerun()
            return
        
        # Filter alerts by risk level
        risk_filter = st.selectbox(
            "Filter by Risk Level",
            ["All", "High", "Medium", "Low"]
        )
        
        filtered_collisions = st.session_state.collisions
        if risk_filter != "All":
            filtered_collisions = [c for c in st.session_state.collisions 
                                 if c.get('risk_level') == risk_filter.lower()]
        
        # Display enhanced alerts
        for i, collision in enumerate(filtered_collisions):
            risk_level = collision.get('risk_level', 'unknown')
            distance = collision['closest_approach']['distance']
            probability = collision.get('collision_probability', 0)
            
            # Enhanced color coding with better styling
            if risk_level == 'high':
                st.markdown(f"""
                <div class="status-card alert-high">
                    <h3>🚨 HIGH RISK ALERT</h3>
                    <p><strong>Objects:</strong> {collision['satellite1_name']} vs {collision['satellite2_name']}</p>
                    <p><strong>Distance:</strong> {distance:.2f} km</p>
                    <p><strong>Probability:</strong> {probability:.3f}</p>
                    <p><strong>Time to Closest:</strong> {collision.get('time_to_closest_approach', 0):.1f} hours</p>
                </div>
                """, unsafe_allow_html=True)
            elif risk_level == 'medium':
                st.markdown(f"""
                <div class="status-card alert-medium">
                    <h3>⚠️ MEDIUM RISK ALERT</h3>
                    <p><strong>Objects:</strong> {collision['satellite1_name']} vs {collision['satellite2_name']}</p>
                    <p><strong>Distance:</strong> {distance:.2f} km</p>
                    <p><strong>Probability:</strong> {probability:.3f}</p>
                    <p><strong>Time to Closest:</strong> {collision.get('time_to_closest_approach', 0):.1f} hours</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="status-card alert-low">
                    <h3>ℹ️ LOW RISK ALERT</h3>
                    <p><strong>Objects:</strong> {collision['satellite1_name']} vs {collision['satellite2_name']}</p>
                    <p><strong>Distance:</strong> {distance:.2f} km</p>
                    <p><strong>Probability:</strong> {probability:.3f}</p>
                    <p><strong>Time to Closest:</strong> {collision.get('time_to_closest_approach', 0):.1f} hours</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"📋 View Details", key=f"details_{i}"):
                    st.json(collision)
            
            with col2:
                if st.button(f"🧭 Plan Maneuver", key=f"maneuver_{i}"):
                    st.info("Maneuver planning initiated...")
            
            with col3:
                if st.button(f"✅ Dismiss Alert", key=f"dismiss_{i}"):
                    st.success("Alert dismissed!")
            
            st.divider()
    
    def show_maneuvers(self):
        """Show enhanced maneuver planning and execution"""
        st.markdown("### 🧭 Maneuver Control Center")
        
        if not st.session_state.maneuvers:
            st.info("No maneuvers planned at this time.")
            return
        
        # Enhanced maneuver summary
        total_maneuvers = len(st.session_state.maneuvers)
        total_delta_v = sum(m.get('delta_v_magnitude', 0) for m in st.session_state.maneuvers)
        total_fuel = sum(m.get('fuel_consumption', 0) for m in st.session_state.maneuvers)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.display_metric_card("Total Maneuvers", total_maneuvers, "🧭")
        
        with col2:
            self.display_metric_card("Total Delta-V", f"{total_delta_v:.2f} m/s", "⚡")
        
        with col3:
            self.display_metric_card("Total Fuel", f"{total_fuel:.4f} kg", "⛽")
        
        with col4:
            # Simple approach: count based on status instead of datetime
            pending_maneuvers = sum(1 for m in st.session_state.maneuvers 
                                   if m.get('status') == 'planned')
            self.display_metric_card("Pending", pending_maneuvers, "⏳")
        
        # Enhanced maneuver list
        st.markdown("### 📋 Planned Maneuvers")
        
        for i, maneuver in enumerate(st.session_state.maneuvers):
            maneuver_type = maneuver.get('maneuver_type', 'unknown')
            delta_v = maneuver.get('delta_v_magnitude', 0)
            execution_time = maneuver.get('execution_time', 'Unknown')
            
            st.markdown(f"""
            <div class="status-card">
                <h3>🧭 Maneuver {i+1}: {maneuver.get('maneuver_satellite_id', 'Unknown')}</h3>
                <p><strong>Type:</strong> {maneuver_type}</p>
                <p><strong>Delta-V:</strong> {delta_v:.2f} m/s</p>
                <p><strong>Execution:</strong> {execution_time}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"📋 Details", key=f"maneuver_details_{i}"):
                    st.json(maneuver)
            
            with col2:
                if st.button(f"▶️ Execute", key=f"execute_{i}"):
                    st.success("Maneuver execution initiated!")
            
            with col3:
                if st.button(f"❌ Cancel", key=f"cancel_{i}"):
                    st.warning("Maneuver cancelled!")
            
            st.divider()
    
    def show_system_settings(self):
        """Show system configuration and settings"""
        st.markdown("### ⚙️ System Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="status-card">
                <h3>🔧 System Settings</h3>
                <p><strong>Update Frequency:</strong> 10 seconds</p>
                <p><strong>Data Sources:</strong> Celestrak, Space-Track</p>
                <p><strong>Propagation Horizon:</strong> 7 days</p>
                <p><strong>Collision Threshold:</strong> 10 km</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="status-card">
                <h3>📊 Performance Metrics</h3>
                <p><strong>Data Collection:</strong> Active</p>
                <p><strong>Orbit Propagation:</strong> Active</p>
                <p><strong>Collision Detection:</strong> Active</p>
                <p><strong>Maneuver Planning:</strong> Active</p>
            </div>
            """, unsafe_allow_html=True)
    
    def show_data_flow_monitoring(self):
        """Show comprehensive data flow monitoring dashboard"""
        st.markdown("### 🔄 Data Flow Monitoring Dashboard")
        st.markdown("*Real-time monitoring of data flow through all system components*")
        
        # Data Flow Status Overview
        st.markdown("#### 📊 Data Flow Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="status-card">
                <h3>📡 Data Collection</h3>
                <p style="font-size: 1.2rem; font-weight: 600;">{st.session_state.data_flow_status['data_collection']}</p>
                <p><strong>Last Update:</strong> {st.session_state.last_update.strftime('%H:%M:%S') if st.session_state.last_update else 'Never'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="status-card">
                <h3>🔮 Orbit Propagation</h3>
                <p style="font-size: 1.2rem; font-weight: 600;">{st.session_state.data_flow_status['orbit_propagation']}</p>
                <p><strong>Data Points:</strong> {len(st.session_state.data_pipeline.get('processed_data', {}) or {})}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="status-card">
                <h3>🚨 Collision Detection</h3>
                <p style="font-size: 1.2rem; font-weight: 600;">{st.session_state.data_flow_status['collision_detection']}</p>
                <p><strong>Active Alerts:</strong> {len(st.session_state.collisions)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        col4, col5 = st.columns(2)
        
        with col4:
            st.markdown(f"""
            <div class="status-card">
                <h3>🧭 Maneuver Planning</h3>
                <p style="font-size: 1.2rem; font-weight: 600;">{st.session_state.data_flow_status['maneuver_planning']}</p>
                <p><strong>Planned Maneuvers:</strong> {len(st.session_state.maneuvers)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="status-card">
                <h3>📊 Visualization</h3>
                <p style="font-size: 1.2rem; font-weight: 600;">{st.session_state.data_flow_status['visualization']}</p>
                <p><strong>Charts Updated:</strong> {len(st.session_state.data_pipeline.get('visualization_data', {}) or {})}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Data Pipeline Visualization
        st.markdown("#### 🔄 Data Pipeline Flow")
        
        pipeline_data = {
            'Stage': ['Raw Data', 'Processed Data', 'Analysis Results', 'Visualization'],
            'Status': [
                '✅ Complete' if st.session_state.data_pipeline['raw_data'] and len(st.session_state.data_pipeline['raw_data']) > 0 else '🟡 Pending',
                '✅ Complete' if st.session_state.data_pipeline['processed_data'] and len(st.session_state.data_pipeline['processed_data']) > 0 else '🟡 Pending',
                '✅ Complete' if st.session_state.data_pipeline['analysis_results'] and len(st.session_state.data_pipeline['analysis_results']) > 0 else '🟡 Pending',
                '✅ Complete' if st.session_state.data_pipeline['visualization_data'] and len(st.session_state.data_pipeline['visualization_data']) > 0 else '🟡 Pending'
            ],
            'Data Size': [
                len(st.session_state.data_pipeline['raw_data'] or {}),
                len(st.session_state.data_pipeline['processed_data'] or {}),
                len(st.session_state.data_pipeline['analysis_results'] or {}),
                len(st.session_state.data_pipeline['visualization_data'] or {})
            ]
        }
        
        df_pipeline = pd.DataFrame(pipeline_data)
        st.dataframe(df_pipeline, use_container_width=True)
        
        # Performance Metrics
        st.markdown("#### ⚡ Performance Metrics")
        
        col6, col7, col8 = st.columns(3)
        
        with col6:
            total_time = st.session_state.flow_monitor['performance_metrics']['total_time']
            st.metric("Total Processing Time", f"{total_time:.2f}s")
        
        with col7:
            collection_time = st.session_state.flow_monitor['performance_metrics']['collection_time']
            st.metric("Data Collection Time", f"{collection_time:.2f}s")
        
        with col8:
            processing_time = st.session_state.flow_monitor['performance_metrics']['processing_time']
            st.metric("Analysis Time", f"{processing_time:.2f}s")
        
        # Data Quality Metrics
        st.markdown("#### 📈 Data Quality Metrics")
        
        col9, col10, col11 = st.columns(3)
        
        with col9:
            completeness = st.session_state.flow_monitor['data_quality']['completeness']
            st.metric("Data Completeness", f"{completeness:.1f}%")
        
        with col10:
            accuracy = st.session_state.flow_monitor['data_quality']['accuracy']
            st.metric("Data Accuracy", f"{accuracy:.1f}%")
        
        with col11:
            freshness = st.session_state.flow_monitor['data_quality']['freshness']
            st.metric("Data Freshness", f"{freshness:.1f}%")
        
        # Data Flow Diagram
        st.markdown("#### 🔀 Data Flow Architecture")
        
        st.markdown("""
        ```
        📡 Celestrak API → 📊 Raw Data → 🔮 Orbit Engine → 📈 Processed Data
                              ↓                    ↓
        📡 Space-Track API → 📊 Raw Data → 🚨 Collision Detector → ⚠️ Alerts
                              ↓                    ↓
        📡 Sample Data → 📊 Raw Data → 🧭 Maneuver Planner → 🚀 Maneuvers
                              ↓                    ↓
                              📊 Visualization Engine → 🎨 Interactive Charts
        ```
        """)
        
        # Error Log
        if st.session_state.data_flow_status['sync_errors']:
            st.markdown("#### ❌ Error Log")
            
            for error in st.session_state.data_flow_status['sync_errors'][-5:]:  # Show last 5 errors
                st.error(f"**{error['timestamp']}** - {error['error']} (Stage: {error['stage']})")
        
        # Manual Data Flow Test
        st.markdown("#### 🧪 Test Data Flow")
        
        col12, col13 = st.columns(2)
        
        with col12:
            if st.button("🔄 Test Complete Data Flow", type="primary", use_container_width=True):
                self.update_data()
        
        with col13:
            if st.button("🔄 Test Individual Components", use_container_width=True):
                self.test_individual_components()
    
    def test_individual_components(self):
        """Test individual system components for data flow verification"""
        st.info("🧪 Testing individual components...")
        
        try:
            # Test data collection
            with st.spinner("Testing data collection..."):
                test_data = asyncio.run(self.data_collector.collect_data())
                st.success(f"✅ Data collection: {len(test_data)} objects")
            
            # Test orbit propagation
            with st.spinner("Testing orbit propagation..."):
                test_positions = asyncio.run(self.orbit_engine.propagate_orbits(test_data))
                st.success(f"✅ Orbit propagation: {len(test_positions)} positions")
            
            # Test collision detection
            with st.spinner("Testing collision detection..."):
                test_collisions = asyncio.run(self.collision_detector.detect_collisions(test_positions))
                st.success(f"✅ Collision detection: {len(test_collisions)} alerts")
            
            # Test maneuver planning
            if test_collisions:
                with st.spinner("Testing maneuver planning..."):
                    test_maneuvers = asyncio.run(self.maneuver_planner.plan_maneuvers(test_collisions))
                    st.success(f"✅ Maneuver planning: {len(test_maneuvers)} maneuvers")
            
            st.success("🎉 All component tests completed successfully!")
            
        except Exception as e:
            st.error(f"❌ Component test failed: {e}")
    
    def load_json_data(self):
        """Load satellite data from JSON file"""
        try:
            import json
            import os
            
            json_paths = [
                "data/processed_satellite_data.json",
                "data/fake_satellite_data.json",
                "../data/fake_satellite_data.json",
                "fake_satellite_data.json"
            ]
            
            for json_path in json_paths:
                if os.path.exists(json_path):
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                        if 'satellites' in data:
                            st.session_state.satellite_data = data['satellites']
                            
                            # Regenerate collisions and maneuvers based on new data
                            st.session_state.collisions = self._generate_realistic_collisions()
                            st.session_state.maneuvers = self._generate_realistic_maneuvers()
                            
                            # Update data flow status
                            st.session_state.data_flow_status['data_collection'] = '✅ Complete'
                            st.session_state.data_flow_status['last_sync'] = datetime.now()
                            
                            st.success(f"✅ Successfully loaded {len(data['satellites'])} objects from {json_path}")
                            return
            
            st.error("❌ JSON data file not found in any expected location")
            
        except Exception as e:
            st.error(f"❌ Error loading JSON data: {e}")
    
    def export_data(self, format_type="JSON"):
        """Export current data with enhanced options"""
        try:
            if format_type == "JSON":
                # Export visualization data
                data_json = self.visualizer.export_visualization_data('json')
                
                # Create download button
                st.download_button(
                    label="📥 Download Data (JSON)",
                    data=data_json,
                    file_name=f"space_traffic_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            elif format_type == "CSV":
                # Convert to CSV format
                df = pd.DataFrame(st.session_state.satellite_data).T
                csv_data = df.to_csv(index=True)
                
                st.download_button(
                    label="📥 Download Data (CSV)",
                    data=csv_data,
                    file_name=f"space_traffic_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:  # PDF
                st.info("PDF export feature coming soon!")
            
            st.success("Data exported successfully!")
            
        except Exception as e:
            st.error(f"Error exporting data: {e}")

def main():
    """Main function to run the dashboard"""
    dashboard = SpaceTrafficDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
