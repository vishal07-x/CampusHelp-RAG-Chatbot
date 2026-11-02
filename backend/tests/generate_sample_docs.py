import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "sample_documents"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_pdf(filepath: Path, title: str, pages_content: list):
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1E40AF'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=6
    )
    notice_style = ParagraphStyle(
        'Notice',
        parent=styles['Italic'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=10
    )

    story = []
    
    for page_idx, sections in enumerate(pages_content):
        # Header for each page
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(f"Official Institutional Document - Campus Administration | Page {page_idx + 1}", notice_style))
        story.append(Spacer(1, 10))

        for heading, text, *table_data in sections:
            if heading:
                story.append(Paragraph(heading, h2_style))
            if text:
                story.append(Paragraph(text, body_style))
            if table_data and table_data[0]:
                t = Table(table_data[0], colWidths=[200, 300])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E0E7FF')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,0), 9),
                    ('BOTTOMPADDING', (0,0), (-1,0), 6),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('FONTSIZE', (0,1), (-1,-1), 8.5),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ]))
                story.append(t)
                story.append(Spacer(1, 10))

        if page_idx < len(pages_content) - 1:
            story.append(PageBreak())

    doc.build(story)
    print(f"Generated: {filepath.name}")


def generate_all_samples():
    # 1. Academic Regulations & Attendance Policy
    create_pdf(
        OUTPUT_DIR / "1_Academic_Regulations_and_Attendance_Policy.pdf",
        "Apex Institute of Technology - Academic Regulations & Attendance Policy 2024-2025",
        [
            # Page 1
            [
                (
                    "1. Attendance Mandate & Minimum Requirements",
                    "Students must maintain a minimum aggregate attendance of 75% in each registered course (theory and laboratory independently) to be eligible to appear for the End-Semester Final Examinations. Attendance is marked digitally via the Campus Portal by course instructors."
                ),
                (
                    "2. Condonation of Attendance Shortage",
                    "A student having attendance between 65% and 74.9% may apply for attendance condonation strictly on medical grounds or official representation of the institute in approved inter-collegiate sports/cultural events. Medical certificates verified by the Campus Chief Medical Officer must be submitted to the Academic Dean within 5 working days of resumption of classes.",
                    [
                        ["Attendance Percentage", "Eligibility Status"],
                        ["75.0% and above", "Eligible for End-Semester Examinations"],
                        ["65.0% to 74.9%", "Eligible ONLY with formal Dean Medical Condonation & Fine ($25 / Rs 1,000)"],
                        ["Below 65.0%", "Strictly Detained. Awarded 'FA' Grade (Failure due to Attendance). Must repeat course."]
                    ]
                )
            ],
            # Page 2
            [
                (
                    "3. Course Registration, Add/Drop Deadlines",
                    "Course registration takes place during the first week of every semester. Students are permitted to Add or Drop elective courses up to the end of Week 2 of the academic term. Withdrawal from an elective course without academic penalty is allowed until Week 4 with prior advisor approval."
                ),
                (
                    "4. Minimum and Maximum Credit Limits",
                    "Undergraduate students in B.Tech programs must register for a minimum of 16 credits and a maximum of 26 credits per semester. Overloading up to 28 credits is permitted solely for students with a cumulative CGPA of 8.50 or higher in their preceding academic year."
                )
            ]
        ]
    )

    # 2. Fee Structure & Scholarship Guidelines
    create_pdf(
        OUTPUT_DIR / "2_Fee_Structure_and_Scholarship_Guidelines_2024.pdf",
        "Apex Institute of Technology - Comprehensive Fee Structure & Scholarships 2024-2025",
        [
            # Page 1
            [
                (
                    "1. Tuition Fee Schedule & Payment Deadlines",
                    "All tuition fees must be remitted strictly via the online ERP student portal. The payment deadlines for the academic year 2024-2025 are as follows: Fall Semester fees are due on August 15, 2024. Spring Semester fees are due on January 15, 2025.",
                    [
                        ["Program / Department", "Tuition Fee Per Semester"],
                        ["B.Tech Computer Science & Engineering", "$45,000 / INR 95,000"],
                        ["B.Tech Electronics & Mechanical", "$42,000 / INR 88,000"],
                        ["BCA & B.Sc Data Science", "$35,000 / INR 75,000"],
                        ["MBA & Master of Science", "$50,000 / INR 110,000"]
                    ]
                ),
                (
                    "2. Late Payment Penalty Policy",
                    "A grace period of 7 calendar days is permitted. Remittance after the deadline incurs a late fee fine of $50 / INR 500 per week for up to two weeks. Failure to remit fees beyond 14 days past deadline results in temporary withholding of semester registration and course access."
                )
            ],
            # Page 2
            [
                (
                    "3. Merit-Based Institutional Scholarships",
                    "The institution awards merit scholarships based on Semester Grade Point Average (SGPA) and CGPA maintained across consecutive terms.",
                    [
                        ["Cumulative CGPA Band", "Tuition Fee Waiver %"],
                        ["CGPA 9.50 - 10.00", "75% Tuition Fee Waiver"],
                        ["CGPA 9.00 - 9.49", "50% Tuition Fee Waiver"],
                        ["CGPA 8.50 - 8.99", "25% Tuition Fee Waiver"]
                    ]
                ),
                (
                    "4. Need-Based Financial Assistance and Sports Quota",
                    "Economically Disadvantaged students with annual family income below $5,000 / INR 3,00,000 can apply for the Dean's Hardship Grant providing up to 50% fee relief. National level medalists in recognized sports receive a 100% sports scholarship covering tuition and hostel fees."
                )
            ]
        ]
    )

    # 3. Examination Rules & Grading System
    create_pdf(
        OUTPUT_DIR / "3_Examination_Rules_and_Grading_System.pdf",
        "Apex Institute of Technology - Examination Regulations & Evaluation System",
        [
            # Page 1
            [
                (
                    "1. Course Assessment Breakdown",
                    "The evaluation scheme comprises Continuous Internal Assessment (CIA) and End-Semester Examinations (ESE). CIA constitutes 50% weightage (Mid-Term Exam: 30%, Quizzes & Assignments: 20%). The End-Semester Examination carries 50% weightage.",
                    [
                        ["Component", "Weightage %", "Minimum Passing Requirement"],
                        ["Continuous Internal Assessment (CIA)", "50%", "40% (20 marks out of 50)"],
                        ["End-Semester Examination (ESE)", "50%", "40% (20 marks out of 50)"],
                        ["Overall Aggregate Course Score", "100%", "50% Overall Aggregate"]
                    ]
                ),
                (
                    "2. 10-Point Absolute Grading Scale",
                    "Grades are awarded on a 10-point scale: 'O' (Outstanding, 10 points, >=90%), 'A+' (Excellent, 9 points, 80-89%), 'A' (Very Good, 8 points, 70-79%), 'B+' (Good, 7 points, 60-69%), 'B' (Above Average, 6 points, 55-59%), 'C' (Pass, 5 points, 50-54%), 'F' (Fail, 0 points, <50%)."
                )
            ],
            # Page 2
            [
                (
                    "3. Re-evaluation, Re-totaling, and Script Inspection",
                    "Students may request re-evaluation of their end-semester answer scripts within 7 calendar days of result publication via the Exam Controller portal. A non-refundable processing fee of $20 / INR 500 per course applies. If the revised score changes by more than 10%, the re-evaluation fee is refunded.",
                    None
                ),
                (
                    "4. Supplementary Examinations",
                    "Supplementary examinations for failed courses ('F' grade) are conducted annually during the Summer break in July. A student can appear for a maximum of 4 supplementary papers in a single examination session."
                )
            ]
        ]
    )

    # 4. Placement Eligibility & Recruitment Policy
    create_pdf(
        OUTPUT_DIR / "4_Placement_Eligibility_and_Recruitment_Policy.pdf",
        "Apex Institute of Technology - Training & Placement Cell Policies 2024",
        [
            # Page 1
            [
                (
                    "1. Student Registration & Eligibility Criteria",
                    "To participate in campus recruitment drives, undergraduate students must possess a minimum cumulative CGPA of 6.50 across all completed semesters with no more than 1 active/standing backlog at the date of drive registration. Certain Tier-1 multinational recruiters enforce strict criteria of CGPA >= 7.50 with zero lifetime backlogs.",
                    [
                        ["Category", "Criteria"],
                        ["General Placement Eligibility", "CGPA >= 6.50, Max 1 active backlog"],
                        ["Tier-1 / Dream Companies", "CGPA >= 7.50, 0 active backlogs"],
                        ["Super Dream Recruiter Band", "Packages exceeding 18 LPA ($75,000)"]
                    ]
                ),
                (
                    "2. The Dream Offer Regulation",
                    "Once a candidate secures a placement offer, they are categorized as Placed. Placed students are permitted to contest for ONLY ONE additional 'Dream Offer' if the compensation package is at least 1.5 times their existing offer, or for any 'Super Dream' offer exceeding 18 LPA."
                )
            ],
            # Page 2
            [
                (
                    "3. Mandatory Professional Dress Code",
                    "Students appearing for corporate presentations, written rounds, and interviews must strictly adhere to formal corporate attire. Formal dark suits/blazers, polished formal shoes, and institutional ID badges are compulsory. Casual apparel or sneakers result in instant debarment from the drive."
                ),
                (
                    "4. Pre-Placement Training (Bootcamp)",
                    "Participation in the 6th-semester 40-hour Aptitude, Data Structures, and Soft Skills training bootcamp is mandatory. Failure to achieve 85% attendance in the training bootcamp forfeits campus placement registration."
                )
            ]
        ]
    )

    # 5. Campus Facilities, Hostel & Library Rules
    create_pdf(
        OUTPUT_DIR / "5_Campus_Facilities_Hostel_and_Library_Rules.pdf",
        "Apex Institute of Technology - Campus Facilities, Library & Residential Rules",
        [
            # Page 1
            [
                (
                    "1. Central Library Timings & Borrowing Regulations",
                    "The Central Library operates from 8:00 AM to 10:00 PM on all weekdays, and 9:00 AM to 5:00 PM on weekends and public holidays. During End-Semester Examination weeks, reading halls remain open until 2:00 AM.",
                    [
                        ["User Category", "Book Issue Quota", "Borrowing Duration", "Overdue Late Fine"],
                        ["Undergraduate Students", "4 Books", "14 Days", "$1 / INR 5 per day per book"],
                        ["Postgraduate & Scholars", "6 Books", "30 Days", "$1 / INR 5 per day per book"],
                        ["Faculty Members", "10 Books", "90 Days", "No overdue fine"]
                    ]
                ),
                (
                    "2. Digital Library & Research Databases",
                    "Students have access to IEEE Xplore, ScienceDirect, and ACM Digital Library terminals on the 2nd floor. Remote off-campus proxy access is enabled through the student library portal credentials."
                )
            ],
            # Page 2
            [
                (
                    "3. Residential Hall & Hostel Regulations",
                    "Hostel curfew is strictly 9:30 PM for all campus residential blocks. Night biometric attendance is captured between 9:30 PM and 10:15 PM. Students planning overnight stay outside campus must obtain written parental consent submitted through the warden e-portal 24 hours prior."
                ),
                (
                    "4. Health Center & Emergency Facilities",
                    "The Apex Campus Health Center operates 24/7 with a resident physician, nurses, and an on-call emergency ambulance service. Basic medical consultations, emergency trauma triage, and generic pharmaceuticals are free for all enrolled students upon presentation of student ID cards."
                )
            ]
        ]
    )


if __name__ == "__main__":
    generate_all_samples()
