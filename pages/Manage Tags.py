import streamlit as st
from db import Tags

# --- Helper functions ---
def delete_tag(tag_id: int):
    Tags.delete().where(Tags.id == tag_id).execute()

def delete_tag_and_refresh(tag_id: int):
    delete_tag(tag_id)
    st.rerun()

@st.dialog("Add Tag")
def add_tag_dialog_open():
    tag = st.text_input("Tag Name")
    if tag:
        if st.button("Add", key="confirm-add-tag"):
            Tags.create(name=tag.strip())
            st.rerun()

# --- UI ---
st.title("🧩 Manage Tags")

st.button("➕ Add Tag", key="open-add-tag-dialog", on_click=add_tag_dialog_open)

tags = Tags.select()

if tags:
    for tag in tags:
        with st.container(border=True):
            col1, col2, col3 = st.columns([6, 1, 1], gap="medium")
            col1.write(f"{tag.name}")
            if col3.button("🗑️", key=f"delete-{tag.id}"):
                delete_tag_and_refresh(tag.id)
else:
    st.info("No tags found. Please add a tag to get started.")
