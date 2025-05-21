import os
import logging
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from prompts import graphql_prompt
from typing import Any, Dict, Optional
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from langfuse_integration import trace_query, is_available as is_langfuse_available

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class GraphQLTool:
    """Custom GraphQL Tool for LangChain"""
    
    def __init__(self):
        """Initialize the GraphQL Tool"""
        # Get GraphQL endpoint from environment
        self._endpoint = os.getenv("GRAPHQL_ENDPOINT") or os.getenv("GRAPHQL_API_URL")
        if not self._endpoint:
            logger.error("GRAPHQL_ENDPOINT or GRAPHQL_API_URL environment variable is required")
            raise ValueError("GRAPHQL_ENDPOINT or GRAPHQL_API_URL environment variable is required")
        
        logger.info(f"Using GraphQL endpoint: {self._endpoint}")
        
        # Set up headers (if any)
        self.headers = {}
        
        # Set up GQL client
        transport = RequestsHTTPTransport(
            url=self._endpoint,
            headers=self.headers,
            verify=True,
            retries=3,
        )
        
        try:
            self.client = Client(transport=transport, fetch_schema_from_transport=False)
            logger.info(f"Successfully connected to GraphQL endpoint: {self._endpoint}")
        except Exception as e:
            logger.error(f"Failed to connect to GraphQL endpoint: {e}")
            raise
    
    @property
    def endpoint(self) -> str:
        """Get the GraphQL endpoint"""
        return self._endpoint
    
    def run(self, query: str) -> str:
        """Execute a GraphQL query and return the results"""
        # Clean up the query string
        query = query.replace('query:', '').strip().strip('"')
        if query.endswith('", fetch_schema_from_transport=False'):
            query = query[:-len('", fetch_schema_from_transport=False')]
        logger.info(f"GraphQL Query: {query}")
        
        result = None
        try:
            # Try a minimal query first to see what fields are available
            minimal_query = """
            query {
                jobs {
                    items {
                        name
                    }
                }
            }
            """
            try:
                minimal_result = self.client.execute(gql(minimal_query))
                logger.info(f"Minimal query result: {minimal_result}")
                result = str(minimal_result)
            except Exception as e:
                logger.warning(f"Failed to execute minimal query: {e}")
                # Try another field
                minimal_query = """
                query {
                    jobs {
                        items {
                            description
                        }
                    }
                }
                """
                try:
                    minimal_result = self.client.execute(gql(minimal_query))
                    logger.info(f"Minimal query result: {minimal_result}")
                    result = str(minimal_result)
                except Exception as e:
                    logger.warning(f"Failed to execute second minimal query: {e}")
            
            # Execute the actual query if minimal queries failed
            if not result:
                result = str(self.client.execute(gql(query)))
            
            # Log to Langfuse if available
            if is_langfuse_available():
                trace_query("", query, result)
                
            return result
        except Exception as e:
            error_msg = f"Error executing GraphQL query: {str(e)}"
            logger.error(f"GraphQL query failed: {e}")
            
            # Log error to Langfuse if available
            if is_langfuse_available():
                trace_query("", query, error_msg)
                
            return error_msg

# Initialize agent when module is loaded
try:
    # Create GraphQL tool
    graphql_tool = GraphQLTool()
    
    # Create Tool instance for LangChain
    tool = Tool(
        name="GraphQLJobsAPI",
        description="Use this tool to query job listings from the GraphQL API.",
        func=graphql_tool.run
    )
    
    # Setup LLM
    if os.getenv("OPENAI_API_KEY"):
        logger.info("Using OpenAI")
        llm = ChatOpenAI(
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-3.5-turbo"
        )
    else:
        logger.error("No OpenAI API key provided")
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # Initialize agent
    agent = initialize_agent(
        tools=[tool],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    logger.info("Agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize agent: {e}")
    agent = None

def query_agent(question: str) -> str:
    """Process a natural language query through the agent"""
    
    if agent is None:
        return "Agent initialization failed. Please check your environment variables and logs."
    
    try:
        logger.info(f"Processing query: {question}")
        result = agent.run(graphql_prompt.format(question=question))
        
        # Log to Langfuse if available
        if is_langfuse_available():
            trace_query(question, "", result)
            
        return result
    except Exception as e:
        error_msg = f"An error occurred while processing your query: {str(e)}"
        logger.error(f"Error processing query: {e}")
        
        # Log error to Langfuse if available
        if is_langfuse_available():
            trace_query(question, "", error_msg)
            
        return error_msg