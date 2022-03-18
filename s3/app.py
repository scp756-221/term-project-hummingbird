"""
SFU CMPT 756
Sample application---music service.
"""

# Standard library modules
import logging
import sys
import csv

# Installed packages
from flask import Blueprint
from flask import Flask
from flask import request
from flask import Response

from prometheus_flask_exporter import PrometheusMetrics

import requests

import simplejson as json

# The application

app = Flask(__name__)

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'playlist process')

DB_PATH = '/data/playlist.csv'
bp = Blueprint('app', __name__)


database = {}


def load_db():
    global database
    with open(DB_PATH, 'r') as inp:
        rdr = csv.reader(inp)
        next(rdr)  # Skip header line
        for userId, songId, playlistId, id in rdr:
            database[id] = (userId, songId, playlistId)

@bp.route('/', methods=['GET'])
def list_all():
    global database
    response = {
        "Count": len(database),
        "Items":
            [{'userId': value[0], 'songId': value[1], 'playlistId': value[2], 'UUID':id}
             for id, value in database.items()]
    }
    return response

@bp.route('/health')
@metrics.do_not_track()
def health():

    return Response("healthyyyyyyyyy", status=200, mimetype="application/json")


@bp.route('/readiness')
@metrics.do_not_track()
def readiness():
    pass


@bp.route('/', methods=['POST'])
def create_playlist():
    global database
    try:
        content = request.get_json()
        UserID = content['userId']
        SongID = content['songId']
    except Exception:
        return app.make_response(
            ({"Message": "Error reading arguments"}, 400)
            )
    PlaylistID = int(database[max(database)][2]) + 1
    id = int(max(database)) + 1
    database[id] = (UserID, SongID,str(PlaylistID))
    response = {
        "UUID": id
    }
    return response

@bp.route('/<playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    global database
    check = False
    deleteList = []
    for id, value in database.items():
        userId, songId, playlistId = value[0], value[1], value[2]
        if playlistId == str(playlist_id):
            deleteList.append(id)
            check = True
    for deleteid in deleteList:
        del database[deleteid]
    if check != True:
        response = {
            "Count": 0,
            "Items":[{'userId': value[0], 'songId': value[1], 'UUID': id}
             for id, value in database.items()]
        }
        return app.make_response((response, 404))
    return {}

@bp.route('/<playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    global database
    if playlist_id in database:
        userId = None
        songId = []
        uuid = []
        for i in database:
            entry = database[i]
            
            if entry[2] == playlist_id:

                userId = entry[0]
                songId.append(entry[1])
                uuid.append(i)
        
        response = {
            "Count": 1,
            "Items":
            [{
                'userId': userId,
                'songId': songId,
                "playlistId": playlist_id,
                'UUID': uuid
            }]           
        }
    else:
        response = {
            "Count": 0,
            "Items": []
        }
        return app.make_response((response, 404))
    return response
    


# @bp.route('/<playlist_id>', methods=['GET'])
# def get_playlist():
#     pass


# @bp.route('/<playlist_id>', methods=['PUT'])
# def update_playlist():
#     pass



# All database calls will have this prefix.  Prometheus metric
# calls will not---they will have route '/metrics'.  This is
# the conventional organization.
app.register_blueprint(bp, url_prefix='/api/v1/playlist/')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        logging.error("missing port arg 1")
        sys.exit(-1)

    load_db()
    p = int(sys.argv[1])
    # Do not set debug=True---that will disable the Prometheus metrics
    app.run(host='0.0.0.0', port=p, threaded=True)