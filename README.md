# 🚀 JobLess AI - Professional Career Path Analyzer

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Google AI](https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logoColor=white)](https://console.groq.com/)
[![Cohere](https://img.shields.io/badge/Cohere-39594C?style=for-the-badge&logoColor=white)](https://cohere.com/)

A professional AI-powered career guidance platform that analyzes your skills, experience, and aspirations to provide personalized career recommendations with actionable insights. Bring your own free API key from Gemini, Groq, or Cohere — no paid subscription needed.

## ✨ Key Features

### 🎯 Core Capabilities
- **Multi-Provider AI**: Choose between Google Gemini, Groq (ultra-fast), or Cohere — all free tiers available
- **Multi-Input Support**: Upload resume (PDF) or manual skill entry
- **Personalized Recommendations**: Get 2-3 tailored career paths with match scores
- **Skill Gap Analysis**: Visual charts showing current proficiency vs. required skills
- **Salary Insights**: Realistic Indian salary ranges (LPA format)
- **Learning Roadmap**: Specific courses and certifications to bridge skill gaps
- **Interview Preparation**: Targeted tips for each career path

### 📊 Advanced Features
- **Analysis History**: Track and revisit past analyses (up to 20 records)
- **PDF Export**: Download professional reports of your analysis
- **Career Comparison**: Side-by-side comparison of recommended paths
- **Resume Builder**: AI-assisted resume creation tab
- **Mock Interview**: Practice interview questions with AI feedback
- **Customizable Settings**: Choose analysis depth (Quick/Standard/Deep)
- **Industry Filtering**: Target specific industries (Tech, Finance, Healthcare, etc.)
- **Location Preferences**: Tailor recommendations to Indian metro, tier-2, remote, or international roles

### 🎨 Professional UI/UX
- **Modern Design**: Deep blue gradient theme with glassmorphism effects
- **Animated Interface**: Smooth Lottie animations and a custom 3D gyroscope header
- **Responsive Layout**: Works seamlessly on desktop and tablet devices
- **Interactive Charts**: Altair-powered visualizations for skill analysis
- **Progress Indicators**: Real-time feedback during AI processing

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- A free API key from **one** of:
  - [Google Gemini](https://aistudio.google.com/app/apikey) — 1500 req/day, no card
  - [Groq](https://console.groq.com/keys) — ultra-fast inference, no card
  - [Cohere](https://dashboard.cohere.com/api-keys) — generous free trial, no card

### Installation

1. **Clone or Download the Project**
```bash
git clone <your-repo-url>
cd jobless-ai
```

2. **Create Virtual Environment** (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the Application**
```bash
streamlit run jobless_ai_public.py
```

5. **Access the App**
- Open your browser and navigate to `http://localhost:8501`
- Paste your free API key in the sidebar
- Start analyzing your career path!

## 📖 User Guide

### How to Use

#### Step 1: Configure Settings
1. Open the sidebar (click `>` if collapsed)
2. Select your **AI Provider** (Gemini, Groq, or Cohere)
3. Select your preferred **model**
4. Paste your **free API key** for that provider

#### Step 2: Input Your Profile
- **Upload Resume**: Click "📄 Upload Resume (PDF)"
- **Manual Entry**: Type or paste your skills, experience, and qualifications

#### Step 3: Set Preferences
- **Preferred Industries**, **Career Stage**, **Location**

#### Step 4: Analyze
1. Click "🔮 Analyze Career Path"
2. Wait 30–60 seconds for AI processing
3. View your personalized recommendations

#### Step 5: Explore Results
- **Profile Summary**, **Career Paths**, **Skill Gaps**, **Next Steps**, **Learning Path**, **Interview Tips**

#### Step 6: Export or Save
- Click "📥 Export PDF" to download a professional report
- Your analysis is automatically saved to History

### Advanced Features

#### Analysis History
- Access via "📜 History" tab — view, load, or clear past analyses

#### Career Comparison
- "⚖️ Compare" tab — side-by-side match scores, salaries, and skill requirements

#### Resume Builder
- "📝 Resume Builder" tab — AI-assisted resume drafting

#### Mock Interview
- "🎤 Mock Interview" tab — practice interview Q&A with AI feedback

## 🛠️ Technical Architecture

### Project Structure
```
jobless-ai/
├── jobless_ai_public.py    # Main application
├── requirements.txt         # Dependencies
├── setup.sh                # Unix setup script
├── setup.bat               # Windows setup script
├── README.md               # This file
├── QUICKSTART.md           # 5-minute setup guide
├── DEPLOYMENT.md           # Hosting guide
├── CONTRIBUTING.md         # Contribution guidelines
├── CHANGELOG.md            # Version history
└── API_KEY_GUIDE.md        # How to get free API keys
```

### Technology Stack
- **Frontend**: Streamlit
- **AI Providers**: Google Gemini · Groq · Cohere
- **PDF Processing**: PyMuPDF (fitz)
- **Data Visualization**: Altair
- **Export**: ReportLab (PDF generation)
- **Animations**: Streamlit-Lottie

## 🔧 Configuration Options

### Analysis Depth
- **Quick**: 1 career path, basic analysis
- **Standard**: 2 career paths, detailed insights (default)
- **Deep**: 3 career paths, comprehensive analysis

### Supported AI Providers
| Provider | Free Tier | Speed |
|----------|-----------|-------|
| Google Gemini 🆓 | 1500 req/day, no card | Fast |
| Groq 🆓⚡ | Generous limits, no card | Ultra-fast |
| Cohere 🆓 | Free trial, no card | Fast |

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key required" | Paste your key in the sidebar for the selected provider |
| PDF upload fails | Ensure PDF is text-based (not scanned); try manual entry |
| Analysis too slow | Try "Quick" mode or switch to Groq (fastest provider) |
| Export PDF fails | Ensure `reportlab` is installed: `pip install reportlab` |
| UI looks broken | Clear browser cache (Ctrl+F5) or try a different browser |

## 🔒 Security & Privacy

- ✅ **No data storage** — analysis is session-based only
- ✅ **API keys** are held in your browser session and cleared on tab close
- ✅ **Resume data** is sent only to the AI provider you select
- ✅ **No tracking** — JobLess AI does not collect personal information

## 🚀 Deployment

### Streamlit Cloud (Free)
```bash
# 1. Push to GitHub
git push origin main

# 2. Go to share.streamlit.io → New app
# 3. Set main file: jobless_ai_public.py
# 4. No secrets needed — users bring their own keys
# 5. Deploy!
```

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY jobless_ai_public.py .
EXPOSE 8501
CMD ["streamlit", "run", "jobless_ai_public.py"]
```

## 🎯 Roadmap

### Current Version (v3.0 — JobLess AI)
- ✅ Multi-provider AI (Gemini, Groq, Cohere)
- ✅ Resume Builder tab
- ✅ Mock Interview tab
- ✅ Animated 3D header
- ✅ BYOK (Bring Your Own Key) model
- ✅ PDF export & analysis history

### Planned (v3.1)
- 🔄 Multi-language support (Hindi, Bengali, etc.)
- 🔄 LinkedIn profile import
- 🔄 Job market trends integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

## 📄 License

MIT License — Copyright (c) 2025 Anubhab Mondal

## 👨‍💻 Author

**Anubhab Mondal**
- Project: JobLess AI
- Version: 3.0
- Year: 2025

## 🙏 Acknowledgments

Google Gemini · Groq · Cohere · Streamlit · PyMuPDF · Altair · LottieFiles

---

<div align="center">

**Built with ❤️ by Anubhab Mondal**

[⭐ Star this repo](https://github.com/archiemondal82-alt/nexstep-ai) | [🐛 Report Bug](https://github.com/archiemondal82-alt/nexstep-ai/issues) | [✨ Request Feature](https://github.com/archiemondal82-alt/nexstep-ai/issues)

</div>
