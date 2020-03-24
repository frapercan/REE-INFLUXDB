import json
import requests
import pendulum



# Configure the data scrapping here in the template
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

URL = "http://localhost:9999"
ORG = "US"
TOKEN = "zDxSwoznrqSipuTs2VJfrOJl-e2twnCKsraGd-K_4YKUY0c_EB9fb341_kCi0lQqz9dUx_yWYGKUqiZaI2cGOA=="
BUCKET = 'REE'

INPUT_TEMPLATE_DEMANDA_1 = {
    "request_type": "DEMANDA",
    "request_subtype": "Demanda real",
    "start_date": [2017, 1, 1, 0],
    "end_date": [2019, 12, 31, 0],
    "time_trunc": "hour",
    "measurement_unit": "KWh"
}

INPUT_TEMPLATE_DEMANDA_2 = {
    "request_type": "DEMANDA",
    "request_subtype": "Demanda prevista",
    "start_date": [2017, 1, 1, 0],
    "end_date": [2019, 12, 31, 0],
    "time_trunc": "hour",
    "measurement_unit": "KWh"
}

INPUT_TEMPLATE_PRECIOS_1 = {
    "request_type": "PRECIOS",
    "request_subtype": "PVPC (€/MWh)",
    "start_date": [2017, 1, 1, 0],
    "end_date": [2019, 12, 31, 0],
    "time_trunc": "hour",
    "measurement_unit": "€/MWh"

}

INPUT_TEMPLATE_PRECIOS_2 = {
    "request_type": "PRECIOS",
    "request_subtype": "Precio mercado spot (€/MWh)",
    "start_date": [2017, 1, 1, 0],
    "end_date": [2019, 12, 31, 0],
    "time_trunc": "hour",
    "measurement_unit": "€/MWh"
}

HTTP_API_URI = 'https://apidatos.ree.es/es/datos/'
DATABASE = "REE"
REQUEST_TYPE_URL = {'DEMANDA': 'demanda/demanda-tiempo-real',
                    'PRECIOS': 'mercados/precios-mercados-tiempo-real'}

REQUEST_TYPE = {'DEMANDA': {"Demanda real": 0, "Demanda programada": 1, "Demanda prevista": 2},
                'PRECIOS': {"PVPC (€/MWh)": 0, "Precio mercado spot (€/MWh)": 1}}
DATA_LIMIT = 600

insertion_template = {
    'measurement': 'CONSUMO',
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

def get_data_by_date_range(request_type, request_subtype,measurement_unit, start_date, end_date, time_trunc='hour', store=True):
    """
    Get historical data for specific type and time frame between to date.
    """
    print(request_type,request_subtype)
    start_date = pendulum.create(*start_date)
    end_date = pendulum.create(*end_date)
    insertion_template['tags'][request_type] = request_subtype
    next_date = start_date.add(hours=DATA_LIMIT)
    finished = False

    if store:
        client = connect()

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
        points = serialize_points(response,request_type,measurement_unit,request_subtype)
        write_api = client.write_api(write_options=SYNCHRONOUS)

        write_api.write(bucket=BUCKET, org=ORG, record=points)

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


def serialize_points(response, request_type, request_subtype, measurement_unit):
    points = []
    for i, tick in enumerate(response):
        point = Point(measurement_unit).field(request_subtype, float(tick['value'])).time(tick['datetime'])
        points.append(point)
    # Return True is operation is successful
    return points


def connect():
    """
    Connect to InfluxDB.
    """
    try:
        print('Connection to InfluxDB...')
        client = InfluxDBClient(
            url=URL,
            token=TOKEN,
            org=ORG
        )

    except Exception as e:
        print('Could not connect to InfluxDB.', e)
        return e
    else:
        print('Connection to InfluxDB successfully established.')
        return client


if __name__ == '__main__':
    get_data_by_date_range(**INPUT_TEMPLATE_PRECIOS_1)
    get_data_by_date_range(**INPUT_TEMPLATE_PRECIOS_2)
    get_data_by_date_range(**INPUT_TEMPLATE_DEMANDA_2)
    get_data_by_date_range(**INPUT_TEMPLATE_DEMANDA_1)

