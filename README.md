# 🧠 Local AI Chat Assistant with Persistent Memory

A sophisticated, locally-run AI chat assistant that remembers your conversations, providing a truly personalized and private AI experience. Built with a modern Python stack, this application leverages local Large Language Models (LLMs), a persistent memory store powered by Supabase, and a sleek, interactive web interface built with Streamlit.

This project's core purpose is to demonstrate the power of combining local AI with persistent memory, showcasing an iterative development process from a basic proof-of-concept to a full-fledged, multi-user web application.

## ✨ Key Features

  * **🧠 Persistent Memory**: The AI remembers past conversations, allowing for context-aware and personalized interactions for each user.
  * **🔐 User Authentication**: Secure sign-up and login functionality to ensure that your conversations remain private and tied to your account.
  * **💻 Local First**: The entire AI stack, from the LLM to the embedding models, runs on your local machine using Ollama, ensuring complete data privacy and offline capabilities.
  * **🌐 Interactive UI**: A user-friendly and responsive web interface built with Streamlit, providing a seamless chat experience.
  * **💾 Scalable Backend**: Utilizes Supabase for robust user authentication and a scalable vector store for the AI's memory.
  * **🧹 Memory Management**: Users can clear their entire chat history, allowing them to start fresh whenever they choose.

## 🚀 How It Works: A Deep Dive

The system is designed to be a powerful yet easy-to-understand application of Retrieval-Augmented Generation (RAG) in a conversational AI context.

### Step 1: Ingestion - Building the Memory

The foundation of the agent is its ability to learn from your conversations.

  * **Conversational Data**: Every interaction you have with the AI—both your messages and the AI's responses—is treated as a potential memory.
  * **`mem0` Core Engine**: The `mem0` library is the workhorse for memory management. After each conversational turn, the `memory.add()` function is called. It takes the conversation and:
    1.  Uses an embedding model (e.g., `nomic-embed-text`) to create a vector representation of the conversation.
    2.  Stores this vector and the conversation text in the Supabase vector store, associated with your user ID.

### Step 2: Retrieval - Finding Relevant Memories

When you send a new message, the agent doesn't just rely on its pre-trained knowledge. It first retrieves relevant memories from your past conversations.

  * **User-Specific Search**: The `memory.search()` function is called with your message as the query and your unique user ID.
  * **Vector Similarity Search**: This function performs a vector similarity search in the Supabase database to find the most relevant memories from your past conversations.
  * **Contextual Augmentation**: The retrieved memories are then used to augment the system prompt that is sent to the LLM. For example, if you previously mentioned you're interested in Python, the system prompt might be augmented with "Memories: The user is interested in Python."

### Step 3: Generation - Synthesizing the Answer

With the added context from your past conversations, the LLM can generate a much more personalized and relevant response.

  * **Grounded Generation**: The LLM uses the retrieved memories as a primary source of context to formulate its answer. This allows the AI to "remember" previous parts of the conversation and provide a more coherent and intelligent response.
  * **Continuous Learning**: The new conversation turn (your message and the AI's response) is then added to the memory, allowing the AI to continuously learn and adapt to your conversations.

## 📈 Project Evolution

This repository showcases the iterative development of the project, from a simple script to a full-fledged application.

  * **v1: The Proof of Concept (`v1-basic-qdrant-mem0.ipynb`)**: This initial version, developed in a Jupyter Notebook, demonstrated the core functionality of `mem0` using a local Qdrant vector store. It established the basic principles of adding and searching for memories.

  * **v2: The CLI Chatbot (`v2-supabase-mem0.py`)**: The project was then refactored into a command-line interface (CLI) application. The vector store was migrated from Qdrant to Supabase for better scalability and integration with user authentication.

  * **v3: The Full-Fledged Web App (`v3-streamlit-supabase-mem0.py`)**: The final iteration of the project is a multi-user web application built with Streamlit. This version includes a complete user authentication system, a polished user interface, and the ability for each user to have their own private and persistent memory.

## 🛠️ Setup and Installation

### Prerequisites

  * **Python 3.8+**
  * **Ollama**: [Install Ollama](https://ollama.com/) and pull the required models:
    ```bash
    ollama pull qwen3:8b # or any model of you preference
    ollama pull nomic-embed-text
    ```
  * **Supabase Account**: You'll need a Supabase account to handle authentication and the vector store or You'll need to setup supabase locally.
  * **qdrant Storage**: You'll need to locally install qdrant with docker.
    ```bash
    docker run -p 6333:6333 -p 6334:6334 \
        -v $(pwd)/qdrant_storage:/qdrant/storage \
        qdrant/qdrant
    ```
  

### Create a `.env` file

Create a file named `.env` in the root of the project and add your Supabase connection details.

```env
SUPABASE_URL="your_supabase_url"
SUPABASE_KEY="your_supabase_key"
DATABASE_URL="your_supabase_database_url"
```

## 📂 Project Structure

  * `v1-basic-qdrant-mem0.ipynb`: The initial proof-of-concept Jupyter Notebook.
  * `v2-supabase-mem0.py`: The command-line interface version of the chatbot.
  * `v3-streamlit-supabase-mem0.py`: The final Streamlit web application with user authentication.
  * `.env`: Configuration file for your Supabase credentials.
  * `supabase`: folder for your Supabase storage.

## 🛠️ Tech Stack

  * **Memory & LLM Orchestration:** `mem0`
  * **Web Framework:** `Streamlit`
  * **Database & Authentication:** `Supabase`
  * **Local LLMs & Embeddings:** `Ollama` (with models like `qwen3:8b`, `llama3.2`, `nomic-embed-text`)
  * **Vector Store:** `Qdrant` (in v1), `Supabase pgvector` (in v2 and v3)
