import googlemaps
from datetime import datetime
import json
import MySQLdb

db = MySQLdb.connect(host="13.79.157.111",    # your host, usually localhost
                     user="remote_root",         # your username
                     passwd="UrbanSafety@1",  # your password
                     db="urbansafety")        # name of the data base

cur = db.cursor()

gmaps = googlemaps.Client(key='AIzaSyD30ToSvoDFPOfe95Cg8nBMNIjB4mNAYis')

arrival_time = datetime(2016, 5, 16, 9, 30)

sql_query = 'SELECT id, ST_X(ST_Centroid(coordinates)), ST_Y(ST_Centroid(coordinates)), ST_AsText(ST_Centroid(coordinates)) FROM areas'
cur.execute(sql_query)
centroids = cur.fetchall()

for centroid in centroids:
    area_id = centroid[0]
    start_lat = centroid[1]
    start_lng = centroid[2]
    point = centroid[3]

    lng = 50.334915
    while lng <= 50.536322:
        lat = 30.363247
        while lat <= 30.834887:
            sql_query = '''SELECT mbrcontains(regions.polygon, ST_GeomFromText('POINT(%(lat)f %(lng)f)'))
                        FROM regions
                        WHERE id = 1''' % {
                            'lat': lat,
                            'lng': lng
                        }

            cur.execute(sql_query)
            isInKyiv = cur.fetchone()[0]

            time_transit = 0
            if isInKyiv == 1:
                directions_result = gmaps.directions(str(start_lng) + ', ' + str(start_lat),
                                         str(lng) + ', ' + str(lat),
                                         mode='transit',
                                         arrival_time=arrival_time)
                try:
                    time_transit = int(round(directions_result[0]['legs'][0]['duration']['value'] / 60.0))
                except:
                    time_transit = -1

            sql_query = '''INSERT INTO transit(area_id, point_from, point_to, time_transit)
                        VALUES (%(area_id)i, ST_GeomFromText('POINT(%(start_lat)f %(start_lng)f)'),
                        ST_GeomFromText('POINT(%(lat)f %(lng)f)'), %(time_transit)i)''' % {
                            'area_id': area_id,
                            'start_lat': start_lat,
                            'start_lng': start_lng,
                            'lat': lat,
                            'lng': lng,
                            'time_transit': time_transit
                        }
            print lat, lng
            cur.execute(sql_query)
            db.commit()
            lat += (30.834887 - 30.363247) / 15.0
        print 1
        lng += (50.536322 - 50.334915) / 15.0

db.close()
