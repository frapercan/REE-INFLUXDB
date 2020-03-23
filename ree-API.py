import json
import time
import asyncio
import websockets
import requests
import pendulum
import os
import pandas as pd
import copy

from influxdb import InfluxDBClient

# Configure the data scrapping here in the template
INPUT_TEMPLATE_DEMANDA_1 = {
    "request_type": "DEMANDA",
    "request_subtype": "Demanda real",
    "start_date": [2017, 1, 1, 0],
    "end_date": [2020, 2, 2, 0],
    "time_trunc": "hour"
}

INPUT_TEMPLATE_DEMANDA_2 = {
    "request_type": "DEMANDA",
    "request_subtype": "Demanda prevista",
    "start_date": [2017, 1, 1, 0],
    "end_date": [2020, 2, 2, 0],
    "time_trunc": "hour"
}

INPUT_TEMPLATE_PRECIOS_1 = {
    "request_type": "PRECIOS",
    "request_subtype": "PVPC (€/MWh)",
    "start_date": [2017, 1, 1, 0],
    "end_date": [2020, 2, 2, 0],
    "time_trunc": "hour"
}

INPUT_TEMPLATE_PRECIOS_2 = {
    "request_type": "PRECIOS",
    "request_subtype": "Precio mercado spot (€/MWh)",
    "start_date": [2017, 1, 1, 0],
    "end_date": [2020, 2, 2, 0],
    "time_trunc": "hour"
}

HTTP_API_URI = 'https://apidatos.ree.es/es/datos/'
DATABASE = "REE"
REQUEST_TYPE_URL = {'DEMANDA': 'demanda/demanda-tiempo-real',
                    'PRECIOS': 'mercados/precios-mercados-tiempo-real'}

REQUEST_TYPE = {'DEMANDA': {"Demanda real": 0, "Demanda programada": 1, "Demanda prevista": 2},
                'PRECIOS': {"PVPC (€/MWh)": 0, "Precio mercado spot (€/MWh)": 1}}
DATA_LIMIT = 600

insertion_template = {
    'measurement': '',
    'time': '',
    'fields': {
        'value': 0
    },
    'tags': {
    }
}


#
# REE Values
# https://www.ree.es/es/apidatos
#

def get_data_by_date_range(influxdb_client, request_type, request_subtype, start_date, end_date, time_trunc='hour', store=True):
    """
    Get historical data for specific type and time frame between to date.
    """
    # Create an empty list that will contain all data
    start_date = pendulum.create(*start_date)
    end_date = pendulum.create(*end_date)
    insertion_template['measurement'] = request_type
    insertion_template['tags']['type'] = request_subtype
    next_date = start_date.add(hours=DATA_LIMIT)
    finished = False

    # Loop between two dates
    while not finished:
        if next_date > end_date:
            finished = True
            next_date = end_date
        # Build url
        url = generate_url(request_type, start_date, next_date, time_trunc)
        # Request API
        json_response = requests.get(url)
        response = json.loads(json_response.text)
        response = response['included'][REQUEST_TYPE[request_type][request_subtype]]['attributes']['values']
        print("Va a cargarse hasta:" + response[0]['datetime'])
        # Data storage
        influxdb_client.write_points(serialize_points(response), database=DATABASE)
        # Update date for next iteration
        start_date = start_date.add(hours=DATA_LIMIT)
        next_date = next_date.add(hours=DATA_LIMIT)


def generate_url(data_type, start_date, end_date, time_trunc):
    url = "{0}{1}{2}".format(HTTP_API_URI, REQUEST_TYPE_URL[data_type],
                             "?start_date={start_date}&end_date={end_date}&time_trunc={time_trunc}".format(
                                 time_trunc=time_trunc, start_date=parse_time(start_date),
                                 end_date=parse_time(end_date)))
    return url


def parse_time(dt):
    try:
        return dt.to_iso8601_string()[:-9]
    except Exception as e:
        return e


def serialize_points(response):
    points = []
    for i, tick in enumerate(response):
        template = copy.deepcopy(insertion_template)

        template['time'] = tick['datetime']
        template['fields']['value'] = float(tick['value'])
        points.append(template)
    # Return True is operation is successful
    return points


def connect():
    """
    Connect to InfluxDB.
    """
    host = os.getenv('INFLUXDB_HOST', "localhost")
    port = os.getenv('INFLUXDB_PORT', 8086)
    use_ssl = os.getenv('INFLUXDB_USE_SSL', False)
    verify_ssl = os.getenv('INFLUXDB_VERIFY_SSL', False)
    username = os.getenv('INFLUXDB_USERNAME', None)
    password = os.getenv('INFLUXDB_PASSWORD', None)
    database = os.getenv('INFLUXDB_DATABASE', "REE")

    params = (host, port, username, password, database, use_ssl, verify_ssl)
    try:
        print('Connection to InfluxDB...')
        client = InfluxDBClient(*params)
    except Exception as e:
        print('Could not connect to InfluxDB.', e)
        return e
    else:
        print('Connection to InfluxDB successfully established.')
        return client


if __name__ == '__main__':
    influxdb_client = connect()
    get_data_by_date_range(influxdb_client, **INPUT_TEMPLATE_DEMANDA_2)
    get_data_by_date_range(influxdb_client, **INPUT_TEMPLATE_PRECIOS_1)
    get_data_by_date_range(influxdb_client, **INPUT_TEMPLATE_PRECIOS_2)