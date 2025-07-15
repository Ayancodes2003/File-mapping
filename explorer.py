import json
import streamlit as st

st.set_page_config(layout="wide", page_title="Legal Citation Explorer")

# Load data
with open("data/reference_map.json") as f:
    reference_map = json.load(f)

with open("data/inverted_map.json") as f:
    inverted_map = json.load(f)

all_files = list(reference_map.keys())
all_citations = list(inverted_map.keys())

# Sidebar controls
st.sidebar.title("📚 Explorer Options")
mode = st.sidebar.radio("Select Mode", ["Browse by File", "Browse by Case ID"])

if mode == "Browse by File":
    selected_file = st.sidebar.selectbox("Choose a file", sorted(all_files))

    st.header(f"📄 File: `{selected_file}`")

    references = reference_map[selected_file]["references"]
    resolved = reference_map[selected_file]["resolved"]

    st.subheader("🔗 References Made by This File")
    if references:
        for ref in references:
            status = resolved.get(ref)
            if status:
                st.markdown(f"- ✅ **{ref}** → `{status}`")
            else:
                st.markdown(f"- ❌ **{ref}** (unresolved)")
    else:
        st.info("No citations found in this file.")

elif mode == "Browse by Case ID":
    selected_case = st.sidebar.selectbox("Choose a case ID", sorted(all_citations))

    st.header(f"📌 Case ID: `{selected_case}`")
    files = inverted_map[selected_case]

    st.subheader("📂 Files that Cite This Case")
    for f in files:
        st.markdown(f"- {f}")
