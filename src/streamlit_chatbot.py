import streamlit as st
import os
from dotenv import load_dotenv
from langchain_cohere import ChatCohere
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# Configure the app page
st.set_page_config(page_title="Basic Chatbot", page_icon="🤖")
st.title("Basic Chatbot with LangChain 🤖")
st.markdown("This is an *example chatbot* built with LangChain + Streamlit. Write your message below to get started!")

with st.sidebar:
    st.header("Configuration")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.5, 0.1)
    st.write(f"Current temperature: {temperature}")

    personality = st.selectbox(
        "Assistant Personality",
        [
            "Helpful and friendly",
            "Professional and formal", 
            "Casual and relaxed",
            "Technical expert",
            "Creative and fun"
        ]
    )

    cohere_api_key = os.getenv("COHERE_API_KEY")
    if not cohere_api_key:
        st.error("Cohere API key not found. Please set COHERE_API_KEY in your .env file")
        st.stop()
    
    chat_model = ChatCohere(model="command-a-03-2025", temperature=temperature, cohere_api_key=cohere_api_key)
    
    # Define system messages according to personality
    system_messages = {
        "Helpful and friendly": "You are a helpful and friendly assistant called ChatBot Pro. Respond clearly and concisely.",
        "Professional and formal": "You are a professional and formal assistant. Provide precise and well-structured responses.",
        "Casual and relaxed": "You are a casual and relaxed assistant. Speak naturally and friendly, like a good friend.",
        "Technical expert": "You are a technical expert assistant. Provide detailed responses with technical precision.",
        "Creative and fun": "You are a creative and fun assistant. Use analogies, creative examples and maintain a cheerful tone."
    }

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", system_messages[personality]),
        ("human", "Conversation history:\n{history}\n\nCurrent question: {message}")

    ])

    chain = chat_prompt | chat_model

# Initialize message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages in the interface
for msg in st.session_state.messages:
    if isinstance(msg, SystemMessage):
        # Don't display the message on screen
        continue

    role = "assistant" if isinstance(msg, AIMessage) else "user"

    with st.chat_message(role):
        st.markdown(msg.content)

if st.button("New conversation"):
    st.session_state.messages = []
    st.rerun()

# User input box
question = st.chat_input("Write your message:")

if question:
    # Immediately display the user's message on screen
    with st.chat_message("user"):
        st.markdown(question)

    try:
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            for chunk in chain.stream({"message": question, "history": st.session_state.messages}):
                full_response += chunk.content
                response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)

        st.session_state.messages.append(HumanMessage(content=question))
        st.session_state.messages.append(AIMessage(content=full_response))

    except Exception as e:
        st.error(f"Error processing the request: {e}")
        st.info("Verify that your Cohere API key is configured correctly")
