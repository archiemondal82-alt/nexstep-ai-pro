# 🚀 NexStep AI Pro - Deployment Guide

## Deployment Options

### 1. Streamlit Community Cloud (Recommended - FREE)

**Advantages:**
- ✅ Free hosting
- ✅ Automatic HTTPS
- ✅ Easy updates via Git
- ✅ Built-in secrets management
- ✅ No server management

**Steps:**

1. **Prepare Your Repository**
```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/nexstep-ai-pro.git
git branch -M main
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
- Go to [share.streamlit.io](https://share.streamlit.io)
- Click "New app"
- Connect to your GitHub repository
- Select: `nexstep_pro.py` as main file
- Click "Advanced settings"
- Add secrets:
  ```toml
  GOOGLE_API_KEY = "your_api_key_here"
  ```
- Click "Deploy"!

3. **Access Your App**
- Your app will be live at: `https://your-app-name.streamlit.app`
- Share this URL with users

**Updates:**
Simply push to GitHub - app auto-updates!
```bash
git add .
git commit -m "Update description"
git push
```

---

### 2. Heroku Deployment

**Prerequisites:**
- Heroku account
- Heroku CLI installed

**Steps:**

1. **Create Required Files**

`Procfile`:
```
web: streamlit run nexstep_pro.py --server.port=$PORT --server.address=0.0.0.0
```

`setup.sh`:
```bash
mkdir -p ~/.streamlit/
echo "\
[general]\n\
email = \"your-email@example.com\"\n\
" > ~/.streamlit/credentials.toml
echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
```

2. **Deploy**
```bash
heroku login
heroku create nexstep-ai-pro
heroku config:set GOOGLE_API_KEY=your_api_key
git push heroku main
heroku open
```

---

### 3. Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY nexstep_pro.py .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app
ENTRYPOINT ["streamlit", "run", "nexstep_pro.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Build and Run:**
```bash
# Build image
docker build -t nexstep-ai-pro .

# Run container
docker run -p 8501:8501 \
  -e GOOGLE_API_KEY=your_api_key \
  nexstep-ai-pro

# Access at http://localhost:8501
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  nexstep:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    restart: unless-stopped
```

---

### 4. AWS EC2 Deployment

**Steps:**

1. **Launch EC2 Instance**
- Choose Ubuntu 22.04 LTS
- t2.micro (free tier eligible)
- Configure security group:
  - SSH (22) - Your IP
  - Custom TCP (8501) - Anywhere

2. **Connect and Setup**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3-pip python3-venv -y

# Clone repository
git clone https://github.com/YOUR_USERNAME/nexstep-ai-pro.git
cd nexstep-ai-pro

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export GOOGLE_API_KEY=your_api_key

# Run with nohup (keeps running after logout)
nohup streamlit run nexstep_pro.py --server.port=8501 --server.address=0.0.0.0 &
```

3. **Access**
- Visit: `http://your-ec2-public-ip:8501`

**Optional: Setup as Service**
```bash
sudo nano /etc/systemd/system/nexstep.service
```

Add:
```ini
[Unit]
Description=NexStep AI Pro
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/nexstep-ai-pro
Environment="GOOGLE_API_KEY=your_api_key"
ExecStart=/home/ubuntu/nexstep-ai-pro/venv/bin/streamlit run nexstep_pro.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable nexstep
sudo systemctl start nexstep
sudo systemctl status nexstep
```

---

### 5. DigitalOcean App Platform

1. **Connect Repository**
- Go to DigitalOcean App Platform
- Create new app
- Connect GitHub repository

2. **Configure**
- Build Command: `pip install -r requirements.txt`
- Run Command: `streamlit run nexstep_pro.py --server.port=$PORT`
- Add environment variable: `GOOGLE_API_KEY`

3. **Deploy**
- Click "Deploy"
- App will be live at provided URL

---

### 6. Google Cloud Run

**Prerequisites:**
- Google Cloud account
- gcloud CLI installed

**Steps:**

1. **Create `Dockerfile`** (see Docker section above)

2. **Deploy**
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud run deploy nexstep-ai-pro \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_api_key

# Get URL
gcloud run services describe nexstep-ai-pro --region us-central1
```

---

## Environment Variables

### Required
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Optional
```
APP_TITLE=NexStep AI Pro
APP_ICON=🚀
DEFAULT_THEME=dark
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

---

## Security Checklist

Before deploying to production:

- [ ] API key stored securely (not in code)
- [ ] `.env` file in `.gitignore`
- [ ] HTTPS enabled
- [ ] Rate limiting configured (if applicable)
- [ ] Error logging setup
- [ ] Backup strategy in place
- [ ] Update dependencies: `pip install --upgrade -r requirements.txt`

---

## Monitoring & Maintenance

### Logs
```bash
# Streamlit Cloud: Check dashboard
# Heroku: heroku logs --tail
# Docker: docker logs -f container_id
# EC2: tail -f nohup.out
```

### Updates
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
# (Method depends on deployment platform)
```

### Performance Tips
1. Use Streamlit caching: `@st.cache_data`
2. Optimize AI calls (avoid redundant requests)
3. Monitor API usage/costs
4. Set up CDN for static assets (if needed)

---

## Cost Comparison

| Platform | Free Tier | Cost (After Free) | Best For |
|----------|-----------|-------------------|----------|
| Streamlit Cloud | 1 free app | $0 | Quick deployment |
| Heroku | 550 hours/month | ~$7/mo | Small projects |
| AWS EC2 | 750 hours/month (1 year) | ~$5-10/mo | Full control |
| DigitalOcean | $0 trial credit | ~$5/mo | Simplicity |
| Google Cloud Run | 2M requests/month | Pay-per-use | Scalability |

---

## Troubleshooting Deployment

### Common Issues

**1. Port Binding Error**
```python
# Ensure using correct port
streamlit run nexstep_pro.py --server.port=$PORT
```

**2. Module Not Found**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**3. API Key Not Found**
```bash
# Check environment variable
echo $GOOGLE_API_KEY

# Set it
export GOOGLE_API_KEY=your_key
```

**4. Memory Issues**
```bash
# Increase Streamlit memory limit
streamlit run nexstep_pro.py --server.maxUploadSize=200
```

---

## Recommended: Streamlit Cloud

For most users, **Streamlit Cloud** is the best option:
- ✅ Free
- ✅ Easy
- ✅ Automatic updates
- ✅ No server management
- ✅ Built-in secrets

**Quick Deploy:**
1. Push to GitHub
2. Connect at share.streamlit.io
3. Add API key in Secrets
4. Deploy!

Done in 5 minutes! 🚀

---

## Support

Need help deploying?
- 📧 Email: support@example.com
- 💬 GitHub Issues
- 📚 [Streamlit Docs](https://docs.streamlit.io/streamlit-community-cloud)

---

**Built with ❤️ by Anubhab Mondal**
