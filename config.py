import os
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_required_env(var_name: str) -> str:
    """Get a required environment variable or raise an error"""
    value = os.getenv(var_name)
    if not value:
        error_msg = f"Missing required environment variable: {var_name}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    return value

# API Keys
try:
    DEEPSEEK_API_KEY = get_required_env('DEEPSEEK_API_KEY')
    GEMINI_API_KEY = get_required_env('GEMINI_API_KEY')
    GEMINI_OPERATIONS_KEY = get_required_env('GEMINI_OPERATIONS_KEY')
    GEMINI_SUPERVISOR_KEY = get_required_env('GEMINI_SUPERVISOR_KEY')
    GEMINI_INVENTORY_KEY = get_required_env('GEMINI_INVENTORY_KEY')
except ValueError as e:
    logger.error(f"Configuration error: {str(e)}")
    logger.error("Please set up your .env file with the required API keys")
    raise

# Model configurations
INVENTORY_MODEL = "deepseek-coder"
OPERATIONS_MODEL = "gemini-pro"
SUPERVISOR_MODEL = "gemini-pro"

# System configurations
MAX_RETRIES = 3
TIMEOUT = 30  # seconds

# Constants
SYSTEM_TIME = "2025-01-09T23:41:00+01:00"
