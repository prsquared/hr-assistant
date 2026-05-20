"""
rag.py — FAISS-backed Retrieval-Augmented Generation (RAG) pipeline.

Responsibilities:
  - Load and chunk HR policy PDFs from data/policies/
  - Build and persist a FAISS vector index to data/faiss_index/
  - Expose a LangChain retrieval chain for policy Q&A

Public API:
  rebuild_index_from_policies() -> FAISS | None
  load_vector_store()           -> FAISS | None
  get_rag_chain(vector_store, llm) -> Chain
"""

import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

FAISS_INDEX_PATH = os.path.join("data", "faiss_index")
POLICIES_DIR = os.path.join("data", "policies")


def rebuild_index_from_policies():
    """Reads all PDFs in data/policies/, builds a FAISS index, and saves it to disk.

    Returns:
        FAISS vector store, or None if no PDFs are found.
    """
    os.makedirs(POLICIES_DIR, exist_ok=True)

    pdf_files = [f for f in os.listdir(POLICIES_DIR) if f.endswith(".pdf")]
    if not pdf_files:
        return None

    all_docs = []
    for pdf_file in pdf_files:
        full_path = os.path.join(POLICIES_DIR, pdf_file)
        try:
            loader = PyPDFLoader(full_path)
            all_docs.extend(loader.load())
        except Exception as e:
            print(f"[rag] Error loading {pdf_file}: {e}")

    if not all_docs:
        return None

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = splitter.split_documents(all_docs)

    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(splits, embeddings)

    os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
    vector_store.save_local(FAISS_INDEX_PATH)
    return vector_store


def load_vector_store():
    """Loads the FAISS index from disk. Rebuilds from PDFs if the index is missing.

    Returns:
        FAISS vector store, or None if no data is available.
    """
    embeddings = OpenAIEmbeddings()
    index_file = os.path.join(FAISS_INDEX_PATH, "index.faiss")

    if os.path.exists(index_file):
        try:
            return FAISS.load_local(
                FAISS_INDEX_PATH,
                embeddings,
                allow_dangerous_deserialization=True,
            )
        except Exception as e:
            print(f"[rag] Error loading local index: {e}")

    # Fallback: rebuild from source PDFs
    return rebuild_index_from_policies()


def get_rag_chain(vector_store, llm):
    """Wraps the FAISS retriever in a LangChain RetrievalQA chain.

    Args:
        vector_store: A loaded FAISS vector store instance.
        llm:          A LangChain-compatible LLM (e.g. ChatOpenAI).

    Returns:
        A LangChain retrieval chain that accepts {"input": str} and
        returns {"answer": str, "context": list}.
    """
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    system_prompt = (
        "You are an HR policy assistant. Use the retrieved context below to answer "
        "the employee's question. If the answer is not in the context, say so clearly. "
        "Keep responses concise and cite the relevant policy section when possible."
        "\n\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    qa_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, qa_chain)
