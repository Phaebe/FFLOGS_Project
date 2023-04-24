docker build -t projectfflogs_api .
docker login
docker tag projectfflogs_api phaebe/projectfflogs_api:1.0.0
docker push phaebe/projectfflogs_api:1.0.0