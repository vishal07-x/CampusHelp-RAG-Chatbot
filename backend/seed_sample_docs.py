import os
import sys
from pathlib import Path

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.database import SessionLocal
from app.db.init_db import init_db
from app.services.ingestion_service import ingestion_service
from app.core.logging import logger

SAMPLE_DOCS = [
    {
        "filename": "1_Academic_Regulations_and_Attendance_Policy.pdf",
        "department": "Academics",
        "category": "Regulations"
    },
    {
        "filename": "2_Fee_Structure_and_Scholarship_Guidelines_2024.pdf",
        "department": "Finance",
        "category": "Fees"
    },
    {
        "filename": "3_Examination_Rules_and_Grading_System.pdf",
        "department": "Examinations",
        "category": "Exams"
    },
    {
        "filename": "4_Placement_Eligibility_and_Recruitment_Policy.pdf",
        "department": "Placements",
        "category": "Placements"
    },
    {
        "filename": "5_Campus_Facilities_Hostel_and_Library_Rules.pdf",
        "department": "Facilities",
        "category": "Campus"
    }
]


def seed():
    sample_dir = backend_dir.parent / "data" / "sample_documents"
    if not sample_dir.exists():
        logger.error(f"Sample documents folder missing at: {sample_dir}")
        return

    logger.info("Initializing database tables & admin user...")
    with SessionLocal() as db:
        init_db(db)

        for doc_info in SAMPLE_DOCS:
            pdf_path = sample_dir / doc_info["filename"]
            if not pdf_path.exists():
                logger.warning(f"File not found: {pdf_path}")
                continue

            with open(pdf_path, "rb") as f:
                file_bytes = f.read()

            try:
                result = ingestion_service.ingest_pdf(
                    file_bytes=file_bytes,
                    filename=doc_info["filename"],
                    department=doc_info["department"],
                    category=doc_info["category"],
                    db=db
                )
                logger.info(f"[OK] Indexed: {doc_info['filename']} ({result['total_chunks']} chunks, {result['total_pages']} pages)")
            except ValueError as ve:
                logger.info(f"- Note: {doc_info['filename']} already indexed or skipped: {ve}")
            except Exception as e:
                logger.error(f"✗ Failed indexing {doc_info['filename']}: {e}")

    logger.info("Sample institutional documents seeded successfully!")


if __name__ == "__main__":
    seed()
