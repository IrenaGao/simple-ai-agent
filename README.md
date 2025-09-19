# Multi-Agent Telemetry Visualizer

A comprehensive system for capturing, analyzing, and visualizing telemetry from multi-agent AI workflows. This system includes structured telemetry models, agent orchestration, React Flow visualization, and optimization recommendations.

## Features

- **Structured Telemetry**: Pydantic models for capturing detailed telemetry events
- **Multi-Agent Orchestration**: Agent A (orchestrator) can delegate to Agent B (summarizer/grader)
- **Diagram Analysis**: Agent D converts telemetry to React Flow diagrams
- **Synthetic Data**: Generate realistic telemetry for testing and demos
- **FastAPI Backend**: RESTful API for telemetry management and visualization
- **React Frontend**: Modern UI with React Flow for interactive diagrams
- **Optimization Insights**: Automated detection of performance bottlenecks and improvement opportunities

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agent A       │    │   Agent B       │    │   Agent D       │
│ (Orchestrator)  │───▶│ (Summarizer)    │    │ (Diagrammer)    │
│                 │    │                 │    │                 │
│ - Plans queries │    │ - Analyzes      │    │ - Converts      │
│ - Searches KB   │    │ - Summarizes    │    │   telemetry     │
│ - Delegates     │    │ - Grades        │    │ - Creates       │
│ - Emits events  │    │ - Emits events  │    │   React Flow    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Telemetry Store │
                    │                 │
                    │ - In-memory     │
                    │ - Event tracking│
                    │ - Run summaries │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   FastAPI       │
                    │                 │
                    │ - /api/run      │
                    │ - /api/telemetry│
                    │ - /api/health   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   React UI      │
                    │                 │
                    │ - Query form    │
                    │ - Flow diagram  │
                    │ - Telemetry     │
                    │ - Optimizations │
                    └─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- Anthropic API key
- Pinecone API key (optional, for KB search)

### 1. Backend Setup

```bash
# Clone and navigate to project
cd simple-ai-agent

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# ANTHROPIC_API_KEY=your_key_here
# PINECONE_API_KEY=your_key_here (optional)
# PINECONE_INDEX_NAME=your_index (optional)
# USE_LLM_DIAGRAMMER=false (for deterministic mode)

# Run the FastAPI server
python api_server.py
```

The API will be available at `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The React app will be available at `http://localhost:3000`

### 3. Test the System

1. Open `http://localhost:3000` in your browser
2. Enter a query like "How do I set up Intercom?"
3. Choose "Simulate" for synthetic data or "Run Live" for real agent execution
4. View the generated flow diagram and optimization suggestions

## API Endpoints

### Core Endpoints

- `POST /api/run/simulate` - Run simulation or live agent execution
- `GET /api/telemetry/{run_id}` - Get telemetry data for a specific run
- `GET /api/runs` - List all available runs
- `GET /api/health` - Health check

### Management Endpoints

- `POST /api/generate-sample-data` - Generate sample telemetry data
- `DELETE /api/telemetry/{run_id}` - Delete a specific run

## Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_index_name
PINECONE_NAMESPACE=kb-namespace
USE_LLM_DIAGRAMMER=false  # Use LLM for diagram analysis (default: false)
```

### Agent Configuration

The system supports two modes for diagram analysis:

1. **Deterministic Mode** (default): Fast, rule-based analysis without LLM calls
2. **LLM Mode**: More sophisticated analysis using Anthropic Claude

To enable LLM mode:
```bash
export USE_LLM_DIAGRAMMER=true
```

## Usage Examples

### Python API Usage

```python
from agents.orchestrator import OrchestratorAgent
from synthetic_telemetry import generate_sample_run
from agents.diagrammer import DiagrammerAgent

# Generate synthetic data
run = generate_sample_run(run_id="test-run")

# Run live orchestrator
orchestrator = OrchestratorAgent()
result = orchestrator.process_query("How do I set up Intercom?", "run-123")

# Analyze telemetry
diagrammer = DiagrammerAgent()
analysis = diagrammer.analyze_telemetry("run-123")
print(f"Generated {len(analysis.nodes)} nodes and {len(analysis.edges)} edges")
```

### API Usage

```bash
# Run simulation
curl -X POST "http://localhost:8000/api/run/simulate" \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I set up Intercom?", "simulate": true}'

# Get telemetry data
curl "http://localhost:8000/api/telemetry/run-123"

# Generate sample data
curl -X POST "http://localhost:8000/api/generate-sample-data?count=5"
```

## Testing

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_synthetic_telemetry.py
pytest tests/test_diagrammer.py

# Run with coverage
pytest --cov=. --cov-report=html
```

## Development

### Project Structure

```
simple-ai-agent/
├── agents/                 # Agent implementations
│   ├── orchestrator.py    # Agent A: Orchestrator
│   ├── summarizer.py      # Agent B: Summarizer/Grader
│   └── diagrammer.py      # Agent D: Diagrammer/Analyst
├── models/                # Pydantic models
│   └── telemetry.py       # Telemetry data models
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API services
│   │   └── App.jsx        # Main app component
│   └── package.json
├── tests/                 # Test files
├── tools/                 # Existing tools (Pinecone)
├── api_server.py          # FastAPI server
├── synthetic_telemetry.py # Synthetic data generator
├── telemetry_enhanced.py  # Enhanced telemetry utilities
└── requirements.txt       # Python dependencies
```

### Adding New Agents

1. Create agent class in `agents/` directory
2. Implement telemetry logging using `telemetry_enhanced.py`
3. Add agent type to `AgentType` enum in `models/telemetry.py`
4. Update orchestrator to use new agent if needed

### Adding New Telemetry Events

1. Create new event class inheriting from `TelemetryEvent`
2. Add event type to `EventType` enum
3. Update `telemetry_enhanced.py` with logging utilities
4. Update diagrammer to handle new event types

## Troubleshooting

### Common Issues

1. **API Connection Errors**: Ensure FastAPI server is running on port 8000
2. **Missing API Keys**: Check `.env` file has required environment variables
3. **React Build Errors**: Run `npm install` in frontend directory
4. **Import Errors**: Ensure all Python dependencies are installed

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Issues

- Use deterministic mode for diagram analysis (`USE_LLM_DIAGRAMMER=false`)
- Reduce synthetic data generation count for testing
- Check memory usage with large telemetry datasets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test files for usage examples
3. Open an issue on GitHub
