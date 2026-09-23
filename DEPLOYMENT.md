# 🚀 Panduan Deployment Open WebUI

## Arsitektur

Open WebUI adalah aplikasi **full-stack**:
- **Frontend**: SvelteKit (di-build menjadi static SPA)
- **Backend**: Python FastAPI (butuh server persistent)

> ⚠️ **PENTING**: Tidak bisa deploy 100% di Vercel/Netlify saja. Backend butuh server terpisah.

---

## Opsi 1: Railway (Rekomendasi - Paling Mudah)

### Langkah-langkah:
1. Buat akun di [railway.app](https://railway.app)
2. Connect GitHub repository `athenas1337/OpenWebUI`
3. Railway akan otomatis detect `Dockerfile` dan `railway.json`
4. Set environment variables:
   ```
   WEBUI_SECRET_KEY=<random-string>
   OPENAI_API_KEY=<your-key>  (opsional)
   HUGGINGFACE_API_KEY=<your-key>  (opsional)
   ```
5. Deploy! Railway akan build Docker image dan jalankan

### Biaya:
- Trial: $5 credit gratis
- Hobby: $5/bulan
- Pro: $20/bulan

---

## Opsi 2: Render

### Langkah-langkah:
1. Buat akun di [render.com](https://render.com)
2. New → Blueprint → Connect `athenas1337/OpenWebUI`
3. Render akan membaca `render.yaml` dan setup otomatis:
   - Web service dengan Docker
   - PostgreSQL database
   - Persistent disk 10GB
4. Set secret environment variables di dashboard

### Biaya:
- Free tier: tersedia (tapi terbatas)
- Starter: $7/bulan

---

## Opsi 3: Hybrid (Frontend di Vercel + Backend di Railway)

### Frontend (Vercel):
1. Fork/push repo ke GitHub
2. Di Vercel, import project
3. Settings:
   - Framework Preset: SvelteKit
   - Build Command: `npm run build`
   - Output Directory: `build`
4. Environment Variables:
   ```
   WEBUI_BACKEND_URL=https://your-backend.railway.app
   ```

### Backend (Railway/Render/VPS):
1. Deploy backend saja dengan Dockerfile
2. Pastikan CORS dikonfigurasi untuk domain Vercel kamu

> ⚠️ Metode hybrid lebih rumit dan butuh konfigurasi CORS + WebSocket proxy tambahan.

---

## Opsi 4: Docker di VPS

### Cara termudah:
```bash
# Di VPS (Ubuntu/Debian)
docker run -d \
  -p 3000:8080 \
  -v open-webui:/app/backend/data \
  -e OPENAI_API_KEY=your-key \
  -e HUGGINGFACE_API_KEY=your-key \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

### Atau build sendiri:
```bash
git clone https://github.com/athenas1337/OpenWebUI.git
cd OpenWebUI
docker build -t open-webui .
docker run -d -p 3000:8080 -v open-webui:/app/backend/data open-webui
```

---

## Opsi 5: Lokal (Development)

### Prerequisites:
- Node.js 18-22
- Python 3.11 atau 3.12
- (Opsional) Ollama untuk model AI lokal

### Frontend:
```bash
npm install
npm run dev
# Buka http://localhost:5173
```

### Backend:
```bash
cd backend
pip install -r requirements.txt
# Windows:
start_windows.bat
# Atau manual:
uvicorn open_webui.main:app --port 8080 --reload
```

---

## Environment Variables Penting

| Variable | Deskripsi | Default |
|----------|-----------|---------|
| `OLLAMA_BASE_URL` | URL Ollama server | `http://localhost:11434` |
| `OPENAI_API_KEY` | API key OpenAI | (kosong) |
| `OPENAI_API_BASE_URL` | Custom OpenAI endpoint | (kosong) |
| `HUGGINGFACE_API_KEY` | HF API key (gratis) | (kosong) |
| `WEBUI_SECRET_KEY` | JWT signing secret | (auto-generated) |
| `DATABASE_URL` | Database connection | `sqlite:///data/webui.db` |
| `PORT` | Server port | `8080` |
| `CORS_ALLOW_ORIGIN` | CORS origins | `*` |

---

## Push ke GitHub

```bash
git add .
git commit -m "Initial commit: Open WebUI with Image Studio"
git branch -M main
git remote add origin https://github.com/athenas1337/OpenWebUI.git
git push -u origin main
```
