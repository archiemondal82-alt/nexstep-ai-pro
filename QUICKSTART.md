# ⚡ Quick Start Guide - NexStep AI Pro

Get up and running in **5 minutes**!

## 📋 Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one FREE here](https://makersuite.google.com/app/apikey))

---

## 🚀 Installation (Choose Your Method)

### Method 1: Automated Setup (Recommended)

**Windows:**
```bash
# Double-click setup.bat
# OR run in Command Prompt:
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

# 4. Create .env file
cp .env.template .env
```

---

## 🔑 Configure API Key

### Option A: Environment Variable (Recommended)
1. Edit `.env` file
2. Replace `your_api_key_here` with your actual API key
3. Save the file

### Option B: In-App Configuration
1. Run the app first (see next section)
2. Click sidebar `>` button
3. Expand "🔑 API Configuration"
4. Paste your API key
5. It's saved for your session!

---

## ▶️ Run the Application

```bash
# Make sure virtual environment is activated
streamlit run nexstep_pro.py
```

**Access the app:**
- Open browser automatically OR
- Go to: `http://localhost:8501`

---

## 📝 First-Time Usage (60 seconds)

### Step 1: Configure (10 seconds)
- Enter API key in sidebar (if not in .env)
- Select AI model (default is fine)

### Step 2: Input Profile (20 seconds)
Choose ONE:
- **Upload Resume**: Click "Upload Resume" → Select PDF
- **Manual Entry**: Type skills & experience
- **Sample Data**: Use this for testing
  ```
  Skills: Python, Machine Learning, Data Analysis
  Experience: 3 years in software development
  Education: B.Tech Computer Science
  Certifications: AWS Solutions Architect
  Projects: Built recommendation system for e-commerce
  ```

### Step 3: Set Preferences (10 seconds)
- Industries: Technology, Finance (default is fine)
- Career Stage: Select yours
- Location: India - Metro Cities

### Step 4: Analyze (20 seconds)
- Click "🔮 Analyze Career Path"
- Wait 30-60 seconds
- View your personalized recommendations!

---

## 🎯 What You'll Get

After analysis, you'll see:

1. **Profile Summary**
   - Your professional strengths
   - Core skills identified

2. **2-3 Career Recommendations**
   - Match score (how well it fits)
   - Salary range (Indian market)
   - Why this career suits you
   - Skill gap analysis (visual chart)

3. **Action Plan**
   - Next steps with timelines
   - Learning resources
   - Interview preparation tips

4. **Export Options**
   - Download PDF report
   - Save to history
   - Compare careers

---

## 💡 Tips for Best Results

### Resume Upload
- ✅ Use text-based PDF (not scanned images)
- ✅ Include: skills, experience, education, projects
- ✅ Keep file size under 10MB
- ✅ Detailed resume = better recommendations

### Manual Entry
- ✅ Be specific: "Python, Django, PostgreSQL"
- ✅ Include years: "3 years experience"
- ✅ Mention projects: "Built ML model for XYZ"
- ✅ Add certifications: "AWS Certified"
- ✅ State goals: "Want to transition to data science"

### Settings
- 🎯 **Quick Analysis**: 1 career, fast results
- 🎯 **Standard**: 2 careers, balanced (recommended)
- 🎯 **Deep**: 3 careers, comprehensive insights

---

## 🔧 Troubleshooting

### App Won't Start
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Try different port
streamlit run nexstep_pro.py --server.port 8502
```

### "No Models Available"
- ✅ Check API key is correct
- ✅ Verify internet connection
- ✅ Try pasting key again

### PDF Won't Upload
- ✅ Ensure PDF is text-based
- ✅ Try manual entry instead
- ✅ Check file size < 10MB

### Analysis Takes Too Long
- ✅ Normal time: 30-60 seconds
- ✅ Check internet speed
- ✅ Try "Quick" mode

### UI Looks Broken
- ✅ Clear browser cache (Ctrl+F5)
- ✅ Try different browser
- ✅ Update Streamlit: `pip install --upgrade streamlit`

---

## 📚 Next Steps

After your first analysis:

1. **Export Report**
   - Click "📥 Export PDF"
   - Download professional report
   - Share with mentors/advisors

2. **Explore History**
   - Go to "📜 History" tab
   - View past analyses
   - Track your progress

3. **Compare Careers**
   - Check "⚖️ Compare" tab
   - See side-by-side comparison
   - Make informed decisions

4. **Find Resources**
   - Visit "📚 Resources" tab
   - Discover learning platforms
   - Explore job portals

---

## 🎓 Sample Queries to Try

**For Beginners:**
```
Skills: HTML, CSS, JavaScript basics
Education: BCA second year
Goal: Want to become a web developer
```

**For Mid-Career:**
```
Skills: Java, Spring Boot, Microservices, AWS
Experience: 5 years backend development
Looking for: Senior roles or career change
```

**For Career Changers:**
```
Current: Mechanical Engineer, 3 years experience
Learning: Python, Data Analysis
Goal: Transition to data science
```

---

## 🚀 Ready to Deploy?

Want to share with others? Check out:
- `DEPLOYMENT.md` - Full deployment guide
- Streamlit Cloud - Free hosting
- Takes 5 minutes to deploy!

---

## 🆘 Need Help?

- 📖 Full docs: `README.md`
- 🚀 Deployment: `DEPLOYMENT.md`
- 💬 Issues: [GitHub Issues](#)
- 📧 Email: support@example.com

---

## 🎉 You're Ready!

Start analyzing your career path in **3 commands**:

```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
streamlit run nexstep_pro.py
# Open http://localhost:8501 and enjoy! 🚀
```

---

**Built with ❤️ by Anubhab Mondal**

Happy Career Planning! 🎯
