from flask import Flask
from flask_environments import Environments
import os
import datetime

app = Flask(__name__)
env = Environments(app)
env.from_yaml(os.path.join(os.getcwd(), 'config.yaml'))
tmp = app.config['JWT_EXPIRATION_DELTA']
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=tmp)
