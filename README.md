# LLM GraphQL Agent

This project allows users to query a GraphQL API using natural language via an LLM. It converts natural language queries into GraphQL requests against the Jobs API and returns results in human-readable text via a simple HTTP endpoint.

## Features

- Natural language to GraphQL query conversion using LangChain and OpenAI
- FastAPI endpoint for query submission
- Detailed logging of GraphQL queries
- Docker containerization for easy deployment
- Support for Azure OpenAI or standard OpenAI API

## Setup

### Prerequisites

- Python 3.9+
- Docker (optional, for containerized usage)
- OpenAI API key or Azure OpenAI API access

### Local Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/llm-graphql-agent.git
   cd llm-graphql-agent
   ```

2. Create a virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file using the provided `.env.example`
   ```bash
   cp .env.example .env
   # Edit the .env file with your API keys and settings
   ```

### Running Locally

Start the API server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Docker Setup

### Building the Docker Image

```bash
docker build -t llm-graphql-agent .
```

### Running the Docker Container

```bash
docker run -p 8000:8000 --env-file .env llm-graphql-agent
```

The API will be available at `http://localhost:8000`

## API Usage

### Query Endpoint

**POST /query**

Request body:
```json
{
  "q": "What JavaScript jobs are available in Berlin?"
}
```

Response:
```json
{
  "answer": "There are 3 JavaScript jobs available in Berlin: Frontend Developer at Prisma, Full-stack JavaScript Developer at Prisma, and JavaScript Developer at BCG Digital Ventures."
}
```

### Other Endpoints

- `GET /health` - Health check endpoint
- `GET /` - API information

## Example Queries

1. Find jobs by technology:
   ```
   What jobs are available for Python developers?
   ```

2. Find jobs by location:
   ```
   Show me all jobs in London
   ```

3. Find jobs by company:
   ```
   What positions does Shopify have open?
   ```

4. Combined queries:
   ```
   Are there any remote React jobs available?
   ```

## Project Structure

- `main.py` - FastAPI application and endpoints
- `agent.py` - LangChain agent and GraphQL tool implementation
- `prompts.py` - Prompt templates for the LLM
- `Dockerfile` - Docker configuration
- `.env.example` - Environment variable template

## Troubleshooting

- **API Key Issues**: Ensure your OpenAI or Azure OpenAI API keys are correctly set in the `.env` file
- **GraphQL Endpoint**: Verify the GraphQL endpoint is accessible from your environment
- **Docker Networking**: If using Docker, ensure port 8000 is not in use on your host machine

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT](LICENSE)