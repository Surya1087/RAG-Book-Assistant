📚 RAG Book Assistant

A Retrieval-Augmented Generation (RAG) based AI assistant that allows users to upload PDF books and ask questions about their content.

The application uses **local Hugging Face embeddings** to create a vector database and **Mistral AI** to generate answers based on the retrieved document context.

 🚀 Features

- 📄 Upload PDF books directly through the Streamlit interface
- 🔍 Extract and split PDF content into smaller chunks
- 🧠 Generate embeddings using Hugging Face
- 💾 Store document embeddings locally using ChromaDB
- 🔎 Retrieve relevant document chunks using **MMR (Maximal Marginal Relevance)**
- 🤖 Generate answers using Mistral AI
- 💬 Interactive chat interface
- 🗂️ Support for multiple PDF documents
- ♻️ Prevent duplicate PDF processing using file hashing
- 🧹 Clear chat history
- 🔐 API keys stored securely using `.env`

 🏗️ Architecture

                ┌─────────────────┐
                │    PDF Upload   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │   PDF Loader    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Text Splitting  │
                │ Chunk Size:1000 │
                │ Overlap: 200    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Hugging Face    │
                │ Embeddings      │
                │ BGE-Small       │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │   ChromaDB      │
                │ Vector Store    │
                └────────┬────────┘
                         │
                         ▼
             ┌───────────────────────┐
             │   MMR Retrieval       │
             │ k = 4                 │
             │ fetch_k = 10          │
             └───────────┬───────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Mistral AI     │
                │  Codestral      │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │   Final Answer  │
                └─────────────────┘

🛠️ Tech Stack
 --------------------------------------------------------------------
| Technology             | Purpose                                   |
|------------------------|-------------------------------------------|
| Python                 | Programming language                      |
| Streamlit              | Web application interface                 |
| LangChain              | RAG application framework                 |
| Hugging Face           | Local text embeddings                     |
| BAAI/bge-small-en-v1.5 | Embedding model                           |
| ChromaDB               | Vector database                           |
| Mistral AI             | LLM for answer generation                 |
| PyPDF                  | PDF document loading                      |
| uv                     | Python package and environment management |
 --------------------------------------------------------------------

📂 Project Structure
RAG-Book-Assistant/
├── app.py
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── src/
    └── genai_part2_rag_implementation/
        └── __init__.py
        
⚙️ Installation
1. Clone the repository
git clone https://github.com/Surya1087/RAG-Book-Assistant.git
cd RAG-Book-Assistant

2. Create a virtual environment
python3 -m venv .venv
Activate it:
macOS / Linux
source .venv/bin/activate
Windows
.venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

🔑 Environment Variables
Create a .env file in the project root:
MISTRAL_API_KEY=your_mistral_api_key
The .env file is intentionally excluded from Git using .gitignore.

▶️ Run the Application
Start the Streamlit application:
streamlit run app.py
Streamlit will provide a local URL in the terminal.
Open the URL in your browser.

📖 How to Use
Step 1 — Upload a PDF
Upload a book or other PDF document using the file uploader.

Step 2 — Create the Vector Database
Click:
Create Vector Database

The application will:
1. Load the PDF
2. Extract the text
3. Split the text into chunks
4. Generate embeddings
5. Store the embeddings in ChromaDB

Step 3 — Ask Questions
After the document has been indexed, ask questions through the chat interface.
The application retrieves relevant sections from the uploaded documents and uses them as context for generating the answer.

🔎 Retrieval
The application uses MMR (Maximal Marginal Relevance) retrieval.
Current configuration:
search_kwargs={
    "k": 4,
    "fetch_k": 10,
    "lambda_mult": 0.5
}
MMR helps retrieve relevant information while reducing redundant chunks.

🧠 Embedding Model
The project uses:
BAAI/bge-small-en-v1.5
The embedding model runs locally through Hugging Face.
This means document embeddings do not require an OpenAI embedding API.
The same embedding model should be used when creating and querying the vector database.

🤖 Language Model
The application uses Mistral AI:
ChatMistralAI(
    model="codestral-2508"
)
The model receives the retrieved document context and generates the final response.

🗃️ Duplicate Document Detection
The application calculates a SHA-256 hash for every uploaded PDF.
This allows the application to detect whether the exact same PDF has already been added to the vector database.
Processed file information is stored locally in:
processed_files.json
This file is excluded from Git.

💾 Local Vector Database
ChromaDB stores the document embeddings locally in:
chroma_db/
The vector database is also excluded from Git because it is generated locally.

🔒 Security
API keys should be stored in .env:
MISTRAL_API_KEY=your_api_key
Never commit .env or expose API keys publicly.

The following files are excluded through .gitignore:
.env
.venv/
chroma_db/
processed_files.json
__pycache__/
.streamlit/secrets.toml

The local vector database and processed-file registry are created automatically when the application is used for the first time.

🔄 RAG Workflow
PDF
 ↓
Document Loading
 ↓
Text Splitting
 ↓
Embedding Generation
 ↓
ChromaDB
 ↓
User Question
 ↓
MMR Retrieval
 ↓
Relevant Context
 ↓
Mistral AI
 ↓
Generated Answer

🎯 Project Objective
The goal of this project is to build a document-based AI assistant that can understand and answer questions from uploaded books and PDF documents using Retrieval-Augmented Generation.
Instead of relying only on the language model's existing knowledge, the system retrieves relevant information from the user's documents and uses that information to generate responses.

👨‍💻 Author
Surya Pratap Singh
GitHub: Surya1087

📄 License
This project is intended for educational and learning purposes.
