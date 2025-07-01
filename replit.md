# MuleSoft Documentation Generator

## Overview

The MuleSoft Documentation Generator is a Streamlit-based web application that automatically analyzes MuleSoft integration projects and generates comprehensive technical documentation. The application processes XML configuration files and DataWeave transformation scripts to create structured documentation using AI-powered analysis through Groq's LLM services.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application
- **UI Pattern**: Single-page application with progressive file upload and processing
- **State Management**: Streamlit session state for maintaining processed data across interactions
- **Configuration**: Streamlit config in `.streamlit/config.toml` for headless deployment

### Backend Architecture
- **Language**: Python 3.11
- **Design Pattern**: Modular utility-based architecture with specialized parsers and AI agents
- **Core Components**:
  - XML Parser for MuleSoft configuration files
  - DataWeave (DWL) parser for transformation scripts
  - Vector store for semantic search using FAISS
  - Multi-agent AI system using Autogen framework
  - Documentation generator for structured output

### AI Integration
- **Primary LLM**: Groq API with Llama3-8B model
- **Multi-Agent System**: Autogen framework with specialized agents:
  - Summarizer agent for technical summaries
  - Additional agents for specific documentation tasks
- **Embeddings**: HuggingFace sentence-transformers for semantic search

## Key Components

### 1. File Processing Pipeline
- **XML Parser** (`utils/xml_parser.py`): Extracts MuleSoft flows and sub-flows from XML configuration files
- **DWL Parser** (`utils/dwl_parser.py`): Analyzes DataWeave transformation scripts for input/output structures and logic
- **File Upload Handler**: Supports individual files and ZIP archives

### 2. Semantic Search System
- **Vector Store** (`utils/vector_store.py`): FAISS-based indexing for finding related components
- **Embeddings**: Uses sentence-transformers/all-MiniLM-L6-v2 for document embedding
- **Search Capabilities**: Semantic search across flows, components, and transformations

### 3. AI Documentation System
- **AI Agents** (`utils/ai_agents.py`): Multi-agent system for different documentation tasks
- **Documentation Generator** (`utils/documentation_generator.py`): Orchestrates content generation and formatting
- **Content Structure**: Generates markdown documentation with multiple sections

### 4. Main Application
- **Entry Point**: `mule_doc_app.py` - Streamlit application interface
- **Session Management**: Maintains state for processed files and generated documentation
- **Error Handling**: Comprehensive error reporting for file processing issues

## Data Flow

1. **File Upload**: Users upload MuleSoft XML files and/or DataWeave scripts
2. **Parsing**: XML and DWL parsers extract structured data from uploaded files
3. **Vector Indexing**: Processed data is indexed in FAISS vector store for semantic search
4. **AI Analysis**: Multi-agent system analyzes components and generates insights
5. **Documentation Generation**: Structured markdown documentation is created
6. **Output**: Users receive comprehensive project documentation

## External Dependencies

### Required Services
- **Groq API**: For LLM-powered analysis and documentation generation
- **HuggingFace**: For embedding models (sentence-transformers)

### Python Dependencies
- **Streamlit**: Web application framework
- **FAISS**: Vector similarity search
- **Autogen**: Multi-agent AI framework
- **LangChain**: For embedding integration
- **Groq**: API client for LLM services
- **Standard Libraries**: xml.etree.ElementTree, pandas, numpy

### Environment Variables
- `GROQ_API_KEY`: Required for AI-powered documentation generation

## Deployment Strategy

### Replit Configuration
- **Runtime**: Python 3.11 with Nix package management
- **Deployment Target**: Autoscale deployment
- **Port Configuration**: Application runs on port 5000
- **Entry Command**: `streamlit run app.py --server.port 5000`

### Workflow Configuration
- **Run Button**: Executes "Project" workflow
- **Service Command**: `streamlit run mule_doc_app.py --server.port 5000`
- **Port Monitoring**: Waits for port 5000 to be available

### Production Considerations
- Headless Streamlit configuration for server deployment
- Environment variable management for API keys
- Scalable architecture supporting multiple concurrent users

## Changelog

```
Changelog:
- June 19, 2025. Initial setup
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```