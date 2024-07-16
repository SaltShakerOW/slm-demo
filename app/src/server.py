from flask import Flask
from flask_socketio import SocketIO, emit
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, Tool
from langchain.tools import tool
from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferWindowMemory
from yfinance import Ticker
import os, dotenv, requests

dotenv.load_dotenv('.env')

app = Flask(__name__)
socket = SocketIO(app)

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
weather_base_url = "http://api.openweathermap.org/data/2.5/weather?"
llm = Ollama(model="phi3:mini", base_url=os.getenv('OLLAMA_DOCKER_ADDRESS'))

memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=3,
    return_messages=True
)


def get_current_stock(ticker: str) -> list:
    "Returns a list of possible companies and their respective stock prices relative to the parameter string"
    output_array = []
    res = requests.get(f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={ticker}&apikey={ALPHA_VANTAGE_API_KEY}')
    response = res.json()
    print("get_current_stock called") #DEBUGGING
    try:
        data = Ticker(ticker)
        data = data.history(period = "1d")
        price = data["Close"].iloc[-1]
    except:
        for entry in response['bestMatches']:
            new_ticker = entry['1. symbol']
            try:
                data = Ticker(new_ticker)
                data = data.history(period = "1d")
                price = data["Close"].iloc[-1]
            except:
                continue
            else:
                output_array.append({
                    "name": entry['2. name'],
                    "price": price
                })
    else:
        for entry in response['bestMatches']:
            if entry['1. symbol'] == ticker.upper():
                output_array.append({
                    "name": entry['2. name'],
                    "price": price
                })
    return output_array
            
def get_weather(location: str) -> int:
    "Gets the weather at a chosen location in Fahrenheit"
    print("get_weather called") #DEBUGGING
    complete_url = weather_base_url + "appid=" + WEATHER_API_KEY + "&q=" + location
    response = requests.get(complete_url)
    x = response.json()
    current_temperature = x["main"]["temp"]
    return int((current_temperature - 273.15)*1.8 + 32)

tool_list = [
    Tool(
        name="get_current_stock",
        func= get_current_stock,
        description="Returns a list of possible companies and their respective stock prices relative to the desired stock ticker or company name. Input MUST be ONLY either a valid company name OR a valid stock ticker code in the form of a SINGLE WORD.",
    ),
    Tool(
        name="get_weather",
        func= get_weather,
        description="Gets the weather at a chosen location in Fahrenheit. Input must be ONLY a valid city name and nothing else."
    )
]

conversational_agent = initialize_agent(
    agent='chat-conversational-react-description',
    tools=tool_list,
    llm=llm,
    verbose=False,
    max_iterations=3,
    early_stopping_method='generate',
    memory=memory
)

@app.route('/')
def index():
    return '<h1>Server is active</h1>'

@socket.on('message')
def handle_prompt(data):
    response = conversational_agent(data)
    print(response['output'])
    emit(response['output'])

if __name__ == "__main__":
    socket.run(app, port=5000, host="0.0.0.0")


