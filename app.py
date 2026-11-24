

import streamlit as st
import json
import re
from io import BytesIO
from datetime import date

from app.core.document_processor import (
    extract_document_text,
    fill_excel_template
)
from app.ai.local_ai import extract_project_information


# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="LocalReport AI",
    page_icon="📊",
    layout="wide"
)


# --------------------------------
# SESSION STATE
# --------------------------------

defaults = {
    "project_data": {},
    "uploaded_names": [],
    "reports": [],
    "source_doc_bytes": None,
    "source_doc_name": None,
    "template_bytes": None,
    "template_name": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------------
# CUSTOM STYLING
# --------------------------------

st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
.block-container {
    padding-top: 2rem;
}
h1 {
    color: #172554;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------
# SIDEBAR NAVIGATION
# --------------------------------

with st.sidebar:
    st.title("📊 LocalReport AI")
    st.caption("Private Project Reporting Workspace")
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Project Details",
            "Document Upload",
            "AI Report Generator",
            "Generated Reports"
        ]
    )

    st.divider()
    st.success("Local workspace")


# --------------------------------
# DASHBOARD
# --------------------------------

if page == "Dashboard":

    st.title("Project Report Generator")

    st.write(
        "Create project reports from your company documents "
        "and existing report templates."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Projects",
            1 if st.session_state.project_data else 0
        )

    with col2:
        document_count = sum([
            st.session_state.source_doc_bytes is not None,
            st.session_state.template_bytes is not None
        ])

        st.metric("Documents Uploaded", document_count)

    with col3:
        st.metric(
            "Reports Generated",
            len(st.session_state.reports)
        )

    st.divider()

    st.subheader("Welcome to LocalReport AI")

    st.write(
        "Use the sidebar to enter project details, upload your "
        "documents, generate reports using local AI and download "
        "your completed reports."
    )

    st.info(
        "Your documents are processed using your locally installed "
        "Ollama AI model."
    )


# --------------------------------
# PROJECT DETAILS
# --------------------------------

elif page == "Project Details":

    st.title("📋 Project Information")

    existing = st.session_state.project_data

    with st.form("project_form"):

        project_name = st.text_input(
            "Project Name",
            value=existing.get("project_name", ""),
            placeholder="ABC Infrastructure Project"
        )

        col1, col2 = st.columns(2)

        with col1:
            client_name = st.text_input(
                "Client Name",
                value=existing.get("client_name", "")
            )

            project_manager = st.text_input(
                "Project Manager",
                value=existing.get("project_manager", "")
            )

            start_date = st.date_input(
                "Project Start Date",
                value=date.today()
            )

        with col2:
            project_status = st.selectbox(
                "Project Status",
                ["Not Started", "In Progress", "On Hold", "Completed"]
            )

            budget = st.number_input(
                "Project Budget",
                min_value=0.0,
                step=1000.0,
                value=float(existing.get("budget", 0))
            )

            progress = st.slider(
                "Project Completion (%)",
                0,
                100,
                int(existing.get("progress", 0))
            )

        project_description = st.text_area(
            "Project Description",
            value=existing.get("description", ""),
            placeholder="Describe the project..."
        )

        submitted = st.form_submit_button(
            "Save Project Details",
            use_container_width=True
        )

        if submitted:

            if not project_name.strip():
                st.error("Please enter a project name.")

            else:
                st.session_state.project_data = {
                    "project_name": project_name,
                    "client_name": client_name,
                    "project_manager": project_manager,
                    "start_date": str(start_date),
                    "project_status": project_status,
                    "budget": budget,
                    "progress": progress,
                    "description": project_description
                }

                st.success("Project details saved successfully!")

    if st.session_state.project_data:

        st.divider()
        st.subheader("Export Project Information")

        json_data = json.dumps(
            st.session_state.project_data,
            indent=4
        )

        st.download_button(
            "Download Project Details (JSON)",
            data=json_data,
            file_name="project_details.json",
            mime="application/json",
            use_container_width=True
        )


# --------------------------------
# DOCUMENT UPLOAD
# --------------------------------

elif page == "Document Upload":

    st.title("📂 Upload Company Documents")

    st.write(
        "Upload your project information Word document "
        "and your existing Excel report template."
    )

    st.divider()

    st.subheader("1. Project Information Document")

    source_file = st.file_uploader(
        "Upload Word document",
        type=["docx"],
        key="source_uploader"
    )

    if source_file is not None:

        st.session_state.source_doc_bytes = source_file.getvalue()
        st.session_state.source_doc_name = source_file.name

        st.success(f"Uploaded: {source_file.name}")

    elif st.session_state.source_doc_name:

        st.info(
            f"Previously uploaded: {st.session_state.source_doc_name}"
        )

    st.divider()

    st.subheader("2. Excel Report Template")

    template_file = st.file_uploader(
        "Upload Excel template",
        type=["xlsx"],
        key="template_uploader"
    )

    if template_file is not None:

        st.session_state.template_bytes = template_file.getvalue()
        st.session_state.template_name = template_file.name

        st.success(f"Uploaded: {template_file.name}")

    elif st.session_state.template_name:

        st.info(
            f"Previously uploaded: {st.session_state.template_name}"
        )

    st.divider()

    if (
        st.session_state.source_doc_bytes
        and st.session_state.template_bytes
    ):
        st.success(
            "Both documents are ready. Open AI Report Generator "
            "to create your report."
        )

    else:
        st.warning(
            "Please upload both the Word document and Excel template."
        )


# --------------------------------
# AI REPORT GENERATOR
# --------------------------------

elif page == "AI Report Generator":

    st.title("🤖 AI Report Generator")

    st.write(
        "Use your locally running Qwen AI model to analyse "
        "the project document and fill your Excel report."
    )

    st.divider()

    if not st.session_state.source_doc_bytes:

        st.warning("Please upload a Word document first.")

    elif not st.session_state.template_bytes:

        st.warning("Please upload an Excel template first.")

    else:

        st.write(
            f"**Project document:** {st.session_state.source_doc_name}"
        )

        st.write(
            f"**Excel template:** {st.session_state.template_name}"
        )

        st.divider()

        if st.button(
            "🚀 Generate AI Report",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "Reading your document..."
                ):

                    source_stream = BytesIO(
                        st.session_state.source_doc_bytes
                    )

                    document_text = extract_document_text(
                        source_stream
                    )

                if not document_text.strip():

                    st.error(
                        "No readable text was found in the Word document."
                    )

                    st.stop()

                with st.spinner(
                    "Qwen AI is analysing your project information..."
                ):

                    project = extract_project_information(
                        document_text
                    )

                if "error" in project:

                    st.error(
                        "AI extraction failed: "
                        + project["error"]
                    )

                    st.stop()

                if not isinstance(project, dict) or not project.get("project_name"):

                    st.error(
                        "The AI did not return valid project information. "
                        "Please check your source document and try again."
                    )

                    st.stop()

                with st.spinner(
                    "Filling your Excel report..."
                ):

                    template_stream = BytesIO(
                        st.session_state.template_bytes
                    )

                    output_stream = BytesIO()

                    fill_excel_template(
                        project,
                        template_stream,
                        output_stream
                    )

                    output_stream.seek(0)

                    report_bytes = output_stream.getvalue()

                safe_name = re.sub(
                    r"[^A-Za-z0-9_-]+",
                    "_",
                    project["project_name"]
                ).strip("_")

                filename = (
                    safe_name + "_AI_Completed_Report.xlsx"
                )

                st.session_state.reports.append({
                    "filename": filename,
                    "data": report_bytes,
                    "project_name": project["project_name"]
                })

                st.success("AI-generated report created successfully!")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Milestones Extracted",
                        len(project.get("milestones", []))
                    )

                with col2:
                    st.metric(
                        "Risks Extracted",
                        len(project.get("risks", []))
                    )

                st.download_button(
                    "📥 Download Completed Excel Report",
                    data=report_bytes,
                    file_name=filename,
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    use_container_width=True
                )

                st.info(
                    "Please review the generated report carefully "
                    "before sharing it."
                )

            except Exception as error:

                st.error(
                    f"Report generation failed: {error}"
                )


# --------------------------------
# GENERATED REPORTS
# --------------------------------

elif page == "Generated Reports":

    st.title("📥 Generated Reports")

    st.write(
        "View and download reports generated during this session."
    )

    st.divider()

    if not st.session_state.reports:

        st.info("No reports have been generated yet.")

    else:

        for index, report in enumerate(
            reversed(st.session_state.reports)
        ):

            st.subheader(report["project_name"])

            st.write(report["filename"])

            st.download_button(
                "Download Report",
                data=report["data"],
                file_name=report["filename"],
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                key=f"download_report_{index}"
            )

            st.divider()


# --------------------------------
# FOOTER
# --------------------------------

st.caption(
    "LocalReport AI | Offline Local AI Project Reporting Workspace"
)
