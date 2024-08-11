import numpy as np
import logging
from pymongo import MongoClient
from config.config import Envs

client = MongoClient(Envs.MongoUrl)
db = client['sports'] 
collection = db['matches']
temp_codes_collection = db['temp_codes']
users_collection = db['users']

def load_data(user_id):
    collection_name = f'matches_{user_id}'
    user_collection = db[collection_name]
    data = list(user_collection.find())
    X = []
    y = []
    for item in data:
        if 'team1_features' in item and 'team2_features' in item:
            combined_features = item['team1_features'] + item['team2_features']
            X.append(combined_features)
            y.append(item['result'])
    X = np.array(X)
    y = np.array(y)
    
    logging.info(f"Data loaded. X shape: {X.shape}, y shape: {y.shape}")
    
    return X, y

# Otras funciones de manejo de datos relacionadas pueden ir aquí...
