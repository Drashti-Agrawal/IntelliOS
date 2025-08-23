# llm_layer.py
import os
import sys
import time
import logging
import httpx
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

def _get_llm_client():
    """Initialize LLM client lazily to avoid import-time errors"""
    try:
        import groq
        import instructor
        from config.config import ActivityLog
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("GROQ_API_KEY not found in environment variables. LLM parsing will be disabled.")
            return None, None
            
        client = instructor.patch(groq.Groq(api_key=api_key))
        return client, ActivityLog
    except ImportError as e:
        logger.warning(f"LLM dependencies not available: {e}. LLM parsing will be disabled.")
        return None, None
    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}")
        return None, None

def parse_with_llm(provider: str, message: str, max_retries=3, base_delay=5):
    """
    Parses a log message using a constrained LLM call with Groq.
    Returns a Pydantic object on success, or None on failure.
    
    Args:
        provider: The provider of the log (e.g., 'Service Control Manager')
        message: The raw log message to parse
        max_retries: Maximum number of retries for rate limit errors
        base_delay: Base delay in seconds for exponential backoff
    """
    # Get LLM client lazily
    client, ActivityLog = _get_llm_client()
    
    if client is None or ActivityLog is None:
        logger.warning("LLM client not available. Skipping LLM parsing.")
        return None
    
    retry_count = 0
    while retry_count <= max_retries:
        try:
            logger.info(f"Attempting LLM parsing for provider: '{provider}'")
            response = client.chat.completions.create(
                model="llama3-70b-8192",  # Using Llama 3 70B model via Groq
                response_model=ActivityLog,
                messages=[
                    {"role": "system", "content": "You are a world-class log parsing expert. Your task is to extract structured data from a raw log entry into the provided schema. Do not invent any information that is not present in the log. Categorize the event type accurately based on the provider and content."},
                    {"role": "user", "content": f"Provider: {provider}\n\nLog entry: {message}\n\nParse this log entry into structured data according to the ActivityLog schema."},
                ],
            )
            logger.info(f"LLM parsing successful for provider: '{provider}'")
            return response.dict() # Return as a dictionary
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limit error
                retry_count += 1
                if retry_count > max_retries:
                    logger.error(f"LLM parsing failed after {max_retries} retries due to rate limiting")
                    return None
                
                # Get retry-after header or use exponential backoff
                retry_after = int(e.response.headers.get('retry-after', base_delay * (2 ** retry_count)))
                logger.warning(f"Rate limit exceeded. Retrying in {retry_after} seconds (attempt {retry_count}/{max_retries})...")
                time.sleep(retry_after)
            else:
                logger.error(f"LLM parsing failed with HTTP error: {e}")
                return None
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            return None
