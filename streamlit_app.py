"""
Main entry point for Streamlit Community Cloud deployment
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now we can import from frontend
try:
    from frontend.app import main
    
    if __name__ == "__main__":
        main()
except ImportError as e:
    # Fallback: try to import and run directly
    import streamlit as st
    st.error(f"Import error: {e}")
    st.info("Please ensure all dependencies are installed: pip install -r requirements.txt")
