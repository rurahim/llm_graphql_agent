import os
import logging
from dotenv import load_dotenv
from langchain_community.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from prompts import graphql_prompt
from typing import Any, Dict, Optional
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from pydantic import BaseModel, Field

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class GraphQLTool(Tool, BaseModel):
    """Custom GraphQL Tool for LangChain"""
    name: str = "GraphQLJobsAPI"
    description: str = "Use this tool to query job listings from the GraphQL API."
    endpoint: str = ""
    headers: Dict[str, str] = {}
    client: Any = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def initialize(self):
        """Initialize the GraphQL client"""
        # Get GraphQL endpoint from environment
        self.endpoint = os.getenv("GRAPHQL_ENDPOINT") or os.getenv("GRAPHQL_API_URL")
        if not self.endpoint:
            logger.error("GRAPHQL_ENDPOINT or GRAPHQL_API_URL environment variable is required")
            raise ValueError("GRAPHQL_ENDPOINT or GRAPHQL_API_URL environment variable is required")
        
        logger.info(f"Using GraphQL endpoint: {self.endpoint}")
        
        # Set up GQL client
        transport = RequestsHTTPTransport(
            url=self.endpoint,
            headers=self.headers,
        )
        
        try:
            self.client = Client(transport=transport, fetch_schema_from_transport=True)
            logger.info(f"Successfully connected to GraphQL endpoint: {self.endpoint}")
        except Exception as e:
            logger.error(f"Failed to connect to GraphQL endpoint: {e}")
            raise
    
    def _run(self, query: str) -> str:
        """Execute a GraphQL query and return the results"""
        if self.client is None:
            self.initialize()
            
        logger.info(f"GraphQL Query: {query}")
        
        try:
            # Execute the query
            result = self.client.execute(gql(query))
            return str(result)
        except Exception as e:
            logger.error(f"GraphQL query failed: {e}")
            return f"Error executing GraphQL query: {str(e)}"

def setup_llm():
    """Set up the LLM, with Azure as primary and OpenAI as fallback"""
    
    try:
        # Try Azure OpenAI first
        if os.getenv("AZURE_API_KEY") and os.getenv("AZURE_API_ENDPOINT"):
            llm = AzureChatOpenAI(
                deployment_name=os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4"),
                openai_api_version=os.getenv("AZURE_API_VERSION", "2023-05-15"),
                openai_api_key=os.getenv("AZURE_API_KEY"),
                openai_api_base=os.getenv("AZURE_API_ENDPOINT"),
                openai_api_type="azure",
                temperature=0
            )
            logger.info("✅ Using Azure OpenAI.")
            return llm
        else:
            logger.warning("Missing Azure OpenAI config.")
    except Exception as e:
        logger.warning(f"⚠️ Azure OpenAI setup failed: {e}")
    
    # Fallback to standard OpenAI
    if os.getenv("OPENAI_API_KEY"):
        logger.info("⚠️ Falling back to OpenAI")
        return ChatOpenAI(
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    else:
        raise ValueError("Neither Azure OpenAI nor OpenAI API keys are available.")

# Initialize agent when module is loaded
try:
    # Create GraphQL tool
    graphql_tool = GraphQLTool()
    graphql_tool.initialize()
    
    # Setup LLM
    llm = setup_llm()
    
    # Initialize agent
    agent = initialize_agent(
        tools=[graphql_tool],
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
        return agent.run(graphql_prompt.format(question=question))
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return f"An error occurred while processing your query: {str(e)}"