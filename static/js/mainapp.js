var app = angular.module('MyApp', ['ui.bootstrap', 'ngAnimate', 'toastr']);

// Flask (the web server framework) uses Jinja for rendering HTML templates.
// Unfortunately Jinja uses {{}} to indicate locations to fill in in the
// template so this tells AngularJS to use a different set of brackets
// for model variables in the view.
app.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

app.controller('ProjectTasksController', function($scope, $http, toastr) {
    var ctrl = this;
    ctrl.tasks_list = [];

    // Use SocketIO to establish the websockets connection to the server.
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    ctrl.task_description = "";
    ctrl.task_duration = 0;
    ctrl.task_one_sigma = 0;

    ctrl.simulation = {
        current_loop: 0,
        total_loops: 100,
        mean_duration: 0,
        stddev_duration: 0
    }

    ctrl.GetTasks = function() {
        $http.get("/tasks").then(
        function success(response) {
            ctrl.tasks_list.splice(0, ctrl.tasks_list.length);
            // Need to add each task individually as there is some incompatibility with the JSON
            // list returned. Trying to use splice to insert the whole JSON list returned in one go
            // using ctrl.tasks_list.splice(0, ctrl.tasks_list.length, response.data) just puts the
            // JSON string in the array,
            response.data.forEach(function(task) {
                ctrl.tasks_list.splice(ctrl.tasks_list.length, 0, task);
            })
        },
        function fail(response) {
            toastr.error("Unable to retrieve tasks.")
        });
    };

    ctrl.AddTask = function() {
        task = {
            description: ctrl.task_description,
            mean_duration: ctrl.task_duration,
            one_sigma: ctrl.task_one_sigma
        };
        $http.post("/tasks", task).then(
        function success(response) {
            toastr.success(ctrl.task_description + " successfully added.");
            ctrl.tasks_list.splice(ctrl.tasks_list.length, 0, task);
        },
        function fail(response) {
            toastr.error("Failed to add task " + ctrl.task_description + ".");
        });
    }

    ctrl.GetTasks();

    ctrl.StartSimulation = function() {
        $http.post("/start_simulation", "").then(
            function success(response) {
                toastr.success("Simulation running.");
            },
            function fail(response) {
               toastr.error("Failed to start simulation.");
            })
    }

    socket.on('mc_simulator_progress', function(data) {
        ctrl.simulation.current_loop = data.loop
        ctrl.simulation.total_loops = data.loops
        ctrl.simulation.mean_duration = data.mean
        ctrl.simulation.stddev_duration = data.stddev
        $scope.$apply(); // Without this, the view doesn't update in sync with the data.
    })
});