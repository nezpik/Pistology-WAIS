import os
import streamlit as st
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def get_required_env(key: str) -> str:
    """Get a required environment variable or raise an error"""
    value = os.getenv(key)
    if not value:
        error_msg = f"Missing required environment variable: {key}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    return value

# API Keys - loaded from environment variables
try:
    DEEPSEEK_API_KEY = get_required_env('DEEPSEEK_API_KEY')
    GEMINI_API_KEY_SUPERVISOR = get_required_env('GEMINI_API_KEY_SUPERVISOR')
    GEMINI_API_KEY_INVENTORY = get_required_env('GEMINI_API_KEY_INVENTORY')
    GEMINI_API_KEY_OPERATIONS = get_required_env('GEMINI_API_KEY_OPERATIONS')
except ValueError as e:
    logger.error("Failed to load required API keys")
    raise

# Model configurations
DEEPSEEK_MODEL = "deepseek-coder-33b-instruct"
GEMINI_MODEL = "gemini-pro"

# System settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Application settings
MAX_TOKENS = 4096
TEMPERATURE = 0.7
TOP_P = 0.95

# System configurations
MAX_RETRIES = 3
TIMEOUT = 30  # seconds

# Constants
SYSTEM_TIME = "2025-01-09T23:41:00+01:00"
