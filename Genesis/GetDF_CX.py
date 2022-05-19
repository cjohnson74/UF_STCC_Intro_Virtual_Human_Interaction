import os
from google.cloud.dialogflowcx_v3beta1.services.flows.client import FlowsClient
from google.cloud.dialogflowcx_v3beta1.services.intents.client import IntentsClient
from google.cloud.dialogflowcx_v3beta1.services.pages.client import PagesClient
import pandas
from google.cloud.dialogflowcx_v3beta1.services.agents import AgentsClient
from google.cloud.dialogflowcx_v3beta1.services.sessions import SessionsClient
from google.cloud.dialogflowcx_v3beta1.types import session

# Set credential file path here
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./credentials/genesis-redy-2b2bd0e0883e.json"


# vars for writing to excel file
fileName = 'intents.xlsx'
allRows = []
intent_names = []
agent_responses = []


def process_response(line):
    # string processing for response to copy paste into synthesia easier
    line = str(line)
    line = line[7:-2]
    line = line.replace('\\', '')
    line = line.replace('&', 'and')
    line = line.replace('\"', '')
    line += "<break time=\"2s\" />"
    return line


def process_intent_name(line):
    # string processing for intent name to make into suitable file name
    line = line.replace('\\', '')
    line = line.replace('/', '')
    line = line.replace('&', 'and')
    line = line.replace('\'', '')
    line = line.replace('\"', '')
    line = line.replace(' ', '_')
    return line


def write_intent_name_to_text_file(line):
    with open('videoName.txt', 'a') as f:
        f.write(line)
        f.write('\n')


def run_sample():
    # TODO(developer): Replace these values when running the function
    project_id = "genesis-redy"
    # For more information about regionalization see https://cloud.google.com/dialogflow/cx/docs/how/region
    location_id = "us-east1"
    # For more info on agents see https://cloud.google.com/dialogflow/cx/docs/concept/agent
    agent_id = "77fdec19-2f4c-41e4-9d38-bba201c0ac4c"
    agent = f"projects/{project_id}/locations/{location_id}/agents/{agent_id}"
    # For more information on sessions see https://cloud.google.com/dialogflow/cx/docs/concept/session
    session_id = "test-session-12345"
    texts = ["Hello"]
    # For more supported languages see https://cloud.google.com/dialogflow/es/docs/reference/language
    language_code = "en-us"

    print("GOT INTENTS!")

    # detect_intent_texts(agent, session_id, texts, language_code, project_id)
    get_flows(agent, session_id)


def get_flows(agent, session_id):

    session_path = f"{agent}/sessions/{session_id}"
    print(f"Session path: {session_path}\n")
    client_options = None
    agent_components = AgentsClient.parse_agent_path(agent)
    location_id = agent_components["location"]
    if location_id != "global":
        api_endpoint = f"{location_id}-dialogflow.googleapis.com:443"
        print(f"API Endpoint: {api_endpoint}\n")
        client_options = {"api_endpoint": api_endpoint}
    flows_client = FlowsClient(client_options=client_options)
    pages_client = PagesClient(client_options=client_options)

    response0 = flows_client.list_flows(request={"parent": agent})

    individualRow = []

    for item in response0:
        response2 = pages_client.list_pages(request={"parent": item.name})
        for page in response2:
            if (len(page.entry_fulfillment.messages) > 1):
                individualRow = []
                print("MESSAGE:")
                message = page.entry_fulfillment.messages[0].text.text[0]
                print(message)
                agent_responses.append(message)
                payload = page.entry_fulfillment.messages[1].payload
                if 'intentName' in payload:
                    print(payload['intentName'])
                    processed_name = process_intent_name(payload['intentName'])
                    intent_names.append(processed_name)
                    write_intent_name_to_text_file(processed_name)
                    individualRow.append(processed_name)
                    individualRow.append(message)
                    allRows.append(individualRow)


run_sample()
print(intent_names)
print(agent_responses)

# write to excel file
df = pandas.DataFrame(allRows)
df.to_excel(fileName, index=False, header=False)
