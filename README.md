# Marketly

Marketly is a **full-stack stock portfolio web app** built with **Next.js (frontend)** and **Python FastAPI (backend)**.
It centralizes everything you need to track and analyze your investments: **financials, economic indicators, AI-driven analysis, and news** — all in one clean interface.

---

## 🚀 Features

* **Unified Dashboard** – View portfolio metrics, stock financials, and market data in one place.
* **AI Analysis** – GPT-powered insights to better understand companies and macroeconomic trends.
* **Live News** – Aggregated and filtered articles related to your portfolio.
* **Economic Data** – Key indicators and macro context to support investment decisions.
* **Modern Stack** – Built with Next.js, FastAPI, and Supabase for a smooth developer & user experience.

---

## 🛠️ Tech Stack

**Frontend (Next.js / TypeScript)**

* Next.js App Router
* TailwindCSS (planned)
* API integration via `lib/api.ts`

**Backend (Python / FastAPI)**

* FastAPI for routes & APIs
* Data fetching via `yfinance`, FMP, Finnhub, and other APIs
* GPT integration for stock analysis (`services/gpt.py`)

**Database & Infra**

* Supabase (Postgres, auth, storage)
* Planned: Redis caching

---

## 📂 Project Structure

### Backend (`/backend`)

```
backend/
├── app
│   ├── main.py              # FastAPI entrypoint
│   ├── routes/              # API routes (analysis, econ, financials, news)
│   └── services/            # Business logic & integrations
├── run.py                   # Dev server runner
├── company_financials.json  # Example stored data
```

### Frontend (`/frontend/src`)

```
frontend/src/
├── app/           # Next.js App Router
├── components/    # Reusable UI components
├── hooks/         # Custom React hooks
├── lib/           # API utils
├── types/         # Shared TypeScript types
```

---

## ⚡ Getting Started

### Prerequisites

* **Node.js** (>= 18)
* **Python** (>= 3.11, 3.13 recommended)
* **Supabase account** (if using DB features)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app will run at:

* **Frontend:** `http://localhost:3000`
* **Backend API:** `http://localhost:8000`

---

## 🤝 Contributing

This is an early-stage project. Contributions, ideas, and feedback are welcome!

---

## 📜 License

MIT License – feel free to use, modify, and share.

