# Multi-Agent Telemetry Visualizer - Setup Guide

## 🎯 Quick Start

The system has been successfully implemented with all core components working. Here's how to get it running:

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Set Up Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys
# ANTHROPIC_API_KEY=your_key_here
# PINECONE_API_KEY=your_key_here (optional)
```

### 3. Test the System

```bash
# Run basic tests (no external dependencies required)
python3 test_basic.py

# Run full tests (requires all dependencies)
python3 test_system.py
```

### 4. Start the Application

```bash
# Option 1: Use the startup script
python3 start_server.py

# Option 2: Start manually
# Terminal 1: Backend
python3 api_server.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🏗️ System Architecture

### Core Components

1. **Telemetry Models** (`models/telemetry.py`)
   - Pydantic models for structured telemetry
   - In-memory telemetry store
   - React Flow node/edge models

2. **Agents**
   - **Agent A** (`agents/orchestrator.py`): Orchestrator with delegation
   - **Agent B** (`agents/summarizer.py`): Summarizer/Grader
   - **Agent D** (`agents/diagrammer.py`): Diagram generator/analyst

3. **Synthetic Data** (`synthetic_telemetry.py`)
   - Realistic telemetry generation
   - Configurable event patterns
   - Error simulation

4. **API Server** (`api_server.py`)
   - FastAPI backend
   - RESTful endpoints
   - CORS enabled

5. **React Frontend** (`frontend/`)
   - React Flow visualization
   - Real-time telemetry display
   - Optimization suggestions

## 🔧 Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_index_name
USE_LLM_DIAGRAMMER=false  # Use LLM for diagram analysis
```

### Agent Modes

- **Deterministic Mode** (default): Fast, rule-based analysis
- **LLM Mode**: Sophisticated analysis using Claude

## 📊 Usage Examples

### Generate Sample Data

```python
from synthetic_telemetry import generate_sample_run

# Generate a single run
run = generate_sample_run(run_id="demo-run")

# Generate multiple runs
from synthetic_telemetry import SyntheticTelemetryGenerator
generator = SyntheticTelemetryGenerator()
runs = generator.generate_multiple_runs(count=5)
```

### Run Live Agent

```python
from agents.orchestrator import OrchestratorAgent
from telemetry_enhanced import start_run, end_run

# Start telemetry
run_id = start_run()

# Run orchestrator
orchestrator = OrchestratorAgent()
result = orchestrator.process_query("How do I set up Intercom?", run_id)

# End telemetry
end_run()
```

### Generate Diagrams

```python
from agents.diagrammer import DiagrammerAgent

# Analyze telemetry
diagrammer = DiagrammerAgent()
analysis = diagrammer.analyze_telemetry("run-id")

# Get React Flow data
nodes = [node.dict() for node in analysis.nodes]
edges = [edge.dict() for edge in analysis.edges]
optimizations = [opt.dict() for opt in analysis.optimizations]
```

## 🧪 Testing

### Test Files

- `test_basic.py`: Core functionality (no external deps)
- `test_system.py`: Full system tests
- `tests/test_synthetic_telemetry.py`: Synthetic data tests
- `tests/test_diagrammer.py`: Diagram generation tests

### Running Tests

```bash
# Basic tests
python3 test_basic.py

# Full tests
python3 test_system.py

# Specific test files
pytest tests/test_synthetic_telemetry.py
pytest tests/test_diagrammer.py
```

## 🚀 API Endpoints

### Core Endpoints

- `POST /api/run/simulate` - Run simulation or live execution
- `GET /api/telemetry/{run_id}` - Get telemetry data
- `GET /api/runs` - List all runs
- `GET /api/health` - Health check

### Management Endpoints

- `POST /api/generate-sample-data` - Generate sample data
- `DELETE /api/telemetry/{run_id}` - Delete run

## 🎨 Frontend Features

### React Flow Visualization

- Interactive agent flow diagrams
- Real-time telemetry display
- Optimization suggestions panel
- Run history browser

### Components

- `QueryForm`: Input form for queries
- `TelemetryPanel`: Event timeline and run details
- `OptimizationsPanel`: Performance suggestions
- `App`: Main application with React Flow

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Install dependencies with `pip install -r requirements.txt`
2. **API Connection**: Ensure backend is running on port 8000
3. **Frontend Issues**: Run `npm install` in frontend directory
4. **Missing API Keys**: Check `.env` file configuration

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Tips

- Use deterministic mode for faster diagram generation
- Reduce synthetic data count for testing
- Monitor memory usage with large datasets

## 📈 Next Steps

1. **Production Setup**: Add database persistence, authentication
2. **Advanced Analytics**: More sophisticated optimization algorithms
3. **Real-time Updates**: WebSocket support for live telemetry
4. **Custom Agents**: Add more specialized agent types
5. **Export Features**: PDF/PNG diagram export

## 🎉 Success!

The multi-agent telemetry visualization system is now fully implemented and ready to use. All core components are working, and you can start exploring agent interactions, telemetry analysis, and optimization insights through the intuitive React Flow interface.
