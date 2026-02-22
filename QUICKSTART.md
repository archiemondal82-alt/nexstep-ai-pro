# ⚡ Quick Start Guide - JobLess AI

Get up and running in **5 minutes**!

## 📋 Prerequisites

- Python 3.8 or higher
- A free API key from **one** of these providers (pick any):
  - [Google Gemini](https://aistudio.google.com/app/apikey) — Free, 1500 req/day, no card
  - [Groq](https://console.groq.com/keys) — Free, ultra-fast inference, no card
  - [Cohere](https://dashboard.cohere.com/api-keys) — Free trial, no card

---

## 🚀 Installation (Choose Your Method)

### Method 1: Automated Setup (Recommended)

**Windows:**
```bash
setup.bat
```

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

### Method 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Run the Application

```bash
streamlit run jobless_ai_public.py
```

**Access the app at:** `http://localhost:8501`

---

## 🔑 Configure Your API Key (In-App — No .env needed!)

1. Open the sidebar (`>` button if collapsed)
2. Select your **AI Provider** (Gemini, Groq, or Cohere)
3. Click the **"Get [Provider] Key →"** button to open the key page
4. Paste your key into the key field
5. The app confirms **"✅ Key saved!"** and you're ready!

> Keys are stored only in your browser session — they're never saved to disk or sent anywhere except the AI provider you chose.

---

## 📝 First-Time Usage (60 seconds)

### Step 1: Pick a Provider & Model (10 seconds)
- **Groq** is fastest for quick results
- **Gemini** has the highest daily free limit
- **Cohere** is a solid alternative

### Step 2: Input Profile (20 seconds)
Choose ONE:
- **Upload Resume**: Click "Upload Resume" → Select PDF
- **Manual Entry**: Type skills & experience

Sample for testing:
```
Skills: Python, Machine Learning, Data Analysis
Experience: 3 years in software development
Education: B.Tech Computer Science
Certifications: AWS Solutions Architect
Projects: Built recommendation system for e-commerce
```

### Step 3: Set Preferences (10 seconds)
- Industries, Career Stage, Location

### Step 4: Analyze (20 seconds)
- Click **"🔮 Analyze Career Path"** and wait 30–60 seconds

---

## 🎯 What You'll Get

1. **Profile Summary** — strengths and core skills
2. **2–3 Career Recommendations** — match score, salary range, skill gap chart
3. **Action Plan** — next steps, learning resources, interview tips
4. **Export** — download a PDF report or compare careers side-by-side

---

## 🔧 Troubleshooting

| Problem | Fix |
|---------|-----|
| App won't start | `pip install -r requirements.txt --force-reinstall` |
| Key not working | Wait 30s after creating a new key, then retry |
| PDF won't upload | Use text-based PDF or switch to manual entry |
| Analysis too slow | Switch to Groq provider or use "Quick" mode |
| UI looks broken | Clear browser cache (Ctrl+F5) |

---

## 🎉 You're Ready!

```bash
source venv/bin/activate   # or venv\Scripts\activate on Windows
streamlit run jobless_ai_public.py
# Open http://localhost:8501 🚀
```

---

**Built with ❤️ by Anubhab Mondal** | Happy Career Planning! 🎯
