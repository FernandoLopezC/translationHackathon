import logging
import os
import sys
from flask import Flask

app = Flask(__name__)

app.secret_key = 'the random string'


logging.basicConfig(filename='logs/translationLogs.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


from app import routes

