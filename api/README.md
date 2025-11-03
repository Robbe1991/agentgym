# AgentGym API

FastAPI backend for the AgentGym UI, providing REST API endpoints and WebSocket support for real-time training updates.

## Features

- **REST API Endpoints**: Complete API for scenarios, training sessions, models, and settings
- **WebSocket Support**: Real-time training updates via WebSocket connections
- **CORS Enabled**: Configured for frontend integration on localhost:3000
- **Integration Ready**: Seamlessly integrates with AgentGym Python backend

## Installation

Install FastAPI dependencies:

```bash
pip install -e ".[cloud]"
```

Or install from the api requirements:

```bash
pip install -r api/requirements.txt
```

## Running the API Server

Start the API server on port 8000:

```bash
# From the project root
python -m api.main

# Or with uvicorn directly
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (Alternative documentation)

## API Endpoints

### Scenarios

- `GET /api/scenarios` - List all available training scenarios
- `GET /api/scenarios/{scenario_id}` - Get details for a specific scenario

### Training

- `POST /api/training/start` - Start a new training session
- `GET /api/training/{session_id}` - Get training session status
- `GET /api/training` - List all training sessions
- `POST /api/training/{session_id}/pause` - Pause a training session
- `POST /api/training/{session_id}/resume` - Resume a paused session
- `POST /api/training/{session_id}/stop` - Stop and save a training session

### Models

- `GET /api/models` - List all trained models
- `GET /api/models/{model_id}` - Get model details
- `DELETE /api/models/{model_id}` - Delete a trained model

### Settings

- `GET /api/settings` - Get current settings
- `PUT /api/settings` - Update settings

### WebSocket

- `WS /ws/training/{session_id}` - Real-time training updates

## Example Usage

### Start a Training Session

```python
import requests

response = requests.post("http://localhost:8000/api/training/start", json={
    "scenario_id": "customer_support",
    "framework": "LangChain",
    "max_episodes": 200,
    "learning_rate": 0.001
})

session_id = response.json()["session_id"]
print(f"Training session started: {session_id}")
```

### Get Training Status

```python
import requests

session_id = "session_1_1234567890"
response = requests.get(f"http://localhost:8000/api/training/{session_id}")
status = response.json()

print(f"Episode {status['current_episode']}/{status['max_episodes']}")
print(f"Accuracy: {status['accuracy']:.2f}%")
```

### WebSocket Real-time Updates

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/training/session_1_1234567890')

ws.onmessage = (event) => {
  const update = JSON.parse(event.data)
  console.log('Training update:', update)
}
```

## Integration with UI

The API is configured to work with the React frontend running on `http://localhost:3000`. The Vite proxy is set up to forward `/api` requests to the FastAPI backend.

### Frontend Configuration

In `ui/vite.config.js`:

```javascript
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

## Development

### Auto-reload

Run with auto-reload for development:

```bash
uvicorn api.main:app --reload --port 8000
```

### Interactive API Documentation

Visit http://localhost:8000/docs to see the interactive API documentation where you can test all endpoints.

## Architecture

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **WebSocket**: Real-time bidirectional communication
- **CORS**: Cross-Origin Resource Sharing for frontend integration
- **Async/Await**: Asynchronous request handling for better performance

## Next Steps

- Connect React frontend to API endpoints
- Implement database persistence (currently in-memory)
- Add authentication and authorization
- Implement actual training integration with AgentGym scenarios
- Add model export/import functionality
- Set up production deployment configuration
