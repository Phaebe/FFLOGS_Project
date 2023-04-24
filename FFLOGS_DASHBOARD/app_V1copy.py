import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import mysql.connector
from mysql.connector import Error
from pprint import pprint
import datetime as dt
import requests
import warnings
warnings.filterwarnings("ignore")

user = 'root'
password = 'root'
host = 'localhost'
port = 3305

def jobtype_to_df():
    try:
        conn = mysql.connector.connect(user=user, password=password, host=host, port=port)
        sql = """ SELECT * FROM projectfflogs.jobtype; """
        df_result = pd.read_sql(sql, con=conn)
        conn.close() 
        return df_result        
    except Exception as e:
        return {"status": "error", "message": str(e)}   
    
def job_to_df():
    try:
        conn = mysql.connector.connect(user=user, password=password, host=host, port=port)
        sql = """ SELECT * FROM projectfflogs.job; """
        df_result = pd.read_sql(sql, con=conn)
        conn.close() 
        return df_result
    except Exception as e:
        return {"status": "error", "message": str(e)}

def difficulty_to_df():
    try:
        conn = mysql.connector.connect(user=user, password=password, host=host, port=port)
        sql = """ SELECT * FROM projectfflogs.difficulty; """
        df_result = pd.read_sql(sql, con=conn)
        conn.close() 
        return df_result
    except Exception as e:
        return {"status": "error", "message": str(e)}

def encounter_to_df():
    try:
        conn = mysql.connector.connect(user=user, password=password, host=host, port=port)
        sql = """ SELECT * FROM projectfflogs.encounter; """
        df_result = pd.read_sql(sql, con=conn)
        conn.close() 
        return df_result
    except Exception as e:
        return {"status": "error", "message": str(e)}   
    
def character_to_df():
    try:
        conn = mysql.connector.connect(user=user, password=password, host=host, port=port)
        sql = """ SELECT * FROM projectfflogs.character; """
        df_result = pd.read_sql(sql, con=conn)
        conn.close() 
        return df_result
    except Exception as e:
        return {"status": "error", "message": str(e)} 
    
def user_to_df():
    try:
        conn = mysql.connector.connect(user=user, password=password, host=host, port=port)
        sql = """ SELECT * FROM projectfflogs.user; """
        df_result = pd.read_sql(sql, con=conn)
        conn.close() 
        return df_result
    except Exception as e:
        return {"status": "error", "message": str(e)} 
    
def static_to_df():
    try: 
        conn = mysql.connector.connect(user=user, password=password, host=host, port=port)
        sql = """ SELECT * FROM projectfflogs.static; """
        df_result = pd.read_sql(sql, con=conn)
        conn.close() 
        return df_result
    except Exception as e:
        return {"status": "error", "message": str(e)} 

def try_to_df():
    try: 
        conn = mysql.connector.connect(user=user, password=password, host=host, port=port)
        sql = """ SELECT * FROM projectfflogs.try; """
        df_result = pd.read_sql(sql, con=conn)
        conn.close() 
        return df_result
    except Exception as e:
        return {"status": "error", "message": str(e)}

def report_to_df():
    try:
        conn = mysql.connector.connect(user=user, password=password, host=host, port=port)
        sql = """ SELECT * FROM projectfflogs.report; """
        df_result = pd.read_sql(sql, con=conn)
        conn.close() 
        return df_result
    except Exception as e:
        return {"status": "error", "message": str(e)}

def teampertry_to_df():
    try:
        conn = mysql.connector.connect(user=user, password=password, host=host, port=port)
        sql = """ SELECT * FROM projectfflogs.teampertry; """
        df_result = pd.read_sql(sql, con=conn)
        conn.close() 
        return df_result
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Charger les deux dataframes
#df1 = pd.read_csv('data/fights.csv')
df1 = try_to_df()
df2 = pd.read_csv('data/timeline_id87.csv')

# Fusion des deux csv
merged_df = pd.merge(df1, df2, left_on="fk_id_encounter", right_on="id")
#print(merged_df.head())
# Calculer la durée de combat pour chaque ligne
merged_df["duration"] = merged_df["end_time_x"] - merged_df["start_time_x"]

# Convertir les valeurs de durée de combat en secondes
merged_df["duration"] = merged_df["duration"] / 1000
merged_df["temps-attaque"] = merged_df["end_time_y"].apply(lambda x: int(x.split(':')[0])*60 + int(x.split(':')[1]))

# Convertir la colonne "duration" en un objet timedelta
merged_df["duration_time"] = pd.to_timedelta(merged_df["duration"], unit="s")

# Créer une nouvelle colonne contenant la durée sous forme de minutes et secondes
merged_df["duration_min_sec"] = merged_df["duration_time"].apply(lambda x: f"{x.seconds//60:02d}:{x.seconds%60:02d}") 

# Eliminer les colonnes inutiles
df_clean = merged_df.drop(columns=['encounter_tag','main_boss_name','duration_time'])

# Sélectionner les lignes qui satisfont la condition
df_stat = df_clean.loc[df_clean["duration"] >= df_clean["temps-attaque"]]
#print(df_stat.head())
#print(df_clean.head())

# Garder uniquement les valeurs ou l'équipe est morte
df_stat = df_stat.drop_duplicates(subset=['id_try', 'end_time_x'], keep='last')

# ajouter une nouvelle colonne représentant le temps depuis le début du combat
#df_stat["temps_depuis_le_debut"] = df_stat["start_time_x"] - df_stat["reportStartTime"]

# convertir la colonne en secondes
#df_stat["temps_depuis_le_debut"] = df_stat["temps_depuis_le_debut"] / 1000

#df_stat = df_stat.sort_values(by=["temps_depuis_le_debut"])

#df_stat["id_try"] = range(1, len(df_stat)+1)

# Trier le dataframe selon la colonne duration_min_sec
df_sorted = df_stat.sort_values(by='duration_min_sec')

index_list = df_stat.index
df_stat = df_stat.loc[index_list] # sélection des lignes correspondantes aux index
df_stat = df_stat.reset_index(drop=True) # création d'une nouvelle colonne d'index numérotée
#Créer un dictionnaire contenant le nombre d'occurrences de chaque couple mechanic_name-attack_name
couple_mechanic_attack = {}
for i in range(len(df_stat)):
    couple = df_stat.loc[i, 'mechanic_name'] + '-' + df_stat.loc[i, 'attack_name']
    if couple in couple_mechanic_attack:
        couple_mechanic_attack[couple] += 1
    else:
        couple_mechanic_attack[couple] = 1

#Créer une liste contenant les pourcentages du boss pour chaque combat
pourcentage_boss = list(df_stat['boss_percentage'])

#Créer le graphique camembert
fig1 = go.Figure(data=[go.Pie(labels=list(couple_mechanic_attack.keys()), values=list(couple_mechanic_attack.values()), hole=0.5)])
fig1.update_layout(title='Relation entre le couple mechanic-attack et le pourcentage du boss')

# Créer le deuxième graphique scatterplot
fig2 = px.scatter(df_sorted, x="id_try", y="duration_min_sec", title='We died at that moment!',
                  template='plotly_white', labels={"id_try": "Fights Index", "duration_min_sec": "Duration(min:sec)"})
fig2.update_layout(xaxis=dict(showgrid=True, zeroline=True, tickmode='linear'), yaxis=dict(showgrid=True, zeroline=True, tickformat='%M:%S'))






# Afficher les graphiques côte à côte dans un dashboard
external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Final Fantasy XIV"


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="⚔️🐉🧙‍♀️", className="header-emoji"),
                html.H1(
                    children="Final Fantasy XIV: Raids Tool", className="header-title"
                ),
                html.P(
                    children=(
                        "Analyze the mechanics and attacks where you died,"
                        " next try you will not die at the same point!"
                    ),
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(figure=fig1)  
                ),  
                html.Div([
                    dcc.Graph(figure=fig2)
                ], className="six columns"),
            ], 
            className="row"
        )
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)
