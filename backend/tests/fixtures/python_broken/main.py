import os
from fastapi import FastAPI
key = os.environ['SECRET_KEY']
app = FastAPI()
