import os
import streamlit as st
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# API Keys
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
GEMINI_API_KEY_OPERATIONS = os.getenv('GEMINI_API_KEY_OPERATIONS')
GEMINI_API_KEY_SUPERVISOR = os.getenv('GEMINI_API_KEY_SUPERVISOR')
GEMINI_API_KEY_INVENTORY = os.getenv('GEMINI_API_KEY_INVENTORY')

# Check for required API keys
if not all([DEEPSEEK_API_KEY, GEMINI_API_KEY_OPERATIONS, 
           GEMINI_API_KEY_SUPERVISOR, GEMINI_API_KEY_INVENTORY]):
    error_msg = "Missing required API keys. Please check your .env file."
    logger.error(error_msg)
    raise ValueError(error_msg)

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
