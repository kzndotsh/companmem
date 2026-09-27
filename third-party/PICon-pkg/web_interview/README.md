# Human Interview Web Application

This is a web-based interface for conducting human interviews as part of the interrogation evaluation research.

## Architecture

- **Frontend**: Next.js + React + Tailwind CSS (deployed on Vercel)
- **Backend**: FastAPI + Python (deployed on Railway/Render)

## Project Structure

```
├── frontend/              # Next.js frontend application
│   ├── src/app/
│   │   ├── page.tsx       # Landing page (name entry)
│   │   ├── interview/
│   │   │   └── page.tsx   # Interview chat interface
│   │   └── layout.tsx     # Root layout
│   └── package.json
├── api/
│   ├── index.py           # FastAPI backend
│   └── requirements.txt   # Python dependencies
├── src/
│   └── env/
│       └── web_interrogation_env.py  # Web-compatible interview env
└── vercel.json            # Vercel deployment config
```

## Deployment

### Frontend (Vercel)

1. Connect your GitHub repo to Vercel
2. Set the following in Vercel project settings:
   - **Root Directory**: (leave empty, uses repo root)
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Output Directory**: `frontend/.next`
   - **Framework**: Next.js
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: URL of your backend (e.g., `https://your-app.railway.app`)

### Backend (Railway)

1. Create a new Railway project
2. Deploy from GitHub, select the `api/` directory
3. Set environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key (for GPT-5)
   - `GOOGLE_CLAIM_SEARCH`: Google Custom Search API key
   - `GOOGLE_CX_ID`: Google Custom Search Engine ID
   - `GOOGLE_GEOCODE`: Google Geocode API key
4. Railway will auto-detect FastAPI and deploy

### Alternative: Run Backend Locally

```bash
# Install dependencies
pip install -r api/requirements.txt

# Run the FastAPI server
cd api
uvicorn index:app --reload --port 8000
```

## Local Development

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
pip install -r api/requirements.txt
uvicorn api.index:app --reload
```

## Interview Flow

1. **Start**: User enters their name → Creates session
2. **Predefined Questions** (10): Demographic questions from WVS
3. **Main Interrogation** (50 turns): AI-generated follow-up questions
4. **Repeat Phase** (10): Re-asking predefined questions for consistency check
5. **Complete**: Results saved and evaluated

## Fixed Parameters (Human Interview)

- `model`: gpt-5
- `nhd_model`: gpt-5
- `num_sessions`: 1
- `num_turns`: 50

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/start` | POST | Start new interview (requires `name`) |
| `/api/respond` | POST | Submit response, get next question |
| `/api/results/{session_id}` | GET | Get final results |
| `/api/session/{session_id}` | DELETE | Cancel session |
