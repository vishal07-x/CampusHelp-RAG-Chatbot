from pathlib import Path

SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "sample_documents"


def test_upload_pdf_admin_authorized(client, admin_token):
    pdf_path = SAMPLE_DIR / "1_Academic_Regulations_and_Attendance_Policy.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"files": ("1_Academic_Regulations_and_Attendance_Policy.pdf", file_bytes, "application/pdf")},
        data={"department": "Academics", "category": "Regulations"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "INDEXED"
    assert data[0]["total_pages"] == 2
    assert data[0]["total_chunks"] > 0


def test_upload_duplicate_pdf_rejected(client, admin_token):
    pdf_path = SAMPLE_DIR / "1_Academic_Regulations_and_Attendance_Policy.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    # First upload
    r1 = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"files": ("1_Academic_Regulations_and_Attendance_Policy.pdf", file_bytes, "application/pdf")},
        data={"department": "Academics", "category": "Regulations"}
    )
    assert r1.status_code == 200

    # Second upload of the identical file in the same session should report duplicate
    response = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"files": ("1_Academic_Regulations_and_Attendance_Policy.pdf", file_bytes, "application/pdf")},
        data={"department": "Academics", "category": "Regulations"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data[0]["status"] == "FAILED"
    assert "Duplicate document detected" in data[0]["message"]


def test_upload_pdf_student_forbidden(client, student_token):
    pdf_path = SAMPLE_DIR / "2_Fee_Structure_and_Scholarship_Guidelines_2024.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {student_token}"},
        files={"files": ("2_Fee_Structure_and_Scholarship_Guidelines_2024.pdf", file_bytes, "application/pdf")},
        data={"department": "Finance", "category": "Fees"}
    )
    assert response.status_code == 403


def test_list_documents(client, admin_token):
    pdf_path = SAMPLE_DIR / "2_Fee_Structure_and_Scholarship_Guidelines_2024.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    # Ensure at least one doc uploaded in this test session
    client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"files": ("2_Fee_Structure_and_Scholarship_Guidelines_2024.pdf", file_bytes, "application/pdf")},
        data={"department": "Finance", "category": "Fees"}
    )

    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert data["total"] >= 1
