import streamlit as st
import requests

# ---------------------------
# Config
# ---------------------------
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Notes App", layout="centered")
st.title("📝 AI Notes App")

# ---------------------------
# Session State Init
# ---------------------------
if "title" not in st.session_state:
    st.session_state.title = ""

if "content" not in st.session_state:
    st.session_state.content = ""

# ---------------------------
# Add Note (FORM)
# ---------------------------
st.header("➕ Add a New Note")

with st.form("note_form", clear_on_submit=True):
    title = st.text_input("Title")
    content = st.text_area("Content")

    submitted = st.form_submit_button("Add Note")

    if submitted:
        if title and content:
            response = requests.post(
                f"{BASE_URL}/add",
                json={"title": title, "content": content}
            )

            if response.status_code == 200:
                st.success("✅ Note added successfully!")
                st.rerun()
            else:
                st.error(f"❌ {response.json().get('detail')}")
        else:
            st.warning("⚠️ Please fill all fields")

# ---------------------------
# Fetch Notes
# ---------------------------
st.header("📚 All Notes")

try:
    response = requests.get(f"{BASE_URL}/notes")

    if response.status_code == 200:
        notes = response.json()

        if notes:
            for note in notes:
                st.markdown("---")

                col1, col2 = st.columns([5, 1])

                with col1:
                    st.markdown(f"### {note['title']}")
                    st.write(note['content'])

                with col2:
                    if st.button("❌", key=f"del_{note['title']}"):
                        del_res = requests.delete(
                            f"{BASE_URL}/delete/{note['title']}"
                        )

                        if del_res.status_code == 200:
                            st.success(f"Deleted '{note['title']}'")
                            st.rerun()
                        else:
                            st.error("Delete failed")

        else:
            st.info("No notes yet")

    else:
        st.error("Failed to fetch notes")

except Exception as e:
    st.error("⚠️ Backend not running or unreachable")

# ---------------------------
# 🤖 AI AGENT SECTION
# ---------------------------
st.markdown("---")
st.header("🤖 Ask AI Agent")

# Input for user query
query = st.text_input("Ask something about your notes")

# Button to trigger agent
if st.button("Ask Agent"):
    if query:
        try:
            response = requests.get(
                f"{BASE_URL}/agent",
                params={"query": query}
            )

            if response.status_code == 200:
                answer = response.json().get("response", "")

                st.success("🧠 Agent Response")
                st.markdown("### ✨ Answer")
                st.write(answer)

            else:
                st.error("❌ Agent request failed")

        except Exception:
            st.error("⚠️ Backend or Ollama not running")

    else:
        st.warning("⚠️ Please enter a question")