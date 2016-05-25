# coding=utf-8
from __future__ import print_function
import sys

from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy import func

from datetime import *
from db import *

import json
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://remote_root:<password>@1@13.79.157.111:3306/urbansafety'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 1800
db.init_app(app)


@app.route('/houses', methods=['GET'])
def get_info():

    address = ''
    if request.args.get('address') != None:
        address = request.args.get('address').encode('utf-8')

    # Geocoding #

    geocoder_response = requests.get('https://geocode-maps.yandex.ru/1.x/?format=json&geocode=' + address)
    pos = json.loads(geocoder_response.text)['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
    lat = float(pos.split(' ')[0])
    lng = float(pos.split(' ')[1])

    sql_query = '''SELECT id
                FROM areas
                WHERE mbrcontains(areas.coordinates, ST_GeomFromText('POINT(%(lat)f %(lng)f)')) = 1''' % {
                    'lat': lat,
                    'lng': lng
                }
    area_id = db.engine.execute(text(sql_query)).fetchall()[0][0]
    print(area_id, file=sys.stderr)

    # Getting crime rate #

    murders_number = kyiv_crimes_new.query.join(
        crime_types, kyiv_crimes_new.crime_type_id == crime_types.id
    ).join(
        main_crime_types, crime_types.main_crime_type_id == main_crime_types.id
    ).join(
        global_crime_types, main_crime_types.global_crime_type_id == global_crime_types.id
    ).add_columns(
        kyiv_crimes_new.lat, kyiv_crimes_new.lng, global_crime_types.name
    ).filter(
        (kyiv_crimes_new.area_id == area_id) & (global_crime_types.id == 2)
    ).count()

    murder_rate = murders_number * (100000.0 / areas.query.filter(areas.id == area_id).one().population)

    bulgary_number = kyiv_crimes_new.query.join(
        crime_types, kyiv_crimes_new.crime_type_id == crime_types.id
    ).join(
        main_crime_types, crime_types.main_crime_type_id == main_crime_types.id
    ).join(
        global_crime_types, main_crime_types.global_crime_type_id == global_crime_types.id
    ).add_columns(
        kyiv_crimes_new.lat, kyiv_crimes_new.lng, global_crime_types.name
    ).filter(
        (kyiv_crimes_new.area_id == area_id) & (global_crime_types.id == 6)
    ).count()

    bulgary_rate = bulgary_number * (100000.0 / areas.query.filter(areas.id == area_id).one().population)

    crimes = kyiv_crimes_new.query.join(
        crime_types, kyiv_crimes_new.crime_type_id == crime_types.id
    ).join(
        main_crime_types, crime_types.main_crime_type_id == main_crime_types.id
    ).join(
        global_crime_types, main_crime_types.global_crime_type_id == global_crime_types.id
    ).add_columns(
        kyiv_crimes_new.id, global_crime_types.weight
    ).filter(
        ((kyiv_crimes_new.area_id == area_id) & (global_crime_types.weight != None))
    ).all()

    crime_rate = 0
    for crime in crimes:
        if crime[2] != None:
            crime_rate += float(crime[2])

    crime_rate /= 6
    crime_rate *= (100000.0 / areas.query.filter(areas.id == area_id).one().population)
    print(crime_rate, file=sys.stderr)

    # Getting transit #

    sql_query = '''SELECT AVG(transit.time_transit)
                FROM transit
                JOIN areas
                ON mbrcontains(areas.coordinates, transit.point_to) = 1 AND areas.id = 10
                WHERE transit.area_id = %(area_id)i''' % {
                    'area_id': area_id
                }

    cbd_time = 0
    if area_id != 9:
        cbd_time = int(db.engine.execute(text(sql_query)).fetchall()[0][0])
    else:
        cbd_time = 41

    response = {
        "title": address,
        "position": {
          "lat": lng,
          "lng": lat
        },
        'crime': {
            'main': crime_rate,
            'sub': [murder_rate, bulgary_rate, 0]
        },
        'transport': {
            'main': cbd_time,
            'sub': [cbd_time]
        }
      }

    return Response(response=json.dumps(response, indent=3), status=200, mimetype="application/json")


@app.route('/heatmap', methods=['GET'])
def get_heatmap():
    lat = 0
    lng = 0
    if request.args.get('lat') != None:
        lat = float(request.args.get('lat'))
    if request.args.get('lng') != None:
        lng = float(request.args.get('lng'))

    sql_query = '''SELECT id
                FROM areas
                WHERE mbrcontains(areas.coordinates, GeomFromText('POINT(%(lat)f %(lng)f)')) = 1''' % {
                    'lat': lng,
                    'lng': lat
                }
    area_id = db.engine.execute(text(sql_query)).fetchall()[0][0]

    print(area_id, file=sys.stderr)

    sql_query = '''SELECT ST_X(point_to), ST_Y(point_to), time_transit
                FROM transit
                WHERE area_id = %(area_id)i AND time_transit != -1''' % {
                    'area_id': area_id
                }
    points = []
    for point in db.engine.execute(text(sql_query)).fetchall():
        points.append({'lat': point[0], 'lng': point[1], 'weight': point[2]})

    return Response(response=json.dumps(points, indent=3), status=200, mimetype="application/json")

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5999, debug=True, threaded=True)
