"""
Initialize the Flask application and set up the data ingestor and task runner.
"""

import os
from logging.handlers import RotatingFileHandler
from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool

if not os.path.exists('results'):
    os.mkdir('results')

webserver = Flask(__name__)

handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
webserver.logger.addHandler(handler)
webserver.logger.setLevel('INFO')

webserver.tasks_runner = ThreadPool(logger=webserver.logger, webserver=webserver)

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

webserver.job_counter = 1

from app import routes
