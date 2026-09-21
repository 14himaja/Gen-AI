import os
from pathlib import Path
from app.database import db

def upload_master_policy_doc():
    doc_path = Path("docs/ApolloCare_Hospital_Policies_Schemes_Guidelines.txt")
    if not doc_path.exists():
        print("Error: Document file not found!")
        return

    content = doc_path.read_text(encoding="utf-8")
    title = "ApolloCare Master Hospital Policies, Government Schemes & Patient Guidelines (2026)"
    category = "POLICIES_AND_SCHEMES"
    uploaded_by = "A4001"

    res = db.add_hospital_document(
        title=title,
        category=category,
        uploaded_by=uploaded_by,
        content=content
    )

    print("--- DOCUMENT UPLOAD SUCCESSFUL ---")
    print("Doc ID:", res["id"])
    print("Title:", res["title"])
    print("Chunk Count:", res["chunk_count"])
    print("Uploaded By:", res["uploaded_by"])
    print("Upload Date:", res["upload_date"])

if __name__ == "__main__":
    upload_master_policy_doc()
