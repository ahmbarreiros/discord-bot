import os
import base64
import json
import validators
from requests import post, get, put
from dotenv import load_dotenv
from validators import ValidationFailure