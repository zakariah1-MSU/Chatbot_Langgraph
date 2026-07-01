import streamlit as st
from langgraph_tool_backend import chatbot, get_all_threads
from langchain_core.messages import HumanMessage, AIMessage
import uuid

#******************************Utility Functions********************************************
def get_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    st.session_state["message_history"] = []
    st.session_state["thread_id"] = get_thread_id()
    add_chat_thread(st.session_state["thread_id"])

def add_chat_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def load_conversation(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        return []
    config = {"configurable": {"thread_id": thread_id}}
    return chatbot.get_state(config=config).values.get("messages", [])
    


#******************************Session Setup********************************************
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = get_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = get_all_threads()

add_chat_thread(st.session_state["thread_id"])

#******************************UI Setup********************************************
st.sidebar.title("Chatbot")

st.sidebar.button("New Chat", on_click=reset_chat)

st.sidebar.header("My Conversations")

#st.sidebar.text(f"Thread ID: {st.session_state['thread_id']}")
for thread_id in st.session_state["chat_threads"][::-1]:
    if st.sidebar.button(f"Thread ID: {thread_id}"):
        messages = load_conversation(thread_id)
        st.session_state["thread_id"] = thread_id

        temp_message_history = []
        for message in messages:
            if isinstance(message, HumanMessage):
                temp_message_history.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                temp_message_history.append({"role": "assistant", "content": message.content})

        st.session_state["message_history"] = temp_message_history


config = {
    "configurable": {"thread_id": st.session_state["thread_id"]},
    "metadata": {
        "thread_id": st.session_state["thread_id"]
    },
    "run_name": "hish_test"
}

for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Enter your message:")

if user_input:

    st.session_state.message_history.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.text(user_input)
    

    with st.chat_message("assistant"):
        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream({"messages": HumanMessage(content=user_input)}, 
            config=config, stream_mode="messages"
            ):
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content
        ai_response = st.write_stream(ai_only_stream())

        st.session_state.message_history.append({"role": "assistant", "content": ai_response})