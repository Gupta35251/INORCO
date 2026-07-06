from crewai import Task
from agents.agent import agent

task = Task(
    agent = agent,
    description = """
    Answer the user's question using the INORCO Website RAG Tool.

    User Question:
    {question}

    Retrieve the most relevant information from the INORCO website knowledge
    base before generating the response. Base the answer only on the retrieved
    website content. Do not use prior knowledge or make assumptions. If the
    requested information is not available in the knowledge base, clearly
    inform the user that it could not be found on the INORCO website.
    """,

    expected_output = """
    A clear, accurate, and concise answer based solely on the retrieved
    information from the INORCO website. If no relevant information is found,
    respond that the information is unavailable on the INORCO website without
    generating unsupported details.
    """
)