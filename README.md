# 💎 Jewelry Inventory System

## Description

A modern, lightweight application to manage, catalog, and analyze a jewelry store’s inventory. Built with Python, FastAPI, and SQLModel, this system offers:

- Photo upload & processing
- Voice note transcription to metadata
- AI-powered auto-tagging
- Search, filter, and CRUD inventory management
- Statistics dashboard
- Clean, mobile-friendly admin interface

## Features

✅ CRUD operations for jewelry items  
✅ Image validation & thumbnail generation  
✅ Voice-to-text transcription using Whisper  
✅ AI tagging (CLIP + GPT-4)  
✅ Dockerized deployment with CI/CD

## Tech Stack

- **Backend:** Python 3.11, FastAPI
- **Database:** SQLModel (SQLite in dev, PostgreSQL for prod)
- **Frontend:** Jinja2 templates + Tailwind CSS
- **Media Handling:** Pillow
- **AI:** Whisper, CLIP, GPT-4 APIs
- **Deployment:** Docker, Fly.io
- **CI/CD:** GitHub Actions

## Setup

1️⃣ Clone this repo  
2️⃣ Install dependencies with Poetry  
3️⃣ Run the app:  
```bash
poetry shell
bash run.sh
