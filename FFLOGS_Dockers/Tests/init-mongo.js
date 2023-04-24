// Création de la base de données timelineffxiv
db = db.getSiblingDB('timelineffxiv');

// Création de la collection timeline
db.createCollection('timeline');

// Chargement des données depuis le fichier JSON
load("/docker-entrypoint-initdb.d/timeline.json");

print('La base de données timelineffxiv et la collection timeline ont été créées et initialisées avec succès.');
