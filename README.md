# SLM-demo

## .env
Be sure to add a new .env file to the app directory that contains these arguments

    WEATHER_API_KEY = ""
    OLLAMA_DOCKER_ADDRESS = ""
    APP_DOCKER_ADDRESS = ""
    ALPHA_VANTAGE_API_KEY = ""

 - Where the WAETHER_API_KEY is the API key generated from openweathermap.org 
 - Where the OLLAMA_DOCKER_ADDRESS & APP_DOCKER_ADDRESS are the local
   ipv4 addresses of the respective containers     
 - Where ALPHA_VANTAGE_API_KEY is the API key generated from https://www.alphavantage.co/

## Building
In order to build the app, be sure to have docker installed on device and navigate to the /app directory. Then, simply run this command

    docker compose up --build
Do bear in mind that it will take a moment to install the phi3:mini SLM during the first execution of the app.
