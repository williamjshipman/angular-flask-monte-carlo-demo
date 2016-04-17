import eventlet
eventlet.monkey_patch()

from flask import Flask, Response, render_template, request, make_response, jsonify
from flask_socketio import SocketIO
import project_sim
import json
from threading import Thread
import time

app = Flask(__name__, static_path='/static')
socketio = SocketIO(app)

project = project_sim.Project();
mc_simulator = None
simulation_thread = Thread()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks', methods=['POST'])
def add_task():
    data = json.loads(request.data.decode())
    task = project_sim.ProjectTask(data["mean_duration"], data["one_sigma"], data["description"])
    project.add_task(task)
    return make_response()

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return Response(response=json.dumps(
                                        project.tasks,
                                        cls=project_sim.JSONSerialiser),
                    mimetype="application/json")

def simulation_progress(repeats, loops, loop):
    progress = {'loop': loop, 'loops': loops, 'mean': mc_simulator.mean_duration, 'stddev': mc_simulator.std_dev_duration()}
    socketio.emit('mc_simulator_progress', progress)
    time.sleep(0)

@app.route('/start_simulation', methods=['POST'])
def start_simulation():
    global simulation_thread
    global mc_simulator
    if not simulation_thread.is_alive():
        mc_simulator = project_sim.MonteCarloProjectScheduleSimulation(project)
        simulation_thread = Thread(target=lambda: mc_simulator.run_simulations(100000, 100, simulation_progress))
        simulation_thread.start()
    return make_response()

if __name__ == '__main__':
    socketio.run(app, debug=True)
