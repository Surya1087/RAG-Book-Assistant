import streamlit as st
from dotenv import load_dotenv
import tempfile
import os
import hashlib
import json

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="RAG Book Assistant",
    page_icon="📚",
    layout="centered"
)


# ============================================================
# CACHE EMBEDDING MODEL
# ============================================================

@st.cache_resource
def get_embeddings():

    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )


# ============================================================
# CACHE MISTRAL MODEL
# ============================================================

@st.cache_resource
def get_llm():

    return ChatMistralAI(
        model="codestral-2508"
    )


# ============================================================
# FILE HASH
# ============================================================

def get_file_hash(file_path):

    with open(file_path, "rb") as f:

        return hashlib.sha256(
            f.read()
        ).hexdigest()


# ============================================================
# LOAD EMBEDDINGS
# ============================================================

embeddings = get_embeddings()


# ============================================================
# STREAMLIT UI
# ============================================================

st.title("📚 RAG Book Assistant")

st.write(
    "Upload PDF books and ask questions from the documents."
)


# ============================================================
# PDF UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload a PDF book",
    type=["pdf"]
)


# ============================================================
# CREATE VECTOR DATABASE
# ============================================================

if uploaded_file:

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as tmp_file:

        tmp_file.write(
            uploaded_file.getvalue()
        )

        file_path = tmp_file.name


    st.success("PDF uploaded successfully!")


    if st.button("Create Vector Database"):

        with st.spinner(
            "Processing document and creating embeddings..."
        ):

            # --------------------------------------------
            # Calculate PDF hash
            # --------------------------------------------

            file_hash = get_file_hash(
                file_path
            )


            # --------------------------------------------
            # Processed files record
            # --------------------------------------------

            hash_file = "processed_files.json"


            if os.path.exists(hash_file):

                with open(
                    hash_file,
                    "r"
                ) as f:

                    processed_files = json.load(f)

            else:

                processed_files = {}


            # --------------------------------------------
            # Check duplicate PDF
            # --------------------------------------------

            if file_hash in processed_files:

                st.info(
                    "This PDF has already been added "
                    "to the vector database."
                )


            else:

                # ----------------------------------------
                # Load PDF
                # ----------------------------------------

                loader = PyPDFLoader(
                    file_path
                )

                docs = loader.load()


                # ----------------------------------------
                # Split PDF into chunks
                # ----------------------------------------

                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )

                chunks = splitter.split_documents(
                    docs
                )


                # ----------------------------------------
                # Create / Update Chroma DB
                # ----------------------------------------

                if os.path.exists("chroma_db"):

                    vectorstore = Chroma(
                        persist_directory="chroma_db",
                        embedding_function=embeddings
                    )

                    vectorstore.add_documents(
                        chunks
                    )

                else:

                    vectorstore = Chroma.from_documents(
                        documents=chunks,
                        embedding=embeddings,
                        persist_directory="chroma_db"
                    )


                # ----------------------------------------
                # Save processed PDF information
                # ----------------------------------------

                processed_files[file_hash] = (
                    uploaded_file.name
                )


                with open(
                    hash_file,
                    "w"
                ) as f:

                    json.dump(
                        processed_files,
                        f,
                        indent=4
                    )


                st.success(
                    "PDF added to the vector database successfully!"
                )


# ============================================================
# LOAD VECTOR DATABASE
# ============================================================

# No document is indexed on the first visit, so the chat input does not exist yet.
# Initialise it before the database check to avoid referencing an undefined variable.
query = None

if os.path.exists("chroma_db"):

    vectorstore = Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings
    )


    # ========================================================
    # RETRIEVER
    # ========================================================

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 4,
            "fetch_k": 10,
            "lambda_mult": 0.5
        }
    )


    # ========================================================
    # LOAD LLM
    # ========================================================

    llm = get_llm()


    # ========================================================
    # PROMPT
    # ========================================================

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a helpful AI assistant.

Answer the user's question using ONLY the
provided context from the uploaded documents.

If the answer is not present in the context,
say:

"I could not find the answer in the document."

Do not make up information.
"""
            ),
            (
                "human",
                """
Context:

{context}


Question:

{question}
"""
            )
        ]
    )


    # ========================================================
    # CHAT HISTORY
    # ========================================================

    if "messages" not in st.session_state:

        st.session_state.messages = []


    st.divider()

    st.subheader(
        "💬 Ask Questions From the Book"
    )


    # ========================================================
    # DISPLAY PREVIOUS MESSAGES
    # ========================================================

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )


    # ========================================================
    # CLEAR CHAT BUTTON
    # ========================================================

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        st.rerun()


    # ========================================================
    # CHAT INPUT
    # ========================================================

    query = st.chat_input(
        "Ask a question from the book..."
    )


    # ========================================================
# PROCESS QUESTION
# ========================================================

if query:

    # --------------------------------------------
    # Display user question
    # --------------------------------------------

    with st.chat_message("user"):

        st.write(query)


    # --------------------------------------------
    # Save user question
    # --------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )


    # --------------------------------------------
    # Detect normal conversation
    # --------------------------------------------

    casual_messages = [
        "hi",
        "hello",
        "hey",
        "ok",
        "okay",
        "thanks",
        "thank you",
        "good morning",
        "good afternoon",
        "good evening",
        "bye",
        "goodbye",
        "who are you",
        "what are you",
        "how are you"
    ]


    is_casual = query.lower().strip() in casual_messages


    # ========================================================
    # NORMAL LLM CONVERSATION
    # ========================================================

    if is_casual:

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                response = llm.invoke(
                    query
                )


            st.write(
                response.content
            )


        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response.content
            }
        )


    # ========================================================
    # RAG QUESTION
    # ========================================================

    else:

        with st.chat_message("assistant"):

            with st.spinner(
                "Searching the document..."
            ):

                docs = retriever.invoke(
                    query
                )


                # --------------------------------------------
                # Create context
                # --------------------------------------------

                context = "\n\n".join(
                    [
                        doc.page_content
                        for doc in docs
                    ]
                )


                # --------------------------------------------
                # Create RAG prompt
                # --------------------------------------------

                final_prompt = prompt.invoke(
                    {
                        "context": context,
                        "question": query
                    }
                )


                # --------------------------------------------
                # Generate answer
                # --------------------------------------------

                with st.spinner(
                    "Generating answer..."
                ):

                    response = llm.invoke(
                        final_prompt
                    )


            st.write(
                response.content
            )


        # --------------------------------------------
        # Save AI response
        # --------------------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response.content
            }
        )
