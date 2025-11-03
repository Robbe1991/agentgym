# AgentGym UI

Modern React frontend for the AgentGym AI agent training platform.

## Features

- **Dashboard**: Overview of training sessions, models, and metrics
- **Scenarios**: Browse and select training scenarios
- **Training**: Monitor active training sessions with real-time metrics
- **Models**: View and manage trained agent models
- **Settings**: Configure frameworks, LLM providers, and training parameters

## Tech Stack

- **React 18** - UI framework
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Beautiful icons
- **Recharts** - Chart library (for future use)

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server (runs on port 3000)
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
ui/
├── src/
│   ├── components/
│   │   └── Layout.jsx        # Main layout with sidebar
│   ├── pages/
│   │   ├── Dashboard.jsx     # Dashboard page
│   │   ├── Scenarios.jsx     # Scenarios browser
│   │   ├── Training.jsx      # Training monitor
│   │   ├── Models.jsx        # Model management
│   │   └── Settings.jsx      # Settings page
│   ├── App.jsx              # Main app with routing
│   ├── main.jsx             # React entry point
│   └── index.css            # Global styles with Tailwind
├── index.html               # HTML entry point
├── vite.config.js           # Vite configuration
├── tailwind.config.js       # Tailwind configuration
└── package.json             # Dependencies
```

## API Integration

The frontend is configured to proxy API requests to `http://localhost:8000` (FastAPI backend).

To connect to a different backend, update the proxy settings in `vite.config.js`.

## Contributing

This UI is part of the AgentGym project. See the main README for contribution guidelines.

## Next Steps

- Issue #16: Enhanced Training Dashboard with real-time charts
- Issue #17: Advanced Scenario Browser with filtering
- Issue #18: FastAPI backend integration
