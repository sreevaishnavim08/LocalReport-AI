import streamlit as st

st.set_page_config(
    page_title="LocalReport AI",
    page_icon="📊",
    layout="wide"
)

st.title("📊 LocalReport AI")
st.subheader("AI-Powered Project Reporting System")

st.info(
    "Welcome to LocalReport AI. "
    "This is the public demonstration version."
)

st.warning(
    "Cloud AI is not configured yet. "
    "Your full offline AI application remains available locally."
)

st.markdown("### Features")
st.write("📁 Project document management")
st.write("📊 Project progress reporting")
st.write("📑 Excel report generation")
st.write("🤖 AI-powered project analysis — available in the offline version")

st.markdown("---")
st.caption("LocalReport AI | Project Reporting Workspace")