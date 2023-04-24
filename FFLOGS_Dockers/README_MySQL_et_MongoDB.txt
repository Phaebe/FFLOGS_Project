MY SQL :

(A faire une fois dans le terminal du docker mysql, commande pour accèder au terminal de la base de données (dans le terminal direct))
mysql -u root -p
(entrer le password définit dans le docker-compose 'root' - normalement)
use projectfflogs;
show tables;
(puis insérer toutes les commandes de création qu'on veut)


MONDB :

(Entrer dans la ligne de commande du docker mongo et entrer cette commande pour remplir la base avec le fichier timeline.json)
mongoimport --authenticationDatabase admin --username admin --password root --db timelineffxiv --collection timeline --file /data/db/timeline.json

(si on veut se ballader dans le mongo shell)
(l'idée c'est de s'authentifier en premier, 'admin' est le nom du compte administrateur donné dans le docker-compose et 'root' le password)
mongosh
use admin
db.auth('admin','root')
use timelineffxiv
show collections
db.timeline.findOne()
(et là il nous donne le contenu de la collection : victory !)


ETAPES SUIVANTES : 

Créer un document .sh qui ferait toutes ces commandes automatiquement ... (mais ocmplexe avant mercredi)