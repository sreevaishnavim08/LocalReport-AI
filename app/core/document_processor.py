
from docx import Document
from openpyxl import load_workbook


# --------------------------------
# EXTRACT TEXT FROM WORD DOCUMENT
# --------------------------------

def extract_document_text(source_path):
    """Extract paragraphs and tables from a Word document."""

    doc = Document(source_path)

    extracted_text = []

    # Extract paragraphs
    for paragraph in doc.paragraphs:

        text = paragraph.text.strip()

        if text:
            extracted_text.append(text)

    # Extract tables
    for table in doc.tables:

        for row in table.rows:

            row_text = " | ".join(
                cell.text.strip()
                for cell in row.cells
            )

            if row_text.strip():
                extracted_text.append(row_text)

    return "\n".join(extracted_text)


# --------------------------------
# ORIGINAL RULE-BASED DOCUMENT READER
# --------------------------------

def read_project_document(source_path):
    """Read project information using document structure."""

    doc = Document(source_path)

    project = {
        "overview": {},
        "description": "",
        "milestones": [],
        "risks": [],
        "next_period": "",
        "notes": ""
    }

    # Project overview table
    if len(doc.tables) > 0:

        for row in doc.tables[0].rows:

            if len(row.cells) >= 2:

                key = row.cells[0].text.strip()
                value = row.cells[1].text.strip()

                project["overview"][key] = value

    # Milestone table
    if len(doc.tables) > 1:

        for row in doc.tables[1].rows[1:]:

            project["milestones"].append(
                [cell.text.strip() for cell in row.cells]
            )

    # Risk table
    if len(doc.tables) > 2:

        for row in doc.tables[2].rows[1:]:

            project["risks"].append(
                [cell.text.strip() for cell in row.cells]
            )

    # Read text sections
    current_section = ""

    for paragraph in doc.paragraphs:

        text = paragraph.text.strip()

        if not text:
            continue

        if "Project Description" in text:
            current_section = "description"

        elif "Next Reporting Period" in text:
            current_section = "next_period"

        elif "Reporting Notes" in text:
            current_section = "notes"

        elif text.startswith(("1.", "3.", "4.", "5.", "6.")):
            current_section = ""

        elif current_section == "description":
            project["description"] += text + "\n"

        elif current_section == "next_period":
            project["next_period"] += text + "\n"

        elif current_section == "notes":
            project["notes"] += text + "\n"

    return project


# --------------------------------
# FILL EXCEL REPORT TEMPLATE
# --------------------------------

def fill_excel_template(project, template_path, output_path):
    """Fill the Excel report using AI-extracted information."""

    workbook = load_workbook(template_path)

    sheet = workbook["Project Report"]

    # Project overview
    sheet["B5"] = project.get("project_name", "")
    sheet["D5"] = project.get("client", "")
    sheet["B6"] = project.get("project_manager", "")
    sheet["D6"] = project.get("project_status", "")
    sheet["B7"] = project.get("project_start_date", "")
    sheet["D7"] = project.get("target_completion_date", "")
    sheet["B8"] = project.get("approved_budget", "")
    sheet["D8"] = project.get("current_completion", "")

    # Project summary
    sheet["A11"] = project.get("project_description", "")

    # Milestones
    for row_number, milestone in enumerate(
        project.get("milestones", [])[:5],
        start=16
    ):

        sheet.cell(row=row_number, column=1).value = (
            milestone.get("name", "")
        )

        sheet.cell(row=row_number, column=2).value = (
            milestone.get("status", "")
        )

        sheet.cell(row=row_number, column=3).value = (
            milestone.get("progress", "")
        )

        sheet.cell(row=row_number, column=4).value = (
            milestone.get("target_date", "")
        )

    # Risks
    for row_number, risk in enumerate(
        project.get("risks", [])[:4],
        start=24
    ):

        sheet.cell(row=row_number, column=1).value = (
            risk.get("risk_id", "")
        )

        sheet.cell(row=row_number, column=2).value = (
            risk.get("description", "")
        )

        sheet.cell(row=row_number, column=3).value = (
            risk.get("severity", "")
        )

        sheet.cell(row=row_number, column=4).value = (
            risk.get("mitigation", "")
        )

    # Next reporting period and notes
    sheet["A30"] = project.get("next_reporting_period", "")
    sheet["A34"] = project.get("reporting_notes", "")

    # Save completed workbook
    workbook.save(output_path)

    return output_path

