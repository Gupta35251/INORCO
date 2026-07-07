from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from crewai.tools import tool
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
import os
from dotenv import load_dotenv
load_dotenv()

# print("Loading embedding model",flush = True)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})

# parent_directory = os.path.dirname(os.path.abspath(__file__))

# print("Loading Vector DB Path",flush = True)
parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
vector_db_path = os.path.join(parent_directory, "vector_db")
# vector_db_path = "D:/PythonProject/INORCO/vector_db"

# print("Loading API_KEY",flush = True)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@tool("INORCO Website RAG Tool")
def rag_query_tool(query:str)->str:
    """
    Search the INORCO website knowledge base to answer user queries.

    Use this tool for questions related to:
    - Products and product specifications
    - Paints, primers, solvents, and coatings
    - Applications and technical details
    - Company information
    - Contact details
    - Services
    - Information available on any page of the INORCO website

    Do not use this tool for general knowledge questions or topics unrelated
    to the INORCO website.

    Args:
        query (str): User's question.

    Returns:
        str: Answer generated from the retrieved website content.
    """
    # print("Defining LLM",flush = True)
    llm = ChatGroq(api_key = GROQ_API_KEY,model = "llama-3.3-70b-versatile",temperature = 0)
    # print("LLM Loaded")

    vector_store = Chroma(embedding_function = embeddings,persist_directory = vector_db_path)
    # print("Vector Store loaded",flush = True)

    retriever = vector_store.as_retriever(search_type = "similarity",search_kwargs = {'k':10})
    # print("Retrieving Docs",flush  = True)

    # docs = retriever.invoke(query)
    # print("Query is invoked to Retriever",flush = True)
    # for i, d in enumerate(docs):
    #     print(f"--- Retrieved chunk {i} ---")
    #     print(d.page_content[:300])
    #     print()

    # print(f"Collection_Count : {len(docs)}")

    chain = RetrievalQA.from_llm(
        llm= llm,
        retriever = vector_store.as_retriever(search_type = "similarity",search_kwargs = {'k':10}),
        verbose = True,
        return_source_documents = True 
    )

    # print("Chain prepared",flush = True)
    response = chain.invoke({'query':query})
    
    return response["result"]
    # print("Done")

# if __name__ == '__main__':
#     print(rag_query_tool.run(query = "How many organic solvents in the inorco company.Give name of all of them"))

