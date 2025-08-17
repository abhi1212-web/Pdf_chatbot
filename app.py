import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI

# Initialize OpenAI client (make sure your API key is set in terminal: export OPENAI_API_KEY="your_key")
client = OpenAI()

# Streamlit page config
st.set_page_config(page_title="PDF Chatbot", page_icon="📄", layout="centered")
st.title("📄 Chat with your PDF")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# Session state for conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# If PDF is uploaded, process it
if uploaded_file is not None:
    with st.spinner("Reading PDF..."):
        pdf_text = extract_text_from_pdf(uploaded_file)

    st.success("✅ PDF loaded successfully!")

    # Show previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask something about the PDF..."):
        # Store user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build context: PDF text + conversation history
        context = "You are a helpful assistant. Use the following PDF text to answer questions.\n\n"
        context += pdf_text[:3000]  # limit to 3000 chars so it fits into context
        context += "\n\nConversation:\n"
        for msg in st.session_state.messages:
            context += f"{msg['role']}: {msg['content']}\n"

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": context},
                        {"role": "user", "content": prompt}
                    ]
                )
                reply = response.choices[0].message.content
                st.markdown(reply)

        # Save assistant reply
        st.session_state.messages.append({"role": "assistant", "content": reply})
