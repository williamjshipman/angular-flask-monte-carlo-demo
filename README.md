# AngularJS and Flask demo with a Monte-Carlo simulation

This is a demo of using Flask to provide a web server that runs Monte-Carlo simulations and returns
the results to a frontend built on AngularJS.

## Setup

You'll need to install Flask, Flask-SocketIO, eventlet and their dependencies.
If you're using Anaconda then

    conda install flask

Flask-SocketIO and eventlet both get installed with pip:

   pip install eventlet
   pip install Flask-SocketIO

After that, just run

   python app.py

The web server should start serving the site at http://localhost:5000
