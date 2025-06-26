# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a dual-component Vietnamese nail salon system consisting of:

1. **Backend API** (FastAPI + LangGraph): Intelligent chatbot with knowledge base integration for appointment booking and customer service
2. **Admin Dashboard** (Next.js): Management interface for appointments, services, and knowledge base documents

The chatbot operates in Vietnamese and integrates OpenAI GPT-4o-mini with custom tools for scheduling, knowledge base search, and customer management.

## Key Commands

### Backend (chatbot/)
```bash
# Development setup
uv sync                           # Install dependencies via uv package manager
python init_data.py              # Initialize database with sample services and time slots
python run.py                    # Start FastAPI server with auto-reload (port 8080)

# Testing and debugging
python test_chatbot.py           # Test chatbot functionality
python create_test_appointments.py  # Create sample appointments for demo
python integration_test.py       # Full system integration test
python test_upload.py            # Test knowledge base upload endpoint

# API health check
curl http://localhost:8080/api/v1/health
```

### Frontend (admin/)
```bash
# Development
npm install                      # Install dependencies
npm run dev                      # Start Next.js dev server (port 3000)
npm run build                    # Build for production
npm run lint                     # Run ESLint
```

### Full System Startup
```bash
# Terminal 1: Backend
cd chatbot && python run.py

# Terminal 2: Frontend  
cd admin && npm run dev

# Access points:
# - Chatbot: http://localhost:8080/chat
# - Admin Dashboard: http://localhost:3000/dashboard
# - API Documentation: http://localhost:8080/docs
```

## Architecture

### Backend Agent Architecture
The system uses **LangGraph ReAct agent pattern** with these critical components:

- **Agent State**: `add_messages` reducer for conversation history management
- **Tools**: Database interaction functions + `search_knowledge_base` for document retrieval
- **Memory**: `MemorySaver` with thread-based conversation persistence
- **Vietnamese System Prompt**: Defines nail salon assistant behavior in Vietnamese

### Database Schema Integration
**Unified SQLite database** serving both chatbot and admin dashboard:

**Core Booking System:**
- `Service`: Nail services (price, duration, Vietnamese names)
- `TimeSlot`: Auto-generated appointment slots with availability tracking
- `Appointment`: Customer bookings with status management (`scheduled` → `checked-in` → `serving` → `completed`)

**Knowledge Base System:**
- `KnowledgeDocument`: File metadata, processing status, Vietnamese content
- `DocumentChunk`: Searchable text chunks for efficient retrieval
- `ChatSession`/`ChatMessage`: Conversation tracking with `message_metadata` (renamed from `metadata` to avoid SQLAlchemy conflicts)

### API Architecture
- **Chat API** (`/api/v1/chat`): Main conversational interface with conversation threading
- **Admin API** (`/api/v1/admin/*`): CRUD operations for appointments, services, timeslots
- **Knowledge API** (`/api/v1/knowledge/*`): Document upload, processing, and search
- **Frontend Integration**: Admin dashboard consumes backend APIs with real-time updates

### Knowledge Base Integration
- **File Processing**: Supports PDF, DOCX, DOC, TXT with async processing via `aiofiles`
- **Document Chunking**: Automatic text extraction and chunking for search optimization
- **Agent Integration**: `search_knowledge_base` tool allows chatbot to reference uploaded documents
- **Vietnamese Language**: Full Vietnamese support in responses and document content

## Critical Implementation Details

### Agent Error Handling
The agent uses **graceful degradation** - if OpenAI API key is missing, it returns helpful Vietnamese error messages instead of crashing:

```python
# Agent initialization with fallback
if not api_key or api_key == "your_openai_api_key_here":
    return None  # Triggers Vietnamese error response in chat endpoint
```

### Database Session Management
- **Context Managers**: All database operations use `SessionLocal()` context managers
- **Auto-generated Time Slots**: Time slots are created on-demand when queried for dates without existing slots
- **Status Synchronization**: Appointment status changes automatically update time slot availability

### Conversation Threading
- **Thread Persistence**: Each chat uses `conversation_id` for thread-based memory via LangGraph
- **Concurrent Sessions**: Multiple customers can have simultaneous conversations
- **Vietnamese Context**: System prompt ensures all responses maintain Vietnamese language and cultural context

### Frontend-Backend Integration
- **Real-time Updates**: Admin dashboard uses fetch APIs with loading states and error handling
- **CORS Configuration**: Backend configured for `allow_origins=["*"]` to support frontend integration
- **Connection Status**: Frontend components display backend connectivity status and provide retry mechanisms

## Environment Configuration

### Required Environment Variables
```bash
OPENAI_API_KEY=your_actual_openai_api_key    # GPT-4o-mini access
DATABASE_URL=sqlite:///./nail_salon.db       # SQLite path (default)
```

### Package Management
- **Backend**: Uses `uv` for fast Python dependency management with `pyproject.toml`
- **Frontend**: Standard npm with Next.js 15.3.3 and React 19
- **Python**: Requires Python >=3.13

### Critical Dependencies
- **LangChain**: Version 0.3.x for agent compatibility
- **LangGraph**: Version 0.4.x for ReAct agent pattern
- **SQLAlchemy**: Version 2.0+ with proper `metadata` attribute handling
- **Document Processing**: `PyPDF2`, `python-docx`, `aiofiles` for async file handling

## Debugging Common Issues

### SQLAlchemy Metadata Conflicts
If you encounter `Attribute name 'metadata' is reserved`, check for column names conflicting with SQLAlchemy's reserved attributes. Use `message_metadata` instead of `metadata`.

### Agent Initialization Failures
1. Verify `OPENAI_API_KEY` in `.env` file
2. Check LangChain version compatibility (0.3.x required)
3. Restart server after environment changes

### File Upload Issues
1. Ensure `uploads/documents/` directory exists
2. Check file type validation (PDF, DOCX, DOC, TXT only)
3. Verify `python-multipart` and `aiofiles` are installed
4. Test upload endpoint directly: `python test_upload.py`

### Frontend-Backend Connection
1. Verify backend is running on port 8080
2. Check CORS configuration in `app/main.py`
3. Use browser dev tools to inspect network requests
4. Test with standalone drag-drop: `test_drag_drop.html`

### Database Reset
```bash
# If database becomes corrupted or schema changes
rm nail_salon.db
python init_data.py
python create_test_appointments.py
```

This system requires both components running simultaneously for full functionality - the admin dashboard manages content that the chatbot uses for customer interactions.