# 📖 Panduan Penggunaan Open WebUI

## Apa itu Open WebUI?

Open WebUI adalah platform AI workspace yang memungkinkan kamu berkomunikasi dengan berbagai model AI (seperti ChatGPT, Ollama, Claude, dll) melalui satu antarmuka web yang elegan. Mirip dengan ChatGPT, tapi kamu bisa:

- 🤖 Gunakan **model AI lokal** via Ollama (gratis, offline)
- 🌐 Koneksi ke **OpenAI**, **Google Gemini**, **Anthropic Claude**, dll
- 🔧 Tambahkan **custom API endpoint** (Groq, Together AI, Fireworks, dll)
- 🎨 **Generate gambar** via Hugging Face (gratis), DALL-E, Stable Diffusion
- 📚 **RAG (Retrieval Augmented Generation)** — chat dengan dokumen kamu
- 🛠️ **Tools & Functions** — buat plugin custom
- 👥 **Multi-user** — dukung banyak pengguna
- 🖼️ **Image Studio** — fitur khusus untuk generate gambar AI (fitur baru!)

---

## 🚀 Cara Menjalankan (Lokal)

### Prasyarat
- **Node.js** versi 18-22 (cek: `node --version`)
- **Python** versi 3.11 atau 3.12 (cek: `python --version`)
- **(Opsional)** Ollama untuk model AI lokal

### Langkah 1: Install Dependencies

```bash
# Frontend
npm install

# Backend
cd backend
pip install -r requirements.txt
cd ..
```

### Langkah 2: Setup Environment

Salin `.env.example` ke `.env` (sudah dilakukan), lalu edit sesuai kebutuhan:

```bash
# Untuk Ollama lokal
OLLAMA_BASE_URL='http://localhost:11434'

# Untuk OpenAI (opsional)
OPENAI_API_KEY='sk-xxxxxx'

# Untuk Hugging Face Image Generation (gratis!)
HUGGINGFACE_API_KEY='hf_xxxxxx'
```

### Langkah 3: Jalankan

**Terminal 1 — Backend:**
```bash
cd backend
# Windows:
start_windows.bat
# Atau manual:
uvicorn open_webui.main:app --port 8080 --reload
```

**Terminal 2 — Frontend:**
```bash
npm run dev
```

Buka browser: **http://localhost:5173**

---

## 🔑 Setup Pertama Kali

1. Buka http://localhost:5173
2. Klik **"Sign Up"** untuk membuat akun admin pertama
3. User pertama otomatis menjadi **Admin**
4. Masuk ke **Settings** untuk konfigurasi

---

## 🤖 Cara Connect ke AI Models

### Opsi 1: Ollama (Gratis, Lokal)

1. Install Ollama: https://ollama.ai
2. Download model:
   ```bash
   ollama pull llama3.1
   ollama pull mistral
   ollama pull codellama
   ```
3. Di Open WebUI, model akan otomatis terdeteksi
4. Pilih model dari dropdown dan mulai chat!

### Opsi 2: OpenAI API

1. Dapatkan API key dari https://platform.openai.com
2. Di Admin Panel → Settings → Connections
3. Masukkan OpenAI API Key
4. Model GPT-4, GPT-3.5, dll akan tersedia

### Opsi 3: Custom API Endpoint

Open WebUI mendukung **OpenAI-compatible API** apapun:

1. Admin Panel → Settings → Connections
2. Klik **"+"** untuk tambah koneksi baru
3. Masukkan:
   - **URL**: endpoint API (contoh: `https://api.groq.com/openai/v1`)
   - **API Key**: key dari provider
4. Simpan → model dari provider tersebut akan muncul

**Provider yang didukung:**
| Provider | URL | Gratis? |
|----------|-----|---------|
| Groq | `https://api.groq.com/openai/v1` | ✅ (rate limited) |
| Together AI | `https://api.together.xyz/v1` | 💰 (trial credit) |
| Fireworks | `https://api.fireworks.ai/inference/v1` | 💰 |
| OpenRouter | `https://openrouter.ai/api/v1` | ✅ (beberapa model) |
| Cerebras | `https://api.cerebras.ai/v1` | ✅ (rate limited) |
| Mistral | `https://api.mistral.ai/v1` | 💰 |
| Google AI | `https://generativelanguage.googleapis.com/v1beta/openai` | ✅ (Gemini) |

---

## 🎨 Image Studio (Fitur Baru!)

Image Studio adalah halaman khusus untuk generate gambar AI.

### Akses
Buka: **http://localhost:5173/image-studio**

### Fitur
- **Text-to-Image**: Tulis prompt → generate gambar
- **Multi-Engine Support**:
  - **Hugging Face Free** — gratis, berbagai model (SDXL, OpenJourney, dll)
  - **OpenAI DALL-E** — berbayar, kualitas tinggi
  - **AUTOMATIC1111** — lokal, butuh Stable Diffusion
  - **ComfyUI** — lokal, workflow kustom
  - **Ollama** — lokal, model multimodal
- **Gallery**: Lihat dan download semua gambar yang sudah di-generate

### Setup Hugging Face (Gratis!)

1. Daftar di https://huggingface.co (gratis)
2. Buat API token: https://huggingface.co/settings/tokens
3. Tambahkan ke `.env`:
   ```
   HUGGINGFACE_API_KEY='hf_xxxxxxxxxxxxxxxxxx'
   ```
4. Restart backend
5. Buka Image Studio → pilih engine "Hugging Face Free"
6. Pilih model (SDXL 1.0 rekomendasi) → tulis prompt → Generate!

**Model Gratis Tersedia:**
- Stable Diffusion XL 1.0 (terbaik)
- Stable Diffusion 1.5 (cepat)
- OpenJourney v4 (gaya Midjourney)
- Realistic Vision V5.1 (fotorealistik)
- Dreamlike Diffusion (artistik)
- FLUX.1-dev (terbaru)
- OpenDalle V1.1

### Load GGUF Model via Ollama

Untuk menggunakan model AI dari file GGUF:

1. Pastikan Ollama sudah terinstall
2. Buat Modelfile:
   ```
   FROM /path/to/your/model.gguf
   ```
3. Create model di Ollama:
   ```bash
   ollama create my-model -f Modelfile
   ```
4. Model akan muncul di Open WebUI

---

## 📚 Fitur-Fitur Utama

### Chat
- Chat dengan model AI apa saja
- Support markdown, code highlighting, LaTeX
- Copy, share, dan export chat

### Knowledge Base (RAG)
- Upload dokumen (PDF, DOCX, TXT, CSV, dll)
- Chat dengan dokumen kamu
- AI akan menjawab berdasarkan isi dokumen

### Workspace
- **Models**: Buat custom model dengan system prompt khusus
- **Tools**: Buat plugin/tools untuk AI (web search, calculator, dll)
- **Functions**: Buat pipeline processing kustom
- **Prompts**: Simpan template prompt yang sering digunakan

### Admin Panel
- Kelola pengguna (add, remove, change role)
- Monitor penggunaan
- Konfigurasi model dan koneksi
- Setup image generation
- Kelola knowledge bases

### Channels
- Real-time team chat dengan AI
- Kolaborasi multi-user

---

## ⚙️ Konfigurasi Lanjutan

### Database
Default: SQLite (di `backend/data/webui.db`)

Untuk production, gunakan PostgreSQL:
```env
DATABASE_URL=postgresql://user:pass@host:5432/openwebui
```

### Image Generation (Built-in)
Selain Image Studio, kamu juga bisa menggunakan image generation bawaan:

Admin Panel → Settings → Images:
- Enable Image Generation
- Pilih engine: OpenAI, ComfyUI, AUTOMATIC1111, atau Gemini
- Masukkan API key yang sesuai

### Web Search
AI bisa melakukan web search. Setup di Admin Panel → Settings → Web Search:
- DuckDuckGo (gratis, default)
- Google PSE
- Bing
- Brave
- SearXNG

### Audio (Text-to-Speech & Speech-to-Text)
Admin Panel → Settings → Audio:
- OpenAI Whisper
- Faster Whisper (lokal)
- Web Speech API (browser)

---

## 🐛 Troubleshooting

### Backend tidak bisa start?
- Pastikan Python 3.11/3.12 terinstall (bukan 3.13+)
- Coba `pip install -r requirements-slim.txt` untuk instalasi minimal
- Cek error log di terminal

### Frontend error?
- Pastikan `npm install` sukses
- Cek Node.js versi 18-22
- Jalankan `npm run check` untuk cek TypeScript errors

### Tidak bisa connect ke Ollama?
- Pastikan Ollama berjalan: `ollama list`
- Cek `OLLAMA_BASE_URL` di `.env`
- Default: `http://localhost:11434`

### Image generation error?
- Pastikan API key sudah diset
- Hugging Face model mungkin perlu loading pertama kali (tunggu 1-2 menit)
- Cek quota/rate limit

---

## 📝 Struktur Project

```
OpenWebUI/
├── src/                    # Frontend (SvelteKit)
│   ├── routes/             # Halaman-halaman
│   │   ├── (app)/          # App utama
│   │   │   ├── image-studio/  # 🆕 Image Studio
│   │   │   ├── c/          # Chat
│   │   │   ├── workspace/  # Workspace
│   │   │   └── admin/      # Admin panel
│   │   └── auth/           # Login/signup
│   └── lib/                # Komponen, API, stores
├── backend/                # Backend (Python FastAPI)
│   ├── open_webui/
│   │   ├── routers/        # API endpoints
│   │   │   ├── images.py   # Image generation
│   │   │   ├── image_studio.py  # 🆕 Image Studio API
│   │   │   ├── ollama.py   # Ollama proxy
│   │   │   ├── openai.py   # OpenAI proxy
│   │   │   └── ...
│   │   ├── models/         # Database models
│   │   ├── utils/          # Utilities
│   │   │   └── images/
│   │   │       └── huggingface.py  # 🆕 HF Integration
│   │   └── main.py         # FastAPI app
│   └── data/               # Data storage
├── .env                    # Environment config
├── DEPLOYMENT.md           # Panduan deploy
├── GUIDE.md                # Panduan ini
├── vercel.json             # Config Vercel
├── netlify.toml            # Config Netlify
├── railway.json            # Config Railway
└── render.yaml             # Config Render
```

---

## 🔗 Links Penting

- Open WebUI Docs: https://docs.openwebui.com
- Ollama: https://ollama.ai
- Hugging Face: https://huggingface.co
- OpenAI API: https://platform.openai.com
- GitHub Repo: https://github.com/athenas1337/OpenWebUI
