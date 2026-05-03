import requests
import json
import streamlit as stlit
from pprint import pprint

AGENT_ID = "api_agent_os"
ENDPOINT = f"http://localhost:7777/agents/{AGENT_ID}/runs"

# 1 - Connection with Agno (SERVER)

def get_response_stream(message: str):
    response = requests.post(
    url = ENDPOINT,
    data = {
        "message": message,
        "stream": "true"
    },
    stream=True
    )

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    # After getting my response, I want to print it.
    # The type is a requestlit.models.Response, which can be iterated over.
    # Each line can be printed with a loop

    buffer = ""
    for line in response.iter_lines():
        if not line:
            continue
        
        #print(f"Raw: {line}")
        line_str = line.decode('utf-8').strip()

        # Agno sends 'event: Name' followed by 'data: { ... }'
        # We only care about the lines starting with 'data:' 
        if line_str.startswith('data: '):
            content = line_str[6:].strip()
            if content == "[DONE]":
                break
            buffer = content # Start of a new JSON object
        elif buffer:
            # If we already have something in the buffer, append this line
            buffer += line_str

        # Try to parse the buffer if it looks complete
        if buffer.endswith('}'):
            try:
                event = json.loads(buffer)
                yield event
                buffer = "" # Clear buffer after successful yield
            except json.JSONDecodeError:
                # Still incomplete, wait for more lines
                continue            

# 2 - StreamLit

stlit.set_page_config(page_title="Agent Chat PDF")

stlit.title("Agent Chat PDF")


# 2.1 - Show History on page

if "messages" not in stlit.session_state:
    stlit.session_state.messages = []

# 2.2 - Show History
for msg in stlit.session_state.messages:
    with stlit.chat_message(msg["role"]):
        if msg["role"] == "assistant" and msg.get("process"):
            with stlit.expander(label="Process", expanded=False):
                stlit.json(msg["process"])
        stlit.markdown(msg["content"])


# 2.2 - Get user input
if prompt := stlit.chat_input("Type your message..."):
    # Add your message to state
    stlit.session_state.messages.append({"role": "user", "content": prompt})
    with stlit.chat_message("user"):
        stlit.markdown(prompt)

    with stlit.chat_message("assistant"):
        response_placeholder = stlit.empty()
        full_response = ""
    
    # process streaming
    for event in get_response_stream(prompt):
        event_type = event.get("event", "")
        
        # Initiate tool call
        if event_type == "ToolCallStarted":
            tool_name = event.get("tool", {}).get("tool_name")
            with stlit.status(f"Executando {tool_name}...", expanded=True):
                stlit.json(event.get("tool", {}).get("tool_args", {}))

        # Resoibse content
        elif event_type == "RunContent":
            content = event.get("content", "")
            if content:
                full_response += content
                response_placeholder.markdown(full_response + "▌")
    
    response_placeholder.markdown(full_response)

    # save response on state
    stlit.session_state.messages.append({
            "role": "assistant",
            "content": full_response
        })