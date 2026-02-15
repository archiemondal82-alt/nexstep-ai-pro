# 🚀 NexStep AI Pro - Professional Career Path Analyzer

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Google AI](https://img.shields.io/badge/Google_AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

A professional AI-powered career guidance platform that analyzes your skills, experience, and aspirations to provide personalized career recommendations with actionable insights.

## ✨ Key Features

### 🎯 Core Capabilities
- **AI-Powered Analysis**: Uses Google Gemini AI for intelligent career path recommendations
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
- **Customizable Settings**: Choose analysis depth (Quick/Standard/Deep)
- **Industry Filtering**: Target specific industries (Tech, Finance, Healthcare, etc.)
- **Location Preferences**: Tailor recommendations to Indian metro, tier-2, remote, or international roles

### 🎨 Professional UI/UX
- **Modern Design**: Deep blue gradient theme with glassmorphism effects
- **Animated Interface**: Smooth Lottie animations for enhanced user experience
- **Responsive Layout**: Works seamlessly on desktop and tablet devices
- **Interactive Charts**: Altair-powered visualizations for skill analysis
- **Progress Indicators**: Real-time feedback during AI processing

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone or Download the Project**
```bash
# If you have git
git clone <your-repo-url>
cd nexstep-ai-pro

# Or simply download and extract the ZIP file
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

4. **Configure API Key**

**Option A: Environment Variable (Recommended for production)**
```bash
# Copy template
cp .env.template .env

# Edit .env and add your API key
GOOGLE_API_KEY=your_actual_api_key_here
```

**Option B: In-App Configuration (Easier for testing)**
- Run the app (see step 5)
- Enter your API key in the sidebar under "🔑 API Configuration"

5. **Run the Application**
```bash
streamlit run nexstep_pro.py
```

6. **Access the App**
- Open your browser
- Navigate to `http://localhost:8501`
- Start analyzing your career path!

## 📖 User Guide

### How to Use

#### Step 1: Configure Settings
1. Open the sidebar (click `>` if collapsed)
2. Enter your Google API key in "API Configuration"
3. Select your preferred AI model
4. Adjust analysis depth and options

#### Step 2: Input Your Profile
**Method 1: Upload Resume**
- Click "📄 Upload Resume (PDF)"
- Select your resume file
- System automatically extracts text

**Method 2: Manual Entry**
- Select "✍️ Manual Entry"
- Type or paste your skills, experience, and qualifications
- Be detailed for better results

**Method 3: Load from History**
- Select "📜 Load from History"
- Choose a previous analysis
- Modify if needed

#### Step 3: Set Preferences
- **Preferred Industries**: Select target sectors
- **Career Stage**: Your current level (Entry/Mid/Senior/Executive)
- **Location**: Where you want to work

#### Step 4: Analyze
1. Click "🔮 Analyze Career Path"
2. Wait 30-60 seconds for AI processing
3. View your personalized recommendations

#### Step 5: Explore Results
- **Profile Summary**: Overview of your strengths
- **Career Paths**: Detailed recommendations with match scores
- **Skill Gaps**: Visual charts showing areas to improve
- **Next Steps**: Actionable tasks with timelines
- **Learning Path**: Specific courses to take
- **Interview Tips**: Preparation guidance

#### Step 6: Export or Save
- Click "📥 Export PDF" to download a professional report
- Your analysis is automatically saved to History

### Advanced Features

#### Analysis History
- Access via "📜 History" tab
- View all past analyses
- Load previous results
- Clear history when needed

#### Career Comparison
- Go to "⚖️ Compare" tab
- View side-by-side comparison of recommended paths
- Compare match scores, salaries, and skill requirements

#### Learning Resources
- Check "📚 Resources" tab
- Find curated learning platforms
- Discover job portals
- Access interview prep tools

## 🛠️ Technical Architecture

### Project Structure
```
nexstep-ai-pro/
├── nexstep_pro.py          # Main application
├── requirements.txt         # Dependencies
├── .env.template           # Environment variables template
├── README.md               # This file
└── .gitignore             # Git ignore rules
```

### Technology Stack
- **Frontend**: Streamlit
- **AI Engine**: Google Gemini (gemini-1.5-flash / gemini-pro)
- **PDF Processing**: PyMuPDF (fitz)
- **Data Visualization**: Altair
- **Export**: ReportLab (PDF generation)
- **Animations**: Streamlit-Lottie

### Key Components

#### Config Class
Manages API keys and configuration settings

#### AIHandler Class
Handles all AI operations:
- Model discovery
- Career advice generation
- Prompt engineering

#### PDFHandler Class
Extracts text from uploaded resumes

#### ExportHandler Class
Generates professional PDF reports

#### HistoryManager Class
Manages analysis history and session state

#### UIComponents Class
Handles custom CSS and styling

## 🔧 Configuration Options

### Analysis Depth
- **Quick**: 1 career path, basic analysis
- **Standard**: 2 career paths, detailed insights (default)
- **Deep**: 3 career paths, comprehensive analysis

### Optional Features (Toggle in Sidebar)
- ✅ Include Salary Trends
- ✅ Include Learning Roadmap
- ✅ Interview Preparation Tips

### Supported Industries
Technology | Finance | Healthcare | Education | Marketing | Consulting | Manufacturing | E-commerce | Government | Startup

### Career Stages
- Entry Level (0-2 years)
- Mid Level (3-7 years)
- Senior Level (8-15 years)
- Executive (15+ years)

### Location Options
- India - Metro Cities
- India - Tier 2 Cities
- India - Remote
- International Opportunities
- Flexible / Hybrid

## 📊 Sample Output

### Profile Summary
```
Versatile technology professional with 5 years of experience in full-stack 
development and emerging expertise in cloud architecture. Strong foundation 
in modern frameworks and agile methodologies.
```

### Career Recommendation Example
```
🎯 Senior Cloud Solutions Architect
Match Score: 87%
Salary Range: ₹18L - ₹30L (India Metro)

Why This Fits:
Your strong backend development skills combined with recent cloud 
certifications position you well for this high-demand role...

Skill Gap Analysis:
├── Python: 95% 🟢
├── AWS: 60% 🟡
├── Kubernetes: 45% 🟡
└── Leadership: 30% 🔴

Next Steps:
1. Complete AWS Solutions Architect Professional (3 months)
2. Build 2-3 production Kubernetes deployments (6 months)
3. Lead a small team project to develop leadership skills (ongoing)
```

## 🚨 Troubleshooting

### Common Issues

**1. "No models available" Error**
- ✅ Check your API key is correct
- ✅ Verify internet connection
- ✅ Try a different API key

**2. PDF Upload Not Working**
- ✅ Ensure PDF is text-based (not scanned images)
- ✅ File size should be < 10MB
- ✅ Try manual entry as alternative

**3. Analysis Takes Too Long**
- ✅ Normal processing: 30-60 seconds
- ✅ Check internet speed
- ✅ Try "Quick" analysis mode

**4. Export PDF Fails**
- ✅ Ensure ReportLab is installed: `pip install reportlab`
- ✅ Check write permissions in directory
- ✅ Try downloading again

**5. UI Not Loading Properly**
- ✅ Clear browser cache
- ✅ Refresh page (Ctrl+F5)
- ✅ Try different browser
- ✅ Update Streamlit: `pip install --upgrade streamlit`

### Error Messages

| Error | Solution |
|-------|----------|
| `API configuration error` | Check API key format and validity |
| `PDF extraction error` | Use manual entry or different PDF |
| `AI returned invalid format` | Try again or switch to different model |
| `Model fetch error` | Verify API key and internet connection |

## 🔒 Security & Privacy

### Data Handling
- ✅ **No data storage**: Analysis is session-based only
- ✅ **Local processing**: Your resume stays on your device
- ✅ **API encryption**: All AI requests use HTTPS
- ✅ **No tracking**: We don't collect personal information

### Best Practices
1. **Never share your API key** publicly
2. **Use environment variables** for API keys in production
3. **Don't commit `.env` files** to version control
4. **Review PDF content** before uploading sensitive information
5. **Clear history** after use on shared computers

## 🚀 Deployment

### Local Development
```bash
streamlit run nexstep_pro.py
```

### Streamlit Cloud (Free Hosting)
1. Push code to GitHub (exclude `.env`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add `GOOGLE_API_KEY` in Secrets section
5. Deploy!

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY nexstep_pro.py .
EXPOSE 8501
CMD ["streamlit", "run", "nexstep_pro.py"]
```

### Environment Variables for Production
```bash
# Set in your hosting platform
GOOGLE_API_KEY=your_key
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

## 🎯 Roadmap

### Current Version (v2.0)
- ✅ AI-powered career recommendations
- ✅ PDF resume upload
- ✅ Skill gap analysis
- ✅ PDF export
- ✅ Analysis history

### Planned Features (v2.1)
- 🔄 Multi-language support (Hindi, Bengali, etc.)
- 🔄 LinkedIn profile import
- 🔄 Job market trends integration
- 🔄 Networking recommendations
- 🔄 Resume builder tool

### Future Enhancements (v3.0)
- 📅 Career timeline visualization
- 📅 Mentorship matching
- 📅 Company culture fit analysis
- 📅 Salary negotiation tips
- 📅 Mobile app version

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit changes** (`git commit -m 'Add AmazingFeature'`)
4. **Push to branch** (`git push origin feature/AmazingFeature`)
5. **Open Pull Request**

### Contribution Guidelines
- Follow PEP 8 style guide
- Add comments for complex logic
- Test thoroughly before submitting
- Update documentation for new features

## 📄 License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2024 Anubhab Mondal

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

## 👨‍💻 Author

**Anubhab Mondal**
- Project: NexStep AI Pro
- Version: 2.0 (Professional Edition)
- Year: 2024

## 🙏 Acknowledgments

- **Google Gemini AI**: For powerful language models
- **Streamlit**: For amazing web framework
- **PyMuPDF**: For PDF processing capabilities
- **Altair**: For beautiful data visualizations
- **LottieFiles**: For smooth animations
- **Community**: For feedback and support

## 📞 Support

### Get Help
- 📧 Email: support@example.com
- 💬 Issues: [GitHub Issues](https://github.com/yourusername/nexstep-ai-pro/issues)
- 📚 Docs: [Full Documentation](https://docs.example.com)

### Useful Links
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Python Best Practices](https://peps.python.org/pep-0008/)

## 📈 Version History

### v2.0 (Current - Professional Edition)
- Complete refactor with modular architecture
- Added PDF export functionality
- Implemented analysis history
- Career comparison feature
- Enhanced UI/UX with animations
- Comprehensive error handling
- Production-ready code structure

### v1.0 (Original)
- Basic career analysis
- Simple PDF upload
- Skill visualization
- Initial AI integration

---

<div align="center">

**Built with ❤️ by Anubhab Mondal**

[⭐ Star this repo](https://github.com/yourusername/nexstep-ai-pro) | [🐛 Report Bug](https://github.com/yourusername/nexstep-ai-pro/issues) | [✨ Request Feature](https://github.com/yourusername/nexstep-ai-pro/issues)

</div>
