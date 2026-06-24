# ⚡ EnergyShield AI — Energy Supply Chain Resilience Platform
### ET AI Hackathon 2026 | Problem Statement 2

> **Turning geopolitical risk signals into executable procurement decisions — in minutes, not weeks.**

---

## 🎯 Problem

India imports **88% of its crude oil**, with 40–45% transiting the Strait of Hormuz. When the 2025 US-Iran standoff hit, Brent crude spiked 8% in a single session. India's Strategic Petroleum Reserves cover only **9.5 days** of national consumption. Traditional tools cannot model geopolitical disruption in real time, dynamically reroute procurement, or simulate cascading economic impacts.

**The gap:** Signal → Intelligence → Decision currently takes weeks. It needs to take minutes.

---

## 🚀 Solution — EnergyShield AI

A multi-agent AI platform that continuously monitors disruption signals, models scenarios, and generates executable procurement recommendations across India's energy supply chain.

```
SIGNAL INGESTION → RISK SCORING → SCENARIO MODELLING → PROCUREMENT REROUTING → DASHBOARD
      ↓                  ↓                ↓                      ↓                  ↓
  News/AIS/         Corridor Risk     Hormuz/Red Sea        Alternative        Geospatial
  Commodity          Index per         Disruption           Crude Sources       Command
   Feeds              Route            Simulations          + Tanker Ops        Centre
```

---

## 🤖 Agents

| Agent | Function |
|-------|----------|
| **GeoPolitical Sentinel** | Ingests live news, sanctions registries, commodity feeds → produces corridor disruption probability scores |
| **AIS Maritime Tracker** | Monitors vessel movements on Hormuz / Red Sea / Gulf of Aden corridors in near-real-time |
| **Disruption Scenario Modeller** | Simulates Hormuz closure, OPEC+ cuts, Red Sea suspension → cascading GDP/fuel/refinery impact |
| **Procurement Orchestrator** | Ranks alternative crude sources + routes by price, tanker availability, refinery grade compatibility |
| **SPR Optimiser** | Models optimal Strategic Petroleum Reserve drawdown under supply gap forecasts |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     EnergyShield AI Platform                    │
├──────────────┬──────────────┬───────────────┬───────────────────┤
│  Data Layer  │  Agent Layer │ Intelligence  │   Presentation    │
│              │              │    Layer      │      Layer        │
│ • NewsAPI    │ • GeoSentinel│ • Claude LLM  │ • Streamlit UI    │
│ • AIS Feeds  │ • AIS Tracker│ • Scenario    │ • Folium Maps     │
│ • Yahoo Fin. │ • Disruption │   Engine      │ • Plotly Charts   │
│ • OPEC APIs  │   Modeller   │ • RAG over    │ • Alert Dashboard │
│ • SPR Data   │ • Procurement│   Intel Docs  │ • PDF Reports     │
│              │   Agent      │               │                   │
│              │ • SPR Agent  │               │                   │
└──────────────┴──────────────┴───────────────┴───────────────────┘
```

---

## 📂 Repository Structure

```
energy-resilience-ai/
├── agents/
│   ├── geo_sentinel.py          # Geopolitical risk intelligence agent
│   ├── ais_tracker.py           # AIS maritime vessel tracking agent
│   ├── scenario_modeller.py     # Disruption scenario simulation agent
│   ├── procurement_agent.py     # Adaptive procurement orchestrator
│   └── spr_optimiser.py         # Strategic reserve optimisation agent
├── data/
│   ├── corridors.json           # Supply corridor definitions + risk baselines
│   ├── crude_sources.json       # Alternative crude supplier database
│   ├── refinery_specs.json      # Indian refinery grade compatibility matrix
│   └── spr_capacity.json        # SPR site capacities + current levels
├── utils/
│   ├── llm_client.py            # Anthropic Claude API wrapper
│   ├── news_fetcher.py          # Live news ingestion + summarisation
│   ├── commodity_feed.py        # Brent/WTI/shipping index feeds
│   └── report_generator.py      # PDF intelligence report generator
├── frontend/
│   └── app.py                   # Streamlit dashboard (main entry point)
├── config/
│   └── settings.py              # Configuration + environment variables
├── docs/
│   ├── architecture.png         # Architecture diagram
│   └── demo_script.md           # Demo video narration script
├── tests/
│   ├── test_agents.py
│   └── test_scenario_models.py
├── .env.example                 # Environment variable template
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Run

### 1. Clone
```bash
git clone https://github.com/Sam527627/energy-resilience-ai.git
cd energy-resilience-ai
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Add your API keys (Anthropic, NewsAPI)
```

### 4. Run the Platform
```bash
streamlit run frontend/app.py
```

---

## 🔑 API Keys Required

| Key | Source | Cost |
|-----|--------|------|
| `ANTHROPIC_API_KEY` | console.anthropic.com | Free tier available |
| `NEWS_API_KEY` | newsapi.org | Free tier (100 req/day) |

---

## 📊 Evaluation Metrics (Judging Criteria)

| Criterion | Our Approach | Weight |
|-----------|-------------|--------|
| **Innovation** | Multi-agent architecture with live data fusion; no existing tool does this for India's energy supply chain | 25% |
| **Business Impact** | Direct USD impact quantified per scenario; SPR drawdown decisions supported with 48hr lead time | 25% |
| **Technical Excellence** | LLM agents + real AIS/commodity data + geospatial visualisation | 20% |
| **Scalability** | Modular agent design; swap data sources without changing agent logic | 15% |
| **User Experience** | Single-screen command centre; one-click PDF report for decision-makers | 15% |

---

## 👤 Team

**Sambhav Kapoor**
ECE Graduate (Rank 1, CGPA 9.4) — MAIT Delhi 2026
Data Analytics | Machine Learning | Full-Stack Development

---

## 📄 License
MIT License — ET AI Hackathon 2026 Submission
