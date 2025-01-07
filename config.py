# config.py
import os

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:1406@localhost:5432/postgres"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
