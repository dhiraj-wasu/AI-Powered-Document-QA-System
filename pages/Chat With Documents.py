import asyncio
from typing import Literal, Optional, TypedDict, Union
from anyio import sleep
import streamlit as st
from constants import RESPOND_TO_MESSAGE_SYSTEM_PROMPT
from db import DocumentInformationChunks, set_openai_api_key, db
from peewee import SQL

if db.is_closed():
    db.connect()

st.set_page_config(page_title="Chat With Documents")
st.title("Chat With Documents")

class Message(TypedDict):
    role: Union[Literal["user"], Literal["assistant"]]
    content: str
    references: Optional[list[str]]

if "messages" not in st.session_state:
    st.session_state["messages"] = []

def push_message(message: Message):
    st.session_state["messages"].append(message)

async def send_message(input_message: str):
    related_document_information_chunks: list[str] = []

    try:
        with db.atomic():
            set_openai_api_key()
            result = DocumentInformationChunks.select().order_by(
                SQL("embedding <-> ai.openai_embed('text-embedding-3-small', %s)")
            ).params(input_message).limit(5)

            for row in result:
                related_document_information_chunks.append(row.chunk)
    except Exception as e:
        st.error(f"Error retrieving chunks: {e}")
        return

    push_message({
        "role": "user",
        "content": input_message,
        "references": related_document_information_chunks
    })

    total_retries = 0
    while True:
        try:
            messages = ",\n".join([
                f"jsonb_build_object('role', '{msg['role']}', 'content', '{msg['content']}')"
                for msg in st.session_state["messages"]
            ])

            prompt = RESPOND_TO_MESSAGE_SYSTEM_PROMPT.replace("{{knowledge}}", "\n".join([
                f"{i+1}. {chunk}" for i, chunk in enumerate(related_document_information_chunks)
            ]))

            with db.atomic():
                set_openai_api_key()
                response = db.execute_sql(f"""
                    SELECT
                        ai.openai_chat_complete (
                            'gpt-4o-mini-2024-07-18',
                            jsonb_build_array(
                                jsonb_build_object('role', 'system', 'content', %s),
                                {messages}
                            )
                        ) -> 'choices' -> 0 -> 'message' ->> 'content';
                """, (prompt,)).fetchone()[0]

            if not response:
                break

            push_message({
                "role": "assistant",
                "content": response,
                "references": None
            })
            print(f"Generated response: {response}")
            break

        except Exception as e:
            total_retries += 1
            if total_retries > 5:
                st.error(f"Failed to generate a response after multiple retries: {e}")
                break
            await sleep(1)
            print(f"Retrying... ({total_retries}) Error: {e}")

    st.rerun()

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["references"]:
            with st.expander("References"):
                for reference in message["references"]:
                    st.write(reference)

input_message = st.chat_input("Say something")
if input_message:
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.run_until_complete(send_message(input_message))
    event_loop.close()
