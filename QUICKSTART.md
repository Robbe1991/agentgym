# AgentGym - Quick Start Guide

## 🚀 Zum Weitermachen

### 1. Services Starten

**Terminal 1 - Backend:**
```bash
cd D:\projekte\AgentGym
python -m api.main
```
→ Backend läuft auf http://localhost:8001

**Terminal 2 - Frontend:**
```bash
cd D:\projekte\AgentGym\ui
npm run dev
```
→ Frontend läuft auf http://localhost:3000

### 2. System Testen

1. Browser öffnen: http://localhost:3000
2. "Scenarios" → "Start Training" auf Customer Support
3. "Training" → Live Metriken sehen
4. Warte ~2 Minuten → Episode counter steigt
5. "Models" → Trained models sehen

### 3. Development

**Tests laufen lassen:**
```bash
pytest tests/ -v
```

**Code checken:**
```bash
git status
git log --oneline -5
```

**Neue Branch für Features:**
```bash
git checkout -b feature/issue-19-evaluation
```

## 📋 Was ist fertig?

✅ Issues #1-18 (Core, Adapters, Scenarios, Frontend, Backend)
✅ 51 passing tests
✅ Full UI mit Dashboard, Scenarios, Training, Models, Settings
✅ FastAPI Backend mit REST endpoints
✅ Live training simulation

## 🎯 Next Steps (Week 3-4)

**Priorität 1:**
- Issue #19: Enhanced Evaluation (confusion matrices, cost tracking)
- Issue #20: Model Export/Import

**Priorität 2:**
- Issue #21-22: Documentation

## 🐛 Known Issues

Keine kritischen Bugs!

**Kleinigkeiten:**
- Models Import/Export buttons disabled (coming soon)
- Settings API keys in localStorage (nicht production-ready)
- WebSocket implementiert aber noch nicht genutzt

## 📚 Wichtige Files

**Backend:**
- `api/main.py` - Alle API endpoints (395 lines)

**Frontend:**
- `ui/src/api/client.js` - API client
- `ui/src/pages/Training.jsx` - Training page mit live data

**Core:**
- `agentgym/adapters/` - LangChain, AutoGen, CrewAI
- `agentgym/scenarios/` - Training scenarios

## 💡 Troubleshooting

**Frontend startet nicht?**
```bash
cd ui
npm install
npm run dev
```

**Backend startet nicht?**
```bash
pip install -r requirements.txt
pip install -r api/requirements.txt
python -m api.main
```

**Tests failen?**
```bash
pip install -e .
pytest tests/ -v
```

## 🔗 Links

- Session Report: `SESSION_REPORT.md`
- Roadmap: `docs/roadmap.md`
- GitHub: https://github.com/Robbe1991/agentgym

---

**Status:** Production-ready MVP! 🎉
**Next Session:** Enhanced Evaluation & Model Management
