# Changelog

All notable changes to JobLess AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.0.0] - 2025 - JobLess AI (Major Rebrand & Multi-Provider Release)

### 🎉 Major Release — Rebrand + Multi-Provider AI

### Breaking Changes
- Project renamed from **NexStep AI Pro** → **JobLess AI**
- Main file renamed from `nexstep_pro.py` → `jobless_ai_public.py`
- Switched to **BYOK (Bring Your Own Key)** model — no `.env` required

### Added
- **Multi-Provider AI Support**: Google Gemini 🆓, Groq 🆓⚡, Cohere 🆓
  - All providers offer free tiers with no credit card required
  - Users select provider and paste key directly in the sidebar
- **Resume Builder Tab**: AI-assisted resume drafting
- **Mock Interview Tab**: Practice Q&A with AI feedback and scoring
- **Animated 3D Gyroscope Header**: Custom CSS/JS header animation
- **Provider-specific model selector**: Dynamic model list per provider
- **Privacy & Data Notice**: In-sidebar disclosure panel
- **API key helper buttons**: Direct links to each provider's key page

### Enhanced
- Sidebar redesigned with provider/model/key flow
- Session state extended for interview and resume builder features
- Footer updated with JobLess AI branding

### Removed
- Dependency on `.env` / `GOOGLE_API_KEY` environment variable
- `python-dotenv` dependency (no longer required)

---

## [2.0.0] - 2024-02-15 - NexStep AI Pro (Professional Edition)

### Added
- Modular architecture: Config, AIHandler, PDFHandler, ExportHandler, HistoryManager, UIComponents
- PDF export of career analysis reports
- Analysis history (up to 20 records)
- Career comparison tab
- Advanced settings (depth, toggles, industry filter, location, career stage)
- Enhanced AI prompts with learning roadmap and interview tips
- Resources tab with curated platforms and job portals
- Automated setup scripts (setup.sh / setup.bat)
- Comprehensive documentation

### Enhanced
- Tabbed interface, improved card designs, Lottie animations
- Skill gap Altair charts
- Comprehensive error handling

### Fixed
- JSON parsing errors, PDF extraction failures, session state issues

---

## [1.0.0] - 2024-01-15 - Initial Release

### Added
- Basic AI-powered career analysis using Google Gemini
- PDF resume upload and manual entry
- Career path recommendations with match scores
- Skill gap visualization (Altair)
- Indian salary range insights
- Custom CSS deep blue theme

---

## [Unreleased] - Future Plans

### Planned for v3.1.0
- [ ] Multi-language support (Hindi, Bengali, Tamil, etc.)
- [ ] LinkedIn profile import
- [ ] Job market trends integration
- [ ] More AI providers (OpenAI, Mistral, etc.)

### Planned for v4.0.0
- [ ] Career timeline visualization
- [ ] Mentorship matching platform
- [ ] Mobile app
- [ ] Job application tracker

---

**Maintained by Anubhab Mondal**
