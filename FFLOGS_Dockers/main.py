import mysql.connector
from mysql.connector import Error
import pandas as pd
import requests
import warnings
from fastapi import FastAPI
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
import os

warnings.filterwarnings("ignore")

# Creating a FastAPI instance
app = FastAPI(
    title="Final Fantasy XIV",  # Title of the API
    description="Find where you need to workout to kill your boss",  # Description of the API
    version="0.1.0",  # Version of the API
)

# ATTENTION - CONNEXION MYSQL - A METTRE EN SECRET PLUS TARD
#user = 'root'
#password = 'root'
#host = 'mysql_projectfflogs'
#port = 3305
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
host = os.environ.get("MYSQL_HOST") 
port = int(os.environ.get("MYSQL_PORT"))

# ATTENTION - CONNEXION MongoDB - A METTRE EN SECRET PLUS TARD
#host_mongo = "mongo_projectfflogs"
#port_mongo = 27018
#user_mongo = 'admin'
#password_mongo = 'root'
user_mongo = os.environ.get("MONGO_USER")
password_mongo = os.environ.get("MONGO_PASSWORD")
host_mongo = os.environ.get("MONGO_HOST") 
port_mongo = int(os.environ.get("MONGO_PORT"))

# API FFLOGS V2 - ATTENTION DONNER A METTRE DANS DES VARIABLES d'ENVIRONEMENT
token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5ODUxMThjYi1lMjg1LTRmNjUtOTA4Yi05YzM0Njc5ZTNjMGQiLCJqdGkiOiI5N2E1MDA3ZDc0YjQ0ZDNkMzYyNmVlMTM5Nzg1YmZjNmU0ZjFlY2MzZjYyOTBlYmE2NmU3YjY2OTAyMzQyMDQ2YTk4MDhmYmNiY2JmNTAxOSIsImlhdCI6MTY3NDg0MTUwMS42NDM2OSwibmJmIjoxNjc0ODQxNTAxLjY0MzY5NSwiZXhwIjoxNzA1OTQ1NTAxLjYzNTAzOSwic3ViIjoiIiwic2NvcGVzIjpbInZpZXctdXNlci1wcm9maWxlIiwidmlldy1wcml2YXRlLXJlcG9ydHMiXX0.laQPizAIA3WDSxsVJbtsZru0YKiXHs_hn175UwnxssAbY_PGSJPdRv-6ga_njoSBkQzn7nQZ8DIEM55-Po5woq_6Asz3qjreJWcE63184-Fe1Qo4Vuhns1_HvwuwJqNxi60GG2aA_Fod0qLmv8RzGlG9LmMANOb2XrcmRrB4C9S_0SwHfABSgB_sfGFRm1_DYNx3NBdyMRj4czwbvyn7n5znoRRkgK8qHUIBqkMQeIae7ENC4gSqJP8LI7iK0YjI0f6_fulVPxyZAnMINoI5_whDNtRtOCYQmcaEQZ2shE9ijE8uS409mNhGUyG2Tl2t9e0636pXWTTuH_ssBdg8Cn1J3KHoMViBz_3zZtck6rOV5EjAlO74gNPjSboxvva6togOWyrxYLJHd2cJqRlt4KmjD1XNRwALDQLglRb5MHA86DbSW4BoDCv7qQuWuoeMcjYNGX7ogZ6LPSFhoEBquN9PAG1MR3D3yiO6XbsXNqm0wO2kWrVlQw744Ab6kUWmiE0NAKjp1q3GXpha0vwhLKT4Fgvz0l56W2UUosoQboEUnV4enWRGBynH8xz7DUZ5R6_6j3A-OfNpPYoaGggMtxBcRE9C348H_yjg3rgM0sE1ec7E8NvUnQui7y5ctejqzCoLTU-7Ro8O5UGlbdSfokXTJWTdDJtSEN2KreKqrUs'
url = "https://www.fflogs.com/api/v2/client"

# Authentification de l'API
class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

def report_to_df():
    try:    
        conn = mysql.connector.connect(user=user, password=password, host=host, port=port)        
        sql = """ SELECT * FROM projectfflogs.report; """        
        df_result = pd.read_sql(sql, con=conn)
        conn.close()        
        return df_result    
    except Exception as e:
        return {"status": "error", "message": str(e)}

    
@app.get("/get_reports")
async def get_reports():
    df = report_to_df()    
    dict = df.to_dict(orient='records')
    return dict


def try_to_df():
    try: 
        conn = mysql.connector.connect(user=user, password=password, host=host, port=port)
        sql = """ SELECT * FROM projectfflogs.try; """
        df_result = pd.read_sql(sql, con=conn)
        conn.close() 
        return df_result
    except Exception as e:
        return {"status": "error", "message": str(e)}
    

@app.get("/get_tries")
async def get_try():
    df = try_to_df()    
    return df.to_dict(orient='records')


def get_timelines():
    try:
        # Créer une instance de MongoClient avec l'adresse de votre base de données
        client = MongoClient(host, port, username=user, password=password, authSource=user)

        # Accéder à la base de données 'timelineffxiv' 
        db = client['timelineffxiv']

        timeline = db.timeline

        hephaistosII = timeline.find_one() # ATTENTION, quand on aura rempli plus la base de données, il faudra faire un find()
        tag = hephaistosII['encounter_tag']
        id_timeline = hephaistosII['id']
        boss_name = hephaistosII['main_boss_name']
        phases = hephaistosII["phases"] #liste de phases

        # Initialisation des variables pour stocker les résultats
        phases_data = []

        # Itération sur chaque phase
        for phase in hephaistosII['phases']:
            phase_num = phase['phase_number']
            phase_mechanics = phase['mechanics']

            # Itération sur chaque mécanique dans la phase
            for mechanic in phase_mechanics:
                mechanic_name = mechanic['mechanic_name']
                attacks = mechanic['attacks']

                # Itération sur chaque attaque dans la mécanique
                for attack in attacks:
                    attack_name = attack['attack_name']
                    start_time = attack['start_time']
                    end_time = attack['end_time']

                    phases_data.append([
                        hephaistosII['id'],
                        hephaistosII['encounter_tag'],
                        hephaistosII['main_boss_name'],
                        phase_num,
                        mechanic_name,
                        attack_name,
                        start_time,
                        end_time
                    ])

        # Création du DataFrame à partir des données
        df_phases = pd.DataFrame(phases_data, columns=['id', 'encounter_tag','main_boss_name', 'phase',  'mechanic_name', 'attack_name', 'start_time', 'end_time'])

        # Convertir les colonnes start_time et end_time en format datetime avec seulement les minutes et les secondes
        df_phases['start_time'] = pd.to_datetime(df_phases['start_time'], format='%H:%M').dt.strftime('%H:%M')
        df_phases['end_time'] = pd.to_datetime(df_phases['end_time'], format='%H:%M').dt.strftime('%H:%M')

        return df_phases

    except Exception as e:
        return {"status": "error", "message": str(e)}
    

@app.get("/get_timelines")
def get_timelines():
    try:
        # Créer une instance de MongoClient avec l'adresse de votre base de données
        client = MongoClient(host_mongo, port_mongo, username=user_mongo, password=password_mongo, authSource=user_mongo)

        # Accéder à la base de données 'timelineffxiv' 
        db = client['timelineffxiv']

        timeline = db.timeline

        hephaistosII = timeline.find_one() # ATTENTION, quand on aura rempli plus la base de données, il faudra faire un find()
        hephaistosII['_id'] = str(hephaistosII['_id'])  # convert ObjectId to string

        return hephaistosII
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

