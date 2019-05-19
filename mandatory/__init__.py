from flask import Flask
import os

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['vcf', 'json'])

import mandatory.views