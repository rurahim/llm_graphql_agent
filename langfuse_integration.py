import os
from dotenv import load_dotenv
from typing import Optional
import logging

# Conditionally import langfuse only if available
try:
    from langfuse import Langfuse
    from langfuse.decorators import observe
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False

logger = logging.getLogger(__name__)
load_dotenv()

# Initialize Langfuse client if environment variables are available
langfuse_client: Optional[object] = None

def init_langfuse():
    """Initialize Langfuse if environment variables are available"""
    global langfuse_client, LANGFUSE_AVAILABLE
    
    if not LANGFUSE_AVAILABLE:
        logger.info("Langfuse package not installed. Skipping initialization.")
        return None
    
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    if public_key and secret_key:
        try:
            langfuse_client = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=host
            )
            logger.info("✅ Langfuse initialized successfully.")
            return langfuse_client
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Langfuse: {e}")
            return None
    else:
        logger.info("❓ Langfuse keys not provided. Skipping initialization.")
        return None

# Initialize on module import
init_langfuse()

def trace_query(question: str, graphql_query: str, result: str):
    """
    Trace a query using Langfuse
    
    Args:
        question: The original natural language question
        graphql_query: The generated GraphQL query
        result: The result of the query
    """
    if not langfuse_client:
        return
    
    try:
        # Create a new trace
        trace = langfuse_client.trace(
            name="graphql_query",
            metadata={
                "question": question
            }
        )
        
        # Add spans for each step
        trace.span(
            name="question_analysis",
            input={"question": question},
        )
        
        trace.span(
            name="graphql_generation",
            input={"question": question},
            output={"graphql_query": graphql_query}
        )
        
        trace.span(
            name="query_execution",
            input={"graphql_query": graphql_query},
            output={"result": result}
        )
        
        # End the trace
        trace.end()
        
    except Exception as e:
        logger.error(f"Error in Langfuse tracing: {e}")

def is_available():
    """Check if Langfuse is available and initialized"""
    return langfuse_client is not None