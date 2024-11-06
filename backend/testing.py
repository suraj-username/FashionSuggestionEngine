from flask import Flask, jsonify, request
from flask_cors import CORS
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import requests
from io import BytesIO
import numpy as np
import lancedb


db = lancedb.connect("../my_lancedb")
print("Available tables:", db.table_names())

table_name = 'my_table'

def load_table():
    table_names = db.table_names()
    print("Available tables in database:", table_names)
    if table_name in table_names:
        return db.open_table(table_name)
    else:
        raise FileNotFoundError(f"Table {table_name} not found in database.")