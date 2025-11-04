"""
Configuration for OpenAI-powered multi-agent warehouse management system.

This module manages API keys, model configurations, and system settings
for the upgraded warehouse management system using OpenAI SDK.
"""

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


def get_optional_env(key: str, default: str = "") -> str:
    """Get an optional environment variable with a default value"""
    return os.getenv(key, default)


# OpenAI API Configuration
try:
    OPENAI_API_KEY = get_required_env('OPENAI_API_KEY')
except ValueError as e:
    logger.error("Failed to load required OpenAI API key")
    raise


# Model configurations for different agents
# Using GPT-4o for complex reasoning, GPT-4o-mini for simpler tasks
AGENT_MODELS = {
    "supervisor": get_optional_env('SUPERVISOR_MODEL', 'gpt-4o'),  # Routing and validation
    "inventory": get_optional_env('INVENTORY_MODEL', 'gpt-4o'),    # Inventory management
    "operations": get_optional_env('OPERATIONS_MODEL', 'gpt-4o'),  # Operations optimization
    "math": get_optional_env('MATH_MODEL', 'gpt-4o')               # Mathematical calculations
}


# Agent temperature settings (lower = more deterministic)
AGENT_TEMPERATURES = {
    "supervisor": 0.3,   # More deterministic for routing
    "inventory": 0.7,    # Balanced for analysis
    "operations": 0.7,   # Balanced for recommendations
    "math": 0.1          # Very deterministic for calculations
}


# Token limits
MAX_TOKENS = int(get_optional_env('MAX_TOKENS', '4096'))
MAX_CONTEXT_TOKENS = 128000  # GPT-4o context window


# System settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


# Application settings
ENABLE_STREAMING = os.getenv('ENABLE_STREAMING', 'True').lower() == 'true'
ENABLE_FUNCTION_CALLING = os.getenv('ENABLE_FUNCTION_CALLING', 'True').lower() == 'true'


# Retry and timeout settings
MAX_RETRIES = int(get_optional_env('MAX_RETRIES', '3'))
TIMEOUT = int(get_optional_env('TIMEOUT', '30'))  # seconds


# Agent orchestration settings
ENABLE_AGENT_HANDOFFS = True
ENABLE_PARALLEL_PROCESSING = True
MAX_CONVERSATION_HISTORY = 10  # Number of exchanges to keep in memory


# Document processing settings
MAX_DOCUMENT_SIZE_MB = 10
SUPPORTED_FORMATS = ['.pdf', '.txt', '.docx', '.csv', '.xlsx']


# Warehouse-specific settings
DEFAULT_WAREHOUSE_METRICS = {
    "safety_stock_z_score": 1.65,  # For 95% service level
    "lead_time_buffer_days": 2,
    "reorder_point_multiplier": 1.2
}


# System constants
SYSTEM_TIME = "2025-01-09T23:41:00+01:00"
SYSTEM_VERSION = "2.0.0"  # New OpenAI-powered version


# Logging configuration
if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)
else:
    logging.getLogger().setLevel(getattr(logging, LOG_LEVEL.upper()))


# Display configuration summary
def get_config_summary() -> dict:
    """Get a summary of the current configuration"""
    return {
        "version": SYSTEM_VERSION,
        "models": AGENT_MODELS,
        "streaming_enabled": ENABLE_STREAMING,
        "function_calling_enabled": ENABLE_FUNCTION_CALLING,
        "max_tokens": MAX_TOKENS,
        "debug_mode": DEBUG
    }


logger.info(f"Configuration loaded - Version: {SYSTEM_VERSION}")
logger.info(f"Using models: {AGENT_MODELS}")
