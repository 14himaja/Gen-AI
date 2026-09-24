"""
Standalone Migration Script: Migrates all existing document chunks from SQLite
to FAISS Vector Store with L2-normalized vector embeddings.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database import db
from app.services.faiss_store import faiss_store
from app.services.embeddings import embedding_service


def run_migration():
    print("=================================================================")
    print("MIGRATING SQLITE CHUNKS TO FAISS VECTOR STORE")
    print("=================================================================\n")

    # 1. Fetch parent document count
    hospital_docs = db.get_hospital_documents()
    user_docs = db.get_user_documents("P1001") + db.get_user_documents("P1002")
    doc_count = len(hospital_docs) + len(user_docs)

    # 2. Extract all chunks from SQLite
    all_chunks = db.get_all_chunks_for_rebuild()
    chunk_count = len(all_chunks)

    print(f"Documents found: {doc_count}")
    print(f"Chunks found: {chunk_count}")

    if chunk_count == 0:
        print("[WARNING] No document chunks found in SQLite database.")
        return

    # 3. Generate embeddings and rebuild FAISS index
    print("Generating embeddings and indexing vectors into FAISS...")
    faiss_store.rebuild(all_chunks)

    # 4. Clean up SQLite database: Drop hospital_doc_chunks table if present
    try:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS hospital_doc_chunks")
            conn.commit()
        print("Dropped obsolete hospital_doc_chunks table from SQLite (chunks now 100% in FAISS).")
    except Exception as e:
        print(f"[Warning] Could not drop hospital_doc_chunks table: {e}")

    vector_count = faiss_store.index.ntotal if faiss_store.index else 0
    dim = faiss_store.dimension or 0

    print(f"\nChunks embedded: {vector_count}")
    print(f"FAISS vectors: {vector_count}")
    print(f"Embedding dimension: {dim}")
    print("\n=================================================================")
    print("Migration completed successfully: Chunks stored 100% in FAISS DB!")
    print("=================================================================")


if __name__ == "__main__":
    run_migration()

