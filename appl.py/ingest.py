import streamlit as st
from streamlit_chat import message
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import PyPDFLoader

from langchain_community.embeddings import HuggingFaceEmbeddings

import PyPDF2


from langchain_community.llms import CTransformers
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import faiss
from langchain.memory import ConversationBufferMemory
import os

# Get the absolute path to the PDF file
# Create a DirectoryLoader
import PyPDF2

def read_pdf(pdf_path):
  """
  Reads the text content from a PDF file.

  Args:
      pdf_path (str): The path to the PDF file.

  Returns:
      str: The extracted text content from the PDF.

  Raises:
      FileNotFoundError: If the PDF file is not found.
  """

  try:
    with open(pdf_path, 'rb') as pdf_file:
      pdf_reader = PyPDF2.PdfReader(pdf_file)
      text = ""
      for page in pdf_reader.pages:
        text += page.extract_text()
      return text
  except FileNotFoundError:
    raise FileNotFoundError("The specified PDF file could not be found.")

# Assuming your PDF is in the same directory as this script
loader= read_pdf("ZYX Hospital.pdf")



# Load documents
documents = loader.load()




# Split text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
text_chunks = text_splitter.split_text(document)

# Create embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                   model_kwargs={'device': "cpu"})

# Vectorstore
vector_store = FAISS.from_documents(text_chunks, embeddings)

# Create LLM
llm = CTransformers(model="llama-2-7b-chat.ggmlv3.q4_0.bin", model_type="llama",
                    config={'max_new_tokens': 128, 'temperature': 0.01})

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

chain = ConversationalRetrievalChain.from_llm(llm=llm, chain_type='stuff',
                                              retriever=vector_store.as_retriever(search_kwargs={"k": 2}),
                                              memory=memory)

st.title("HealthCare ChatBot 🧑🏽‍⚕️")


def conversation_chat(query):
    result = chain({"question": query, "chat_history": st.session_state['history']})
    st.session_state['history'].append((query, result["answer"]))
    return result["answer"]


def initialize_session_state():
    if 'history' not in st.session_state:
        st.session_state['history'] = []

    if 'generated' not in st.session_state:
        st.session_state['generated'] = ["Hello! Ask me anything about 🤗"]

    if 'past' not in st.session_state:
        st.session_state['past'] = ["Hey! 👋"]


def display_chat_history():
    reply_container = st.container()
    container = st.container()

    with container:
        with st.form(key='my_form', clear_on_submit=True):
            user_input = st.text_input("Question:", placeholder="Ask about your Mental Health", key='input')
            submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:
            output = conversation_chat(user_input)

            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)

    if st.session_state['generated']:
        with reply_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")


# Initialize session state
initialize_session_state()
# Display chat history
display_chat_history()
