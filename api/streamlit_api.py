import requests
import json
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
    # The type is a request.models.Response, which can be iterated over.
    # Each line can be printed with a loop

    buffer = ""
    for line in response.iter_lines():
        if not line:
            continue
        
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

# 2 - Print answer

def print_streaming_response(message: str):
    for event in get_response_stream(message):
        event_type = event.get("event", "")
        print(event_type)

# 3 - Run server

if __name__ == "__main__":
    while True:
        message = input("Ask anything: ")
        print_streaming_response(message)

