# MyHomeServer

A modern, beautiful home automation dashboard built with React, Tailwind CSS, and MCP (Model Context Protocol) integration.

## 🚀 Overview

MyHomeServer is a comprehensive home automation control center that provides a unified interface for managing all your smart home devices. Built with modern web technologies and leveraging the power of MCP servers for seamless integration with various home automation systems.

## ✨ Features

### Core Functionality
- **📹 Camera Management**: Live camera feeds, PTZ controls, recording management
- **⚡ Energy Monitoring**: Smart plug control, energy analytics, cost tracking
- **🌤️ Weather Integration**: Local weather + Netatmo sensor data
- **🔔 Security Systems**: Ring doorbell, motion detection, event history
- **🏠 Smart Home Hub**: Nest devices, Home Assistant integration
- **🤖 AI Integration**: Local LLM for smart automation and insights

### Technical Highlights
- **Beautiful Dark UI**: Modern, professional dark theme designed for 24/7 monitoring
- **Real-time Updates**: Live data from all connected devices
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **MCP-Powered**: Leverages multiple MCP servers for robust device integration
- **Type-Safe**: Built with TypeScript for reliability and maintainability

## 🏗️ Architecture

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling (dark theme only)
- **React Query** for data fetching and caching
- **Lucide React** for consistent iconography
- **Vite** for fast development and building

### Backend
- **FastAPI** as minimal MCP proxy layer
- **MCP Servers** for device integration:
  - `tapo-camera-mcp` - Cameras and energy devices
  - `netatmo-mcp` - Weather sensors
  - `ring-mcp` - Security systems
  - `home-assistant-mcp` - Smart home hub
  - `local-llm-mcp` - AI assistance

### MCP Integration Strategy
```
┌─────────────────┐    ┌─────────────────┐
│   MyHomeServer  │────│   MCP Servers   │
│   (React UI)    │    │                 │
└─────────────────┘    │ • Tapo Camera   │
                       │ • Netatmo       │
┌─────────────────┐    │ • Ring          │
│   FastAPI Proxy │────│ • Home Assistant│
│   (Minimal)     │    │ • Local LLM     │
└─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
myhomeserver/
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API service layer
│   │   ├── types/         # TypeScript definitions
│   │   └── utils/         # Utility functions
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── backend/               # FastAPI proxy
│   ├── api/
│   │   ├── routes.py      # MCP proxy endpoints
│   │   └── middleware.py
│   ├── main.py
│   └── requirements.txt
├── docs/                  # Documentation
│   ├── README.md         # This file
│   ├── PRD.md           # Product Requirements
│   └── api/             # API documentation
└── shared/               # Shared types/config
```

## 🚀 Development Roadmap

### Phase 1: Foundation (Week 1)
- [ ] React + Vite project setup
- [ ] Tailwind CSS configuration (dark theme)
- [ ] Basic component library
- [ ] API client layer setup
- [ ] Layout system (sidebar, header)

### Phase 2: Camera Page (Week 2)
- [ ] Camera grid component
- [ ] Live video streaming
- [ ] PTZ controls
- [ ] Recording management
- [ ] Tapo MCP integration

### Phase 3: Energy Page (Week 3)
- [ ] Smart device grid
- [ ] Energy charts and analytics
- [ ] Device controls
- [ ] Cost tracking

### Phase 4: Weather Page (Week 4)
- [ ] Weather display components
- [ ] Netatmo sensor integration
- [ ] Local weather API
- [ ] Forecast display

### Phase 5: Security & Smart Home (Week 5)
- [ ] Ring doorbell interface
- [ ] Nest/Home Assistant integration
- [ ] Security event timeline
- [ ] Smart home automation

### Phase 6: AI Integration (Week 6)
- [ ] Local LLM integration
- [ ] Smart automation suggestions
- [ ] Voice commands
- [ ] Predictive insights

## 🛠️ Development Setup

### Prerequisites
- Node.js 18+
- Python 3.9+
- MCP servers running:
  - tapo-camera-mcp
  - netatmo-mcp
  - ring-mcp
  - home-assistant-mcp
  - local-llm-mcp

### Quick Start
```bash
# Clone and setup
git clone <repository-url>
cd myhomeserver

# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

## 📊 Key Metrics

- **Performance**: <2s page load times
- **Reliability**: 99.9% uptime with MCP fallbacks
- **Scalability**: Support for 100+ devices
- **Responsiveness**: Mobile-first design
- **Accessibility**: WCAG 2.1 AA compliance

## 🤝 Contributing

This project is in active development. See `docs/PRD.md` for detailed requirements and roadmap.

## 📄 License

This project is part of the Home Automation MCP ecosystem. See individual MCP server repositories for licensing information.

---

**Built with ❤️ for the smart home revolution**