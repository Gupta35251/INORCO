from langchain_community.document_loaders import DirectoryLoader,UnstructuredFileLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os
import re
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def clean_text(text):
    text = re.sub(r'\+91-\d{10}','',text)
    text = re.sub(r'info@inorco\.in','',text)
    text = re.sub(r'Industrial Paints manufacturer.*?(?=\n|$)','',text)
    text = re.sub(r'\n{3,}','\n\n',text)
    return text.strip()


parent_directory = os.path.dirname(os.path.abspath(__file__))
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})
docs_dir = f"{parent_directory}/web_data"
vector_db_path = f"{parent_directory}/vector_db"
loader = DirectoryLoader(docs_dir,glob = "**/*.md",loader_cls = UnstructuredFileLoader)
documents = loader.load()
for doc in documents:
    doc.page_content = clean_text(doc.page_content)
text_splitter = CharacterTextSplitter(
    chunk_size = 1500,
    chunk_overlap = 200
)
chunks = text_splitter.split_documents(documents)
seen = set()
unique_chunks = []
for chunk in chunks:
    key = chunk.page_content.strip()[:300]
    if key not in seen:
        seen.add(key)
        unique_chunks.append(chunk)
vector_db = Chroma.from_documents(documents = unique_chunks,embedding = embeddings,persist_directory=vector_db_path)

