import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from dateutil.relativedelta import relativedelta
from fastapi import FastAPI

app = FastAPI()

def compute_stats():
    # Charger les deux dataframes
    df1 = pd.read_csv('fights.csv')
    df2 = pd.read_csv('timeline_id87.csv')

    # Fusion des deux csv
    merged_df = pd.merge(df1, df2, left_on="encounterID", right_on="id")

    # Calculer la durée de combat pour chaque ligne
    merged_df["duration"] = merged_df["endTime"] - merged_df["startTime"]

    # Convertir les valeurs de durée de combat en secondes
    merged_df["duration"] = merged_df["duration"] / 1000
    merged_df["temps-attaque"] = merged_df["end_time"].apply(lambda x: int(x.split(':')[0])*60 + int(x.split(':')[1]))

    # Convertir la colonne "duration" en un objet timedelta
    merged_df["duration_time"] = pd.to_timedelta(merged_df["duration"], unit="s")

    # Créer une nouvelle colonne contenant la durée sous forme de minutes et secondes
    merged_df["duration_min_sec"] = merged_df["duration_time"].apply(lambda x: f"{x.seconds//60:02d}:{x.seconds%60:02d}") 

    # Eliminer les colonnes inutiles
    df_clean = merged_df.drop(columns=['friendlyPlayers', 'size', 'encounter_tag','main_boss_name','start_time','duration_time', 'id_y',])

    # Sélectionner les lignes qui satisfont la condition
    df_stat = df_clean.loc[df_clean["duration"] >= df_clean["temps-attaque"]]

    # Garder uniquement les valeurs ou l'équipe est morte
    df_stat = df_stat.drop_duplicates(subset=['id_x', 'endTime'], keep='last')

    # ajouter une nouvelle colonne représentant le temps depuis le début du combat
    df_stat["temps_depuis_le_debut"] = df_stat["startTime"] - df_stat["reportStartTime"]

    # convertir la colonne en secondes
    df_stat["temps_depuis_le_debut"] = df_stat["temps_depuis_le_debut"] / 1000

    df_stat = df_stat.sort_values(by=["temps_depuis_le_debut"])

    df_stat["index_combat"] = range(1, len(df_stat)+1)
    
    return df_stat


@app.get("/scatterplot")
async def scatterplot():
    
    df_stat = compute_stats()
    
    # Trier le dataframe selon la colonne duration_min_sec
    df_sorted = df_stat.sort_values(by='duration_min_sec')

    # Création de la figure
    fig = go.Figure()

    # Ajout du nuage de points
    fig.add_trace(go.Scatter(
        x=df_sorted.index_combat,
        y=df_sorted["duration_min_sec"],
        mode='markers',
        marker=dict(size=8, color='blue')
    ))

    # Personnalisation de la figure
    fig.update_layout(
        title='Quand nous sommes mort',
        xaxis_title='Index du combat',
        yaxis_title='Durée (min:sec)',
        xaxis=dict(showgrid=True, zeroline=True, tickmode='linear'),
        yaxis=dict(showgrid=True, zeroline=True, tickformat='%M:%S'),
        template='plotly_white'
)

    # Affichage de la figure
    fig.show()

@app.get("/piechart")
async def piechart():
    df_stat = compute_stats()
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
    pourcentage_boss = list(df_stat['bossPercentage'])

    #Créer le graphique camembert
    fig, ax = plt.subplots()
    ax.pie(couple_mechanic_attack.values(), labels=couple_mechanic_attack.keys(), autopct='%1.1f%%')
    ax.set_title('Relation entre le couple mechanic-attack et le pourcentage du boss')
    plt.show()