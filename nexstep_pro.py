"""
NexStep AI Pro - Public Version (Users Bring Their Own API Key)
Enhanced version with clear API key instructions
"""

import datetime
import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import json
import pandas as pd
import altair as alt
import requests
from streamlit_lottie import st_lottie
import os
from typing import Dict, List, Optional
import time
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# ==================== CONFIGURATION ====================


class Config:
    """Configuration manager for API keys and settings"""

    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY', '')

    def get_api_key(self) -> str:
        """Get API key from session"""
        if 'api_key' in st.session_state and st.session_state.api_key:
            return st.session_state.api_key
        return self.api_key

    def set_api_key(self, key: str):
        """Set API key in session"""
        st.session_state.api_key = key
        if key:
            try:
                genai.configure(api_key=key)
                return True
            except Exception as e:
                st.error(f"Invalid API key: {e}")
                return False
        return False

# ==================== AI HANDLER ====================


class AIHandler:
    """Handles all AI-related operations"""

    def __init__(self, config: Config):
        self.config = config

    def get_available_models(self) -> List[str]:
        """Fetch available Gemini models"""
        try:
            api_key = self.config.get_api_key()
            if not api_key:
                return []

            genai.configure(api_key=api_key)
            models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    models.append(m.name)
            return models if models else ["models/gemini-1.5-flash"]
        except Exception as e:
            return []

    def get_career_advice(self, input_text: str, model_name: str, context: Dict) -> Optional[Dict]:
        """Generate career advice using AI"""
        try:
            model = genai.GenerativeModel(model_name)

            prompt = f"""
            Act as an Elite Indian Career Strategist and AI Career Coach.
            
            **User Profile Analysis:**
            {input_text}
            
            **Context:**
            - Target Industries: {', '.join(context.get('industries', []))}
            - Career Stage: {context.get('career_stage', 'Not specified')}
            - Location Preference: {context.get('location', 'Flexible')}
            
            **Task:**
            Provide a comprehensive career analysis. Return ONLY a valid JSON object (no markdown, no code blocks) with this exact structure:
            
            {{
              "profile_summary": "A concise 2-sentence professional summary",
              "current_skills": ["Skill1", "Skill2", "Skill3"],
              "careers": [
                {{
                  "title": "Specific Job Title",
                  "match_score": 85,
                  "salary_range": "₹15L - ₹25L",
                  "reason": "Why this fits",
                  "skill_gap_analysis": {{"Python": 90, "Leadership": 40}},
                  "next_steps": ["Step 1", "Step 2"],
                  "learning_path": ["Course 1", "Course 2"],
                  "interview_tips": ["Tip 1", "Tip 2"]
                }}
              ]
            }}
            
            Suggest 2-3 distinct career paths. Return ONLY the JSON object.
            """

            response = model.generate_content(prompt)
            txt = response.text.strip()

            if '```json' in txt:
                txt = txt.split('```json')[1].split('```')[0].strip()
            elif '```' in txt:
                txt = txt.split('```')[1].split('```')[0].strip()

            return json.loads(txt)

        except Exception as e:
            st.error(f"⚠️ AI Error: {str(e)}")
            return None

# ==================== PDF HANDLER ====================


class PDFHandler:
    """Handles PDF operations"""

    @staticmethod
    def extract_text(uploaded_file) -> str:
        """Extract text from uploaded PDF"""
        try:
            pdf_bytes = uploaded_file.read()
            text = ""
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text()
            return text.strip()
        except Exception as e:
            st.error(f"PDF extraction error: {e}")
            return ""

# ==================== EXPORT HANDLER ====================


class ExportHandler:
    """Handles export operations"""

    @staticmethod
    def generate_pdf_report(analysis_data: Dict) -> Optional[io.BytesIO]:
        """Generate PDF report from analysis data"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            story.append(
                Paragraph("NexStep AI - Career Analysis Report", styles['Title']))
            story.append(Spacer(1, 12))

            story.append(
                Paragraph("<b>Profile Summary</b>", styles['Heading2']))
            story.append(Paragraph(analysis_data.get(
                'profile_summary', 'N/A'), styles['BodyText']))
            story.append(Spacer(1, 12))

            for idx, career in enumerate(analysis_data.get('careers', []), 1):
                story.append(
                    Paragraph(f"<b>Career Path {idx}: {career['title']}</b>", styles['Heading2']))
                story.append(
                    Paragraph(f"Match Score: {career['match_score']}%", styles['BodyText']))
                story.append(
                    Paragraph(f"Salary: {career['salary_range']}", styles['BodyText']))
                story.append(Spacer(1, 12))

            doc.build(story)
            buffer.seek(0)
            return buffer

        except Exception as e:
            st.error(f"PDF generation error: {e}")
            return None

# ==================== HISTORY MANAGER ====================


class HistoryManager:
    """Manages analysis history"""

    @staticmethod
    def add_to_history(input_text: str, analysis: Dict, context: Dict):
        """Add analysis to session history"""
        if 'history' not in st.session_state:
            st.session_state.history = []

        record = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            'summary': analysis.get('profile_summary', 'Analysis')[:50] + '...',
            'input_text': input_text[:500],
            'analysis': analysis,
            'context': context
        }

        st.session_state.history.append(record)
        if len(st.session_state.history) > 20:
            st.session_state.history = st.session_state.history[-20:]

# ==================== UI COMPONENTS ====================


class UIComponents:
    """UI styling and components"""

    @staticmethod
    def apply_custom_css(theme='dark'):
        """Apply custom CSS styling"""
        css = """
        <style>
            .stApp { 
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; 
                color: white !important; 
            }
            .api-banner {
                background: linear-gradient(90deg, #fbbf24 0%, #f59e0b 100%);
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 30px;
                border-left: 5px solid #f59e0b;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }
            .api-banner h3 {
                color: #1f2937 !important;
                margin-top: 0;
            }
            .api-banner p {
                color: #374151 !important;
            }
            .api-banner a {
                color: #1e40af !important;
                font-weight: bold;
            }
            @keyframes glowPulse {
                0% { filter: drop-shadow(0 0 5px rgba(0, 210, 255, 0.4)); }
                50% { filter: drop-shadow(0 0 20px rgba(0, 210, 255, 0.8)); }
                100% { filter: drop-shadow(0 0 5px rgba(0, 210, 255, 0.4)); }
            }
            .main-header {
                font-family: 'Arial Black', sans-serif; 
                font-size: 3.5rem !important;
                text-align: left; 
                color: #ffffff !important;
                animation: glowPulse 3s infinite ease-in-out;
                text-shadow: 2px 2px 10px rgba(0,0,0,0.5); 
                margin-bottom: 5px !important;
            }
            .result-card {
                background: rgba(255, 255, 255, 0.05) !important;
                backdrop-filter: blur(15px) saturate(180%) !important;
                border-radius: 20px !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                padding: 25px !important; 
                margin-bottom: 25px;
            }
            .stButton>button {
                background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%) !important;
                border-radius: 50px !important; 
                border: none !important; 
                color: white !important;
                font-weight: bold !important; 
            }
            h1, h2, h3 { color: #00d2ff !important; }
            p, li, span, label { color: #e2e8f0 !important; }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

    @staticmethod
    def show_api_setup_banner():
        """Show prominent API key setup instructions"""
        st.markdown("""
        <div class="api-banner">
            <h3>🔑 Setup Required: Get Your FREE Google API Key</h3>
            <p><strong>This app requires a Google Gemini API key to work. Don't worry - it's completely FREE!</strong></p>
            <p>
                1️⃣ Visit: <a href="https://makersuite.google.com/app/apikey" target="_blank">makersuite.google.com/app/apikey</a><br>
                2️⃣ Click "Create API Key" (takes 30 seconds)<br>
                3️⃣ Copy your key<br>
                4️⃣ Paste it in the sidebar → "🔑 API Configuration"
            </p>
            <p><strong>FREE tier includes:</strong> 60 requests/minute, 1500 requests/day - No credit card needed!</p>
        </div>
        """, unsafe_allow_html=True)

# ==================== MAIN APPLICATION ====================


def main():
    """Main application entry point"""

    st.set_page_config(
        page_title="NexStep AI Pro",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''

    # Initialize managers
    config = Config()
    ui = UIComponents()
    ai_handler = AIHandler(config)
    pdf_handler = PDFHandler()
    export_handler = ExportHandler()
    history_manager = HistoryManager()

    # Load animations
    def load_lottieurl(url):
        try:
            r = requests.get(url, timeout=3)
            if r.status_code != 200:
                return None
            return r.json()
        except:
            return None

    lottie_brain = load_lottieurl(
        "https://lottie.host/880ffc06-b30a-406d-a60d-7734e5659837/92k6e3z3tK.json")

    # Apply CSS
    ui.apply_custom_css()

    # ==================== SIDEBAR ====================
    with st.sidebar:
        if lottie_brain:
            st_lottie(lottie_brain, height=120, key="sidebar_brain")

        st.header("⚙️ Settings")

        # API Key Configuration - PROMINENT
        st.markdown("### 🔑 API Configuration")
        st.info("👆 **Required:** Enter your Google API key to use this app")

        api_key_input = st.text_input(
            "Google Gemini API Key",
            value=config.get_api_key(),
            type="password",
            help="Get your FREE key at: https://makersuite.google.com/app/apikey",
            placeholder="Paste your API key here..."
        )

        if api_key_input and api_key_input != config.get_api_key():
            if config.set_api_key(api_key_input):
                st.success("✅ API Key configured!")
                st.rerun()

        # Show Get API Key button
        st.markdown("""
        <a href="https://makersuite.google.com/app/apikey" target="_blank">
            <button style="background: #fbbf24; color: #1f2937; border: none; padding: 10px 20px; 
                           border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%;">
                🔑 Get FREE API Key →
            </button>
        </a>
        """, unsafe_allow_html=True)

        st.divider()

        # Model Selection (only if API key configured)
        if config.get_api_key():
            models = ai_handler.get_available_models()
            if models:
                selected_model = st.selectbox("🤖 AI Model", models, index=0)
            else:
                st.warning("⚠️ Check your API key")
                selected_model = None
        else:
            st.warning("⚠️ Configure API key above")
            selected_model = None

        # Advanced Options
        with st.expander("🎛️ Advanced Options"):
            analysis_depth = st.select_slider(
                "Analysis Depth",
                options=["Quick", "Standard", "Deep"],
                value="Standard"
            )
            include_learning_path = st.checkbox(
                "Include Learning Roadmap", value=True)
            include_interview_prep = st.checkbox(
                "Interview Preparation Tips", value=True)

        st.divider()

        # System Status
        if config.get_api_key():
            st.success(f"""
            **✅ Ready to Analyze**
            - Model: {selected_model.split('/')[-1] if selected_model else 'N/A'}
            - History: {len(st.session_state.history)} records
            """)
        else:
            st.error("**⚠️ API Key Required**\nConfigure above to start")

    # ==================== MAIN HEADER ====================
    st.markdown('<h1 class="main-header">🚀 NexStep AI Pro</h1>',
                unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size: 1.2rem; color: #94a3b8; margin-bottom: 2rem;">'
        'Transform your potential into a concrete career roadmap with AI-powered insights.'
        '</p>',
        unsafe_allow_html=True
    )

    # Show API Setup Banner if no key configured
    if not config.get_api_key():
        ui.show_api_setup_banner()
        st.info(
            "👈 **Next Step:** Enter your API key in the sidebar to start analyzing careers!")
        st.stop()

    # ==================== TABS ====================
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Career Analysis", "📜 History", "⚖️ Compare", "📚 Resources"])

    # ==================== TAB 1: CAREER ANALYSIS ====================
    with tab1:
        st.markdown("### 📋 Input Your Profile")

        col1, col2 = st.columns([2, 1])

        with col1:
            input_method = st.radio(
                "Choose input method:",
                ["📄 Upload Resume (PDF)", "✍️ Manual Entry"],
                horizontal=True
            )

            uploaded_file = None
            manual_skills = ""

            if input_method == "📄 Upload Resume (PDF)":
                uploaded_file = st.file_uploader(
                    "Upload your resume", type="pdf", key="resume_upload")
                if uploaded_file:
                    st.success(f"✓ Loaded: {uploaded_file.name}")

            else:
                manual_skills = st.text_area(
                    "Enter your skills, experience, and qualifications",
                    height=200,
                    placeholder="Example:\n- Programming: Python, JavaScript\n- Experience: 3 years data analysis\n- Education: B.Tech CS\n- Certifications: AWS"
                )

        with col2:
            st.markdown("#### 🎯 Preferences")
            target_industry = st.multiselect(
                "Preferred Industries",
                ["Technology", "Finance", "Healthcare", "Education"],
                default=["Technology"]
            )
            career_stage = st.selectbox(
                "Career Stage", ["Entry Level", "Mid Level", "Senior Level"])
            location_pref = st.selectbox(
                "Location", ["India - Metro", "India - Remote", "International"])

        st.markdown("---")

        analyze_btn = st.button("🔮 Analyze Career Path",
                                use_container_width=True, type="primary")

        if analyze_btn:
            if not selected_model:
                st.error("⚠️ Please configure your API key in the sidebar first!")
            else:
                raw_text = ""
                if uploaded_file:
                    with st.spinner("📖 Reading resume..."):
                        raw_text = pdf_handler.extract_text(uploaded_file)
                elif manual_skills:
                    raw_text = manual_skills

                if not raw_text:
                    st.error(
                        "⚠️ Please provide input via resume or manual entry.")
                else:
                    context = {
                        'industries': target_industry,
                        'career_stage': career_stage,
                        'location': location_pref,
                        'depth': analysis_depth,
                        'include_learning_path': include_learning_path,
                        'include_interview_prep': include_interview_prep
                    }

                    with st.spinner("🧠 AI is analyzing... (30-60 seconds)"):
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(i + 1)

                        data = ai_handler.get_career_advice(
                            raw_text, selected_model, context)
                        progress_bar.empty()

                    if data:
                        st.session_state.current_analysis = data
                        history_manager.add_to_history(raw_text, data, context)
                        st.success("✅ Analysis complete!")
                        st.balloons()

        # Display Results
        if st.session_state.current_analysis:
            data = st.session_state.current_analysis

            st.markdown("---")
            st.markdown("## 📊 Your Career Analysis")

            st.markdown(f"""
            <div class="result-card">
                <h3>📊 Profile Summary</h3>
                <p style="font-size: 1.1rem;">{data.get('profile_summary', 'N/A')}</p>
                <p><strong>Core Skills:</strong> {', '.join(data.get('current_skills', []))}</p>
            </div>
            """, unsafe_allow_html=True)

            careers = data.get('careers', [])
            if careers:
                st.markdown("### 🎯 Recommended Career Paths")

                for idx, job in enumerate(careers, 1):
                    with st.expander(f"**{idx}. {job['title']}** - Match: {job['match_score']}%", expanded=(idx == 1)):
                        col_job1, col_job2 = st.columns([2, 1])

                        with col_job1:
                            st.markdown(f"**💰 Salary:** {job['salary_range']}")
                            st.markdown(f"**📍 Why:** {job['reason']}")
                            st.markdown("**🎯 Next Steps:**")
                            for step in job.get('next_steps', []):
                                st.markdown(f"- {step}")

                        with col_job2:
                            gaps = job.get('skill_gap_analysis', {})
                            if gaps:
                                chart_data = pd.DataFrame({
                                    'Skill': list(gaps.keys()),
                                    'Proficiency': list(gaps.values())
                                })
                                c = alt.Chart(chart_data).mark_bar().encode(
                                    x=alt.X('Proficiency:Q',
                                            scale=alt.Scale(domain=[0, 100])),
                                    y=alt.Y('Skill:N', sort='-x'),
                                    color=alt.Color(
                                        'Proficiency:Q', scale=alt.Scale(scheme='blues'))
                                ).properties(height=200)
                                st.altair_chart(c, use_container_width=True)

    # Other tabs remain similar...
    with tab2:
        st.subheader("📜 Analysis History")
        if st.session_state.history:
            for idx, record in enumerate(reversed(st.session_state.history), 1):
                with st.expander(f"{idx}. {record['timestamp']}"):
                    st.markdown(f"**Summary:** {record['summary']}")
        else:
            st.info("No history yet!")

    with tab3:
        st.subheader("⚖️ Career Comparison")
        st.info("Compare career paths after analysis")

    with tab4:
        st.subheader("📚 Learning Resources")
        st.markdown(
            "- [Coursera](https://coursera.org)\n- [LinkedIn Learning](https://linkedin.com/learning)")

    # Footer
    st.markdown(f"""
        <div style="text-align: center; padding: 20px; color: #94a3b8;">
            © {datetime.date.today().year} NexStep AI Pro | Created by Anubhab Mondal
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
