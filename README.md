# VideoStore_1

## command to build docker  
sudo docker build --build-arg AWS_ACCESS_KEY_ID=$(grep AWS_ACCESS_KEY_ID .env | cut -d '=' -f2)              --build-arg AWS_SECRET_ACCESS_KEY=$(grep AWS_SECRET_ACCESS_KEY .env | cut -d '=' -f2)              -t flask-app .  

## command to run the docker  
sudo docker run -d -v ~/.aws:/root/.aws:ro -p 5000:5000 flask-app
