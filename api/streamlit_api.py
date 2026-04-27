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

    # TODO
    for line in response.iter_lines():
        if line:
            yield json.loads()

    return response

# 2 - Print answer

# 3 - Run server

if __name__ == "__main__":
    message = input("Ask anything: ")
    response = get_response_stream(message)
    print(response)

