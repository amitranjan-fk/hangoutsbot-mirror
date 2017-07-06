import plugins
import requests
import os.path
import sys
import json
import asyncio

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

CLIENT_ACCESS_TOKEN = 'CLIENT_ACCESS_TOKEN'

SERVICE_URL = "http://localhost:8080"


def _initialise(bot):
    plugins.register_handler(_got_a_message, type="message", priority=1)


def _got_a_message(bot, event, command):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

    request = ai.text_request()

    request.session_id = "session_id"
    # prepend = event.user.first_name + " says ";
    prepend = ""
    query = prepend + event.text

    print(query)

    request.query = query

    response = request.getresponse()

    resp = response.read().decode('utf-8')
    print(resp)
    resp_json = json.loads(resp)
    speech = resp_json["result"]["fulfillment"]["messages"][0]["speech"]
    print(speech)
    print(event.conv)
    yield from bot.coro_send_message(event.conv, speech)
    yield from interpret_action(resp_json, event, bot)


@asyncio.coroutine
def interpret_action(resp_json, event, bot):
    action = resp_json["result"]["action"]
    if (action == "modify_oncall"):
        payload = {
            "actor": event.user.first_name,
            "action": action,
            "param": {
                "with": resp_json["result"]["parameters"]["to"].upper()
            }
        }

        print(payload)
        response = requests.post(SERVICE_URL, json.dumps(payload))

        service_response = response.json()
        print(json.dumps(service_response))

        return service_response

    elif (action == "init_qtr_plan"):
        # if (event.user.first_name == "Ankur"):
        conv_list = bot.memory.get_by_path(["convmem"])  # grab all conversations
        for conv_id in conv_list:
            qtr = resp_json["result"]["parameters"]["quarter"]
            msg = "Hi, please share your leave plan for " + qtr
            yield from bot.coro_send_message(conv_id, msg)

        headers = {
            "content-type": 'application/json'
        }

        payload = {
            "actor": event.user.first_name.upper(),
            "action": action,
            "param": {
                "quarter": resp_json["result"]["parameters"]["quarter"]
            }
        }

        print(payload)
        response = requests.post(SERVICE_URL, data=json.dumps(payload), headers=headers)

        service_response = response.text
        print (service_response)
        return service_response

    elif (action == "modify_leave"):

        headers = {
            "content-type": 'application/json'
        }

        payload = {
            "actor": event.user.first_name.upper(),
            "action": action,
            "param": {
                "period": resp_json["result"]["parameters"]["date-period"]
            }
        }
        print(payload)
        response = requests.post(SERVICE_URL, data=json.dumps(payload), headers=headers)

        service_response = response.text
        print(service_response)

        yield from bot.coro_send_message(event.conv, service_response)
        return service_response

    elif (action == "fetch_tasks"):

        headers = {
            "content-type": 'application/json'
        }

        payload = {
            "actor": event.user.first_name.upper(),
            "action": action,
            "param": {
                "period": resp_json["result"]["parameters"]["date-period"],
                "date": resp_json["result"]["parameters"]["date"],
                "person": resp_json["result"]["parameters"]["person"].upper()
            }
        }
        print(json.dumps(payload))
        response = requests.post(SERVICE_URL, data=json.dumps(payload), headers=headers)

        service_response = response.text
        print (service_response)

        yield from bot.coro_send_message(event.conv, service_response)
        return service_response

    elif (action == "get_qtr_plan"):

        headers = {
            "content-type": 'application/json'
        }

        payload = {
            "actor": event.user.first_name.upper(),
            "action": action,
            "param": {
                # "period": resp_json["result"]["parameters"]["date-period"],
                # "date": resp_json["result"]["parameters"]["date"],
            }
        }
        print(json.dumps(payload))
        response = requests.post(SERVICE_URL, data=json.dumps(payload), headers=headers)

        service_response = response.text
        print (service_response)

        yield from bot.coro_send_message(event.conv, service_response)
        return service_response

    elif (action == "fetch_oncall"):

        headers = {
            "content-type": 'application/json'
        }

        payload = {
            "actor": event.user.first_name.upper(),
            "action": action,
            "param": {
                "period": resp_json["result"]["parameters"]["date-period"]
            }
        }
        print(json.dumps(payload))
        response = requests.post(SERVICE_URL, data=json.dumps(payload), headers=headers)

        service_response = response.text
        print (service_response)

        yield from bot.coro_send_message(event.conv, service_response)
        return service_response

    elif (action == "get_bandwidth"):

        headers = {
            "content-type": 'application/json'
        }

        payload = {
            "actor": event.user.first_name.upper(),
            "action": action,
            "param": {
            }
        }
        print(json.dumps(payload))
        response = requests.post(SERVICE_URL, data=json.dumps(payload), headers=headers)

        service_response = response.text
        print (service_response)

        yield from bot.coro_send_message(event.conv, service_response)
        return service_response

    return False