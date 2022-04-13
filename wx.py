import os
import json
import requests


def get_weather():
    url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
        "Authorization": os.getenv("WEATHER_API_KEY"),
        "locationName": "臺北市",
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = json.loads(response.text)
        weather_data = data["records"]["location"][0]["weatherElement"]
        state = weather_data[0]["time"][0]["parameter"]["parameterName"]
        rain_prob = weather_data[1]["time"][0]["parameter"]["parameterName"]
        minT = weather_data[2]["time"][0]["parameter"]["parameterName"]
        comfort = weather_data[3]["time"][0]["parameter"]["parameterName"]
        maxT = weather_data[4]["time"][0]["parameter"]["parameterName"]
    return [state, rain_prob, minT, maxT, comfort]
