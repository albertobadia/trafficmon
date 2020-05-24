import requests

ROUTER_ID = 1
INTERFACE_NAME = "CLIENTES"
MKAPI_URL = "http://mkapi:5000"
MAX_PROBE_COUNT = 20

HEADERS = {"Authorization": "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImJjdG0iLCJleHAiOjE1ODkyMjI0N"
                            "TEsIm9yaWdJYXQiOjE1ODkyMjIxNTF9.nj2LC1rwo13nHA0Pl18IW4XRMXnnk4fGGaE9ONTooM0"}


def run_api(query):
    request = requests.post('http://wisp-server/api2/', json={'query': query}, headers=HEADERS)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def update_str(traffic):
    return """mutation{
                updateRouter(newRouter:{
                    id:""" + str(ROUTER_ID) + """, traffic:" """ + traffic + """ "
                }){
                    ok
                }
            }"""


def query_str():
    return """
    query{
        router(pk: """ + str(ROUTER_ID) + """){
            traffic
        }
    }"""


while True:
    traffic_points = list(run_api(query=query_str())["data"]["router"]["traffic"].split("-"))

    now_traffic = requests.get("{0}/interface/traffic?interface={1}".format(MKAPI_URL, INTERFACE_NAME)).json()

    tx = now_traffic["tx-bits-per-second"]
    rx = now_traffic["rx-bits-per-second"]
    str_traffic = "{0}/{1}".format(tx, rx)

    traffic_points.append(str_traffic)
    if traffic_points.__len__() > MAX_PROBE_COUNT:
        traffic_points.remove(traffic_points[0])

    new_str_traffic = "-".join(traffic_points)
    run_api(update_str(traffic=new_str_traffic))

    print(new_str_traffic)
