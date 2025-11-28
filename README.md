# Voice_Agent

**Voice_Agent** is a real-time **voice-enabled RAG system** using:

- **LiveKit Agents** → bi-directional audio streaming  
- **Deepgram STT/TTS** → speech recognition + output  
- **Google Gemini Flash 2.5** → reasoning + function-calling  
- **Full RAG pipeline** (PDF → chunking → embeddings → FAISS → retrieval)  
- **FAISS Vector Store** for similarity search  
- **SentenceTransformers** for embeddings  

The agent answers questions only about Airbnb knowledge extracted from PDFs and can guide the user through the process of making a reservation.

This backend integrates seamlessly with the official LiveKit React starter frontend:  
https://github.com/livekit-examples/agent-starter-react

---

#  Features

- Real-time conversational voice assistant  
- Automatic PDF ingestion → chunking → embeddings  
- RAG-powered responses retrieved from FAISS  
- End-to-end booking dialogues (name, check-in, check-out)  
- Function-calling for reservation workflow  
- Intelligent refusal for non-Airbnb questions  
- Fully compatible with LiveKit Web, React, and mobile clients

---

#  RAG: How It Works

The RAG pipeline performs:

### **1. PDF Ingestion**
All PDFs inside `/knowledge/` are loaded.

### **2. Text Extraction**
Using PyPDF2, each PDF is converted to raw text.

### **3. Chunking**
Documents are split into manageable segments (≈350 characters).

### **4. Embeddings**
Each chunk is converted into a vector using SentenceTransformers.

### **5. Vector Index (FAISS)**
A FAISS L2 index is built for similarity search.

### **6. RAG Answer Construction**
Query → embedding → FAISS search → context retrieval.

---

#  Voice Agent Architecture

```
User Speech
   ↓
Deepgram STT
   ↓
Gemini Flash 2.5 (LLM)
   ↓
   – Uses RAG lookup tool
   – Uses booking tool
   – Filters irrelevant questions
   ↓
Deepgram TTS
   ↓
User Hears Response
```

---

#  Project Structure

```
Voice_Agent/
│
├── Main.py						# Voice Agent Logic
├── rag_engine.py               # RAG Logic
├── knowledge/
│    └── airbnb_knowledge.pdf   # RAG based data 
│
├── .env				  # Environment variables
├── README.md
└── agent-starter-react   # (LiveKit React starter)
```

---

#  Setup Instructions

## 1. Clone repository
```bash
git clone https://github.com/AhmedKamel200058/Voice_Agent_With_RAG.git
cd Voice_Agent_With_RAG
```

## 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### **3. Download model files**
```bash
python agent.py download-files
```

## 4. Create `.env` file
```
LIVEKIT_URL=ws://your-livekit-server
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret

GOOGLE_API_KEY=your_gemini_key
DEEPGRAM_API_KEY=your_deepgram_key
```

## 5. Add PDFs
Place all knowledge PDFs inside `/knowledge/`.


### 6. Setup frontend**
```bash
cd agent-starter-react
npm install
npm run dev
```

Frontend will be available at:
```
http://localhost:3000
```

---

## 7. Running the Agent

Start backend:
```bash
python Main.py start
```

Start frontend:
```bash
npm run dev
```

---
#  Agent Features

- RAG responses based only on PDF knowledge  
- Full booking dialogue  
- Topic filtering for unrelated questions  
- Real-time voice conversations  

---

#  Demo
https://drive.google.com/file/d/1xB4hpLhUY4J4nSfkd9Act40cTuqyL9qo/view?usp=sharing


---

#  License
MIT License.
