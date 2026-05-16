# ATP Match Predictor

A full-stack ML-powered tennis match prediction app with AI-generated analysis.

🎾 **Live Demo:** https://atp-match-predictor.vercel.app

## What it does

Enter any two ATP players, surface, tournament, and round — get an ML-powered win probability plus an AI-generated sports reporter analysis.

## How it works

1. **Data** — 116,000+ ATP matches loaded from Jeff Sackmann's dataset into PostgreSQL
2. **Features** — surface win rate, recent form, H2H, Elo ratings, ranking computed per player
3. **Model** — XGBoost trained on engineered features, 65.7% accuracy
4. **API** — FastAPI serves predictions via REST endpoints
5. **Narrative** — Claude API generates ESPN-style match previews from the stats
6. **Frontend** — React + Tailwind UI with autocomplete and animated results

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** PostgreSQL
- **ML:** XGBoost, scikit-learn, pandas
- **AI:** Anthropic Claude API
- **Frontend:** React, Tailwind CSS, Vite
- **Deploy:** Railway (backend + DB), Vercel (frontend)

## Architecture

React Frontend (Vercel) → FastAPI REST API (Railway) → PostgreSQL + XGBoost + Claude API

## Key Design Decisions

- **PostgreSQL over CSVs** — indexed queries on 116k rows in milliseconds vs loading 500MB per request
- **Elo ratings** — dynamic skill ratings outperform static ATP rankings as predictors
- **Offline training** — model trained once, saved as pkl, loaded at prediction time for millisecond inference
- **AI narrative** — Claude generates context-aware analysis from real statistical features, not generic text