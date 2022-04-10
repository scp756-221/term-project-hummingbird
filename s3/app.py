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

# DB_PATH = '/data/playlist.csv'
db = {
    "name": "http://cmpt756db:30002/api/v1/datastore",
    "endpoint": [
        "read",
        "write",
        "delete"
    ]
}
bp = Blueprint('app', __name__)

database = {}


# def load_db():
#     global database
#     with open(DB_PATH, 'r') as inp:
#         rdr = csv.reader(inp)
#         next(rdr)  # Skip header line
#         for userId, songId, playlistId, id in rdr:
#             database[id] = (userId, songId, playlistId)

@bp.route('/', methods=['GET'])
def list_all():
    # global database
    # response = {
    #     "Count": len(database),
    #     "Items":
    #         [{'userId': value[0], 'songId': value[1], 'playlistId': value[2], 'UUID':id}
    #          for id, value in database.items()]
    # }
    # return response
    pass

@bp.route('/health')
@metrics.do_not_track()
def health():
    return Response("", status=200, mimetype="application/json")


@bp.route('/readiness')
@metrics.do_not_track()
def readiness():
    return Response("", status=200, mimetype="application/json")


@bp.route('/', methods=['POST'])
def create_playlist():
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    try:
        content = request.get_json()
        user = content['user']
        song = content['song']
        song_list = song.strip().split(',')
    except Exception:
        return json.dumps({"message": "error reading arguments"})
    url = db['name'] + '/' + db['endpoint'][1]
    response = requests.post(
        url,
        json={"objtype": "playlist", "user": user, "song": song_list},
        headers={'Authorization': headers['Authorization']})
    return (response.json())

@bp.route('/<playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    headers = request.headers
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    url = db['name'] + '/' + db['endpoint'][2]
    response = requests.delete(
        url,
        params={"objtype": "playlist", "objkey": playlist_id},
        headers={'Authorization': headers['Authorization']})
    return (response.json())


@bp.route('/<playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    headers = request.headers
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    payload = {"objtype": "playlist", "objkey": playlist_id}
    url = db['name'] + '/' + db['endpoint'][0]
    response = requests.get(
        url,
        params = payload,
        headers = {'Authorization': headers['Authorization']}
    )
    return (response.json())
    

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

    # load_db()
    p = int(sys.argv[1])
    # Do not set debug=True---that will disable the Prometheus metrics
    app.run(host='0.0.0.0', port=p, threaded=True)