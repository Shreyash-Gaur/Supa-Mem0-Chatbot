from dotenv import load_dotenv
from mem0 import Memory
import os

# Load environment variables
load_dotenv()

# --- Final Corrected Config ---
config = {
    "vector_store": {
        "provider": "supabase",
        "config": {
            "connection_string": os.environ['DATABASE_URL'],
            "collection_name": "memories",
            "embedding_model_dims": 768
        }
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.2:latest",
            "ollama_base_url": "http://localhost:11434",
        },
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "ollama_base_url": "http://localhost:11434",
        },
    },
}

# Initialize Memory
memory = Memory.from_config(config)

def chat_with_memories(message: str, user_id: str = "local_user") -> str:
    """
    Handles a chat turn by searching for memories, building a message history,
    generating a response, and adding the conversation to memory.
    """
    # 1. Retrieve relevant user-specific memories
    relevant_memories = memory.search(query=message, user_id=user_id, limit=3)
    
    # 2. Construct the system prompt with memories
    if relevant_memories and relevant_memories.get("results"):
        memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
        system_prompt = f"You are a helpful AI. Answer based on the query and memories.\n\nMemories:\n{memories_str}"
    else:
        system_prompt = "You are a helpful AI."

    # 3. Build the message list for the LLM
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]

    # 4. Generate a response using the lower-level LLM interface
    assistant_response = memory.llm.generate_response(messages=messages)

    # 5. Add the new conversation turn to the user's memory
    messages.append({"role": "assistant", "content": assistant_response})
    memory.add(messages, user_id=user_id)

    return assistant_response

def main():
    """
    Main loop to run the chatbot in the terminal.
    """
    print("Chat with your local AI (type 'exit' to quit)")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        ai_response = chat_with_memories(user_input)
        print(f"AI: {ai_response}")

if __name__ == "__main__":
    main()
