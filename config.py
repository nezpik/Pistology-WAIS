import os
import streamlit as st
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file in development
load_dotenv()

def get_env_or_secret(key: str, default: str = None) -> str:
    """Get value from environment variable or Streamlit secrets"""
    # Try getting from Streamlit secrets first (for production)
    try:
        return st.secrets[key]
    except (KeyError, AttributeError):
        # Fall back to environment variable (for development)
        return os.getenv(key, default)

# API Keys
DEEPSEEK_API_KEY = get_env_or_secret("DEEPSEEK_API_KEY")
GEMINI_API_KEY = get_env_or_secret("GEMINI_API_KEY")
GEMINI_OPERATIONS_KEY = get_env_or_secret("GEMINI_OPERATIONS_KEY")
GEMINI_SUPERVISOR_KEY = get_env_or_secret("GEMINI_SUPERVISOR_KEY")
GEMINI_INVENTORY_KEY = get_env_or_secret("GEMINI_INVENTORY_KEY")

# Check for required API keys
if not all([DEEPSEEK_API_KEY, GEMINI_API_KEY, GEMINI_OPERATIONS_KEY, 
           GEMINI_SUPERVISOR_KEY, GEMINI_INVENTORY_KEY]):
    error_msg = "Missing required API keys. Please check your .env file or Streamlit secrets."
    logger.error(error_msg)
    raise ValueError(error_msg)

# Model configurations
INVENTORY_MODEL = "deepseek-coder"
OPERATIONS_MODEL = "gemini-pro"
SUPERVISOR_MODEL = "gemini-pro"

# System configurations
MAX_RETRIES = 3
TIMEOUT = 30  # seconds

# Constants
SYSTEM_TIME = "2025-01-09T23:41:00+01:00"
