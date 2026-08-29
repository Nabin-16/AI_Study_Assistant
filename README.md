# AI Study Assistant




## Pipeline

```
Study Material (PDF / Image / Text)
        │
        ├── .txt → read directly
        ├── .pdf → PyPDF2 text extraction
        └── .png/.jpg → EasyOCR text extraction
        │
        ↓
   Clean Study Text
        │
        ├── Summarize  → Groq LLM → Concise Summary
        ├── Q&A        → Groq LLM → Answer from Material
        └── Quiz       → Groq LLM → MCQs with Answers
        │
        ↓
   Streamlit App (interactive UI)
```

## Technologies

| Component | Technology |
|-----------|-----------|
| OCR | EasyOCR |
| LLM | Groq API (LLaMA 3.1 8B Instant) |
| PDF parsing | PyPDF2 |
| Web app | Streamlit |
| Language | Python 3.12 |

## Installation

### 1. Clone the repository

```bash
git clone <repo-url>
```

### 2. Create/activate conda environment or virtual environment 


### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up API key

Get a free API key from [console.groq.com](https://console.groq.com):

```bash
# Create .env file
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

## Running

### Streamlit App

```bash
streamlit run app.py
```

### Notebook (for testing individual components)

Open `notebooks/study_assistant.ipynb` in Jupyter.

## Project Structure

```
AI study assistant/
│
├── app.py                  # Streamlit web application
├── requirements.txt        # Python dependencies
├── .env.example            # API key template
├── .gitignore              # Git ignore rules
├── README.md           
│
├── src/                    # Source modules
│   ├── ocr.py              # EasyOCR text extraction
│   ├── text_extractor.py   # PDF and TXT text extraction
│   ├── summarizer.py       # Groq LLM summarization
│   ├── qa.py               # Groq LLM question answering
│   └── quiz.py             # Groq LLM quiz generation
│
├── study_assistant.ipynb   # notebook for testing
│
└── data/
    └── sample/             # Sample test files
        ├── sample_text.txt
        └── sample_img.png
        └── AI(syllabus).pdf
```