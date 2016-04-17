import numpy as np
import json
from concurrent.futures import ProcessPoolExecutor, as_completed

class JSONSerialiser(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ProjectTask):
            return {'mean_duration': obj.mean_duration,
                    'one_sigma': obj.one_sigma,
                    'description': obj.description,
                    '__class__': 'project_sim.ProjectTask'}
        elif isinstance(obj, Project):
            return obj.tasks
        return json.JSONEncoder.default(obj)

    def decode(s):
        json_object = json.loads()
        if '__class__' in json_object:
            if json_object['__class__'] == 'project_sim.ProjectTask':
                return ProjectTask(json_object['mean_duration'], json_object['one_sigma'], json_object['description'])
        return json.JSONDecoder.decode(s)

class ProjectTask(object):
    def __init__(self, mean_duration, one_sigma, description):
        self.mean_duration = np.float64(mean_duration)
        self.one_sigma = np.float64(one_sigma)
        self.description = str(description)

class Project(object):
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def simulate(self, repeats):
        random_sequences = np.random.randn(repeats, len(self.tasks));
        for idx, task in enumerate(self.tasks):
            random_sequences[:,idx] = random_sequences[:,idx] * task.one_sigma + task.mean_duration
        durations = np.sum(random_sequences, axis=1)
        return durations, durations.mean(), durations.var();

class MonteCarloProjectScheduleSimulation(object):
    '''
    A Monte-Carlo simulation of a project's schedule 
    '''
    def __init__(self, project):
        self.project = project
        self.results = []
        self.mean_duration = 0.0
        self.results_count = 0
        self.variance_duration = 0.0

    def run_simulations(self, repeats, loops, progress):
        futures = []
        with ProcessPoolExecutor(max_workers=1) as executor:
            for loop in range(loops):
                futures.append(executor.submit(self.project.simulate, repeats))
            for loop, future in zip(range(loops), as_completed(futures)):
                new_result = future.result()
                self.results.append(new_result[0])
                n_a = self.results_count
                n_b = new_result[0].size
                delta = self.mean_duration - new_result[1]
                self.mean_duration = (n_a * self.mean_duration + n_b * new_result[1]) / (n_a + n_b)
                self.variance_duration += new_result[2] * (n_b - 1) + delta**2 * (n_a * n_b) / (n_a + n_b)
                self.results_count = n_a + n_b
                progress(repeats, loops, loop+1)

    def std_dev_duration(self):
        return np.sqrt(self.variance_duration / (self.results_count - 1))