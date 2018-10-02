import sys
sys.path.append('ropod_common/pyre_communicator')

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from threading import Lock
import time
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

from pyre_communicator.base_class import PyreBaseCommunicator

thread = None
thread_lock = Lock()

def background_thread():
    pyre = PyreBaseCommunicator("web_gui", ['ROPOD'], ['DATA_QUERY'], verbose=False)
    socketio.sleep(1)
    while True:
        peers = pyre.peers()
        peers_list = {}
        for p in peers:
            pdict = {}
            pdict["name"] = pyre.peer_directory[p]
            pdict["uuid"] = str(p);
            pdict["endpoint"] = pyre.peer_address(p)
            peers_list[str(p)] = pdict
        if (len(peers_list) > 0):
            socketio.emit('zyre_peers', {'data':json.dumps(peers_list)})

        groups = pyre.peer_groups()
        gdict = {}
        for g in groups:
            gpeers = pyre.peers_by_group(g)
            gdict[g] = []
            for p in gpeers:
                gdict[g].append(pyre.peer_directory[p])
        if (len(gdict) > 0):
            socketio.emit('zyre_groups', {'data':json.dumps(gdict)})

        socketio.sleep(1)


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)

if __name__ == '__main__':
    socketio.run(app)
