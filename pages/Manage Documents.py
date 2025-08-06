import asyncio
from io import BytesIO
from itertools import chain
from anyio import sleep
from openai import BaseModel
import streamlit as st
import fitz  # PyMuPDF for PDF parsing
from constants import CREATE_FACT_CHUNKS_SYSTEM_PROMPT, GET_MATCHING_TAGS_SYSTEM_PROMPT
from db import DocumentInformationChunks, DocumentTags, Tags, db, Documents, set_openai_api_key
from peewee import SQL, JOIN
from utils import find

# Page config
st.set_page_config(page_title="Manage Documents")
st.title("Manage Documents")

# Constants
IDEAL_CHUNK_LENGTH = 4000

# Helper: delete document by ID
def delete_document(document_id: int):
    Documents.delete().where(Documents.id == document_id).execute()

# Model for OpenAI response (chunks)
class GeneratedDocumentInformationChunks(BaseModel):
    facts: list[str]

# Async chunk generation using OpenAI
async def generate_chunks(index: int, pdf_text_chunk: str):
    total_retries = 0
    while True:
        try:
            with db.atomic():
                set_openai_api_key()
                response = db.execute_sql(f"""
                    SELECT
                    ai.openai_chat_complete (
                        'gpt-4o-mini-2024-07-18',
                        jsonb_build_array(
                            jsonb_build_object('role', 'system', 'content', %s),
                            jsonb_build_object('role', 'user', 'content', %s)
                        )
                    ) -> 'choices' -> 0 -> 'message' ->> 'content';
                """, (CREATE_FACT_CHUNKS_SYSTEM_PROMPT, pdf_text_chunk)).fetchone()[0]

            document_information_chunks = GeneratedDocumentInformationChunks.model_validate_json(response).facts
            print(f"✅ Generated {len(document_information_chunks)} facts for chunk {index}.")
            return document_information_chunks

        except Exception as e:
            total_retries += 1
            if total_retries > 5:
                raise e
            await sleep(1)
            print(f"⏳ Retrying chunk {index}... Error: {e}")

# Model for OpenAI response (tags)
class GeneratedMatchingTags(BaseModel):
    tags: list[str]

# Async tag matching using OpenAI
async def get_matching_tags(pdf_text: str):
    tags_result = Tags.select()
    tags = [tag.name.lower() for tag in tags_result]
    if not tags:
        return []

    total_retries = 0
    while True:
        try:
            with db.atomic():
                set_openai_api_key()
                response = db.execute_sql(f"""
                    SELECT
                    ai.openai_chat_complete (
                        'gpt-4o-mini-2024-07-18',
                        jsonb_build_array(
                            jsonb_build_object('role', 'system', 'content', %s),
                            jsonb_build_object('role', 'user', 'content', %s)
                        )
                    ) -> 'choices' -> 0 -> 'message' ->> 'content';
                """, (
                    GET_MATCHING_TAGS_SYSTEM_PROMPT.replace("{{tags_to_match_with}}", str(tags)),
                    pdf_text
                )).fetchone()[0]

            matching_tag_names = GeneratedMatchingTags.model_validate_json(response).tags
            matching_tag_ids = []

            for tag_name in matching_tag_names:
                matching_tag = find(lambda tag: tag.name.lower() == tag_name.lower(), tags_result)
                if matching_tag:
                    matching_tag_ids.append(matching_tag.id)
                else:
                    raise Exception(f"Tag {tag_name} not found in database.")

            print(f"🏷️  Matched tags: {matching_tag_names}")
            return matching_tag_ids

        except Exception as e:
            total_retries += 1
            if total_retries > 5:
                raise e
            await sleep(1)
            print(f"⏳ Retrying tag match... Error: {e}")
