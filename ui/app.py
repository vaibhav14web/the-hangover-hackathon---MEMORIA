import os
import requests
import streamlit as st

st.set_page_config(
    page_title="Codebase Oracle",
    page_icon="🔮",
    layout="centered"
)

# Custom Premium Styling
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top right, #0d0b18, #05040a, #010103);
        color: #e0def4;
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
    }
    .badge {
        display: inline-block;
        background: linear-gradient(135deg, #4c3ba8, #2c9b65);
        color: #ffffff;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        margin-right: 8px;
        margin-top: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Codebase Oracle")
st.subheader("Forensic reasoning over FastAPI's architecture")
st.write("---")

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Collapsible Repository Management Section
with st.expander("⚙️ Repository Management & Ingestion"):
    st.markdown("Provide a GitHub repository URL to import its PR history and code AST directly into Cognee.")
    import_url = st.text_input(
        "Enter GitHub Repository URL:",
        placeholder="e.g. https://github.com/tiangolo/fastapi"
    )
    col1, col2 = st.columns(2)
    with col1:
        import_button = st.button("Ingest PR & Code History")
    with col2:
        check_button = st.button("Check Ingestion Status")
        
    if import_button and import_url:
        with st.spinner("Initializing background ingestion..."):
            try:
                resp = requests.post(
                    f"{API_BASE_URL}/repositories/import",
                    json={"repo_url": import_url},
                    timeout=10
                )
                if resp.status_code == 202:
                    st.success("Ingestion started in the background!")
                else:
                    st.error("Failed to start ingestion.")
            except Exception as e:
                st.error(f"Error starting ingestion: {e}")
                
    if check_button:
        try:
            status_resp = requests.get(f"{API_BASE_URL}/repositories/status", timeout=10)
            if status_resp.status_code == 200:
                data = status_resp.json()
                st.info(f"**Status**: `{data['status']}` | **Details**: {data['details']}")
            else:
                st.error("Could not fetch status.")
        except Exception as e:
            st.error(f"Status check error: {e}")

st.write("---")

# Single question input form
with st.form(key="query_form"):
    user_input = st.text_input(
        "Ask a question about FastAPI's architecture...",
        placeholder="e.g. Why did FastAPI migrate to Pydantic v2?"
    )
    submit_button = st.form_submit_button(label="Consult Oracle")

if submit_button and user_input:
    with st.spinner("Oracle is tracing codebase decisions..."):
        try:
            resp = requests.post(
                f"{API_BASE_URL}/query",
                json={"query": user_input},
                timeout=60
            )
            if resp.status_code == 200:
                data = resp.json()
                if "error" in data:
                    st.error("Query failed, please try again")
                else:
                    st.markdown("### Answer")
                    st.write(data["answer"])
                    
                    # Citations
                    citations = data.get("citations", [])
                    if citations:
                        st.write("")
                        st.markdown("**Sources:**")
                        citation_html = ""
                        for cit in citations:
                            label = cit.get("label", "")
                            if label.startswith("PR #"):
                                badge_text = f"Source: {label}"
                            else:
                                badge_text = f"Source: {label}"
                            citation_html += f'<span class="badge">{badge_text}</span>'
                        st.markdown(citation_html, unsafe_allow_html=True)
                    
                    # Collapsible Evidence Section
                    evidence = data.get("evidence", "")
                    if evidence:
                        with st.expander("🔍 View Context Evidence"):
                            st.text(evidence)
            else:
                st.error("Query failed, please try again")
        except Exception:
            st.error("Query failed, please try again")
