# 🚀 JobLess AI - Deployment Guide

## Deployment Options

### 1. Streamlit Community Cloud (Recommended - FREE)

**Advantages:**
- ✅ Free hosting
- ✅ Automatic HTTPS
- ✅ Easy updates via Git
- ✅ No server management
- ✅ No secrets needed — users bring their own API keys

**Steps:**

1. **Prepare Your Repository**
```bash
git init
git add .
git commit -m "Initial commit - JobLess AI"
git remote add origin https://github.com/YOUR_USERNAME/jobless-ai.git
git branch -M main
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
- Go to [share.streamlit.io](https://share.streamlit.io)
- Click "New app"
- Connect to your GitHub repository
- Set main file: **`jobless_ai_public.py`**
- Click "Deploy"

> No secrets/environment variables needed! Users paste their own free API keys directly in the app sidebar.

3. **Access Your App**
- Live at: `https://your-app-name.streamlit.app`

**Updates:** Just push to GitHub — app auto-updates!
```bash
git add .
git commit -m "Update description"
git push
```

---

### 2. Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY jobless_ai_public.py .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "jobless_ai_public.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t jobless-ai .
docker run -p 8501:8501 jobless-ai
```

---

### 3. Heroku Deployment

`Procfile`:
```
web: streamlit run jobless_ai_public.py --server.port=$PORT --server.address=0.0.0.0
```

```bash
heroku login
heroku create jobless-ai
git push heroku main
heroku open
```

---

### 4. AWS EC2 Deployment

```bash
# After SSH into your instance:
git clone https://github.com/YOUR_USERNAME/jobless-ai.git
cd jobless-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
nohup streamlit run jobless_ai_public.py --server.port=8501 --server.address=0.0.0.0 &
```

---

### 5. DigitalOcean App Platform

- Build Command: `pip install -r requirements.txt`
- Run Command: `streamlit run jobless_ai_public.py --server.port=$PORT`
- No environment variables needed (BYOK model)

---

## Security Checklist

- [ ] No API keys hardcoded in source
- [ ] `.env` (if used) is in `.gitignore`
- [ ] HTTPS enabled on your hosting platform
- [ ] Dependencies up to date: `pip install --upgrade -r requirements.txt`

---

## Cost Comparison

| Platform | Free Tier | Best For |
|----------|-----------|----------|
| Streamlit Cloud | 1 free app | Quick deployment ✅ |
| Heroku | 550 hours/month | Small projects |
| AWS EC2 | 750 hours/month (1 yr) | Full control |
| DigitalOcean | $0 trial credit | Simplicity |

---

## Recommended: Streamlit Cloud

For most users, Streamlit Cloud is the best option — free, easy, no secrets needed since JobLess AI uses a BYOK (Bring Your Own Key) model.

**Quick Deploy:**
1. Push to GitHub
2. Connect at share.streamlit.io
3. Set main file to `jobless_ai_public.py`
4. Deploy — done in 5 minutes! 🚀

---

**Built with ❤️ by Anubhab Mondal**
