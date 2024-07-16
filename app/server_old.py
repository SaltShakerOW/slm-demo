from flask import Flask
from flask_socketio import SocketIO, emit
from langchain_community.llms import Ollama
from langchain_core.tools import tool
from langchain.tools.render import render_text_description # to describe tools as a string 
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from operator import itemgetter
from yfinance import Ticker
import requests, os, dotenv

dotenv.load_dotenv('.env')

app = Flask(__name__)
socket = SocketIO(app)

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
weather_base_url = "http://api.openweathermap.org/data/2.5/weather?"
model = Ollama(model="phi3:mini", base_url=os.getenv('OLLAMA_DOCKER_ADDRESS'))

def converse(input: str) -> str:
    "Generate a conversation with the user based on the input"
    print("converse called") #DEBUGGING
    try:
        return model.invoke(input) 
    except:
        return "Something went wrong with conversion"

@tool
def get_current_stock(ticker: str) -> str:
    "Get the stock price of a chosen stock"
    print("get_current_stock called") #DEBUGGING
    data = Ticker(ticker)
    data = data.history(period = "1d")
    price = data["Close"].iloc[-1]
    print(f"{ticker} ${price}")
    return converse(f"Repeat to the user that the current stock price of {ticker} is ${int(price)}")

@tool
def get_weather(location: str) -> str:
    "Gets the weather at a chosen location in Fahrenheit"
    print("get_weather called") #DEBUGGING
    complete_url = weather_base_url + "appid=" + WEATHER_API_KEY + "&q=" + location
    response = requests.get(complete_url)
    x = response.json()
    current_temperature = x["main"]["temp"]
    return converse(f"Repeat to the user that the weather in {location} is currently {int((current_temperature - 273.15)*1.8 + 32)} degrees Fahrenheit")

tools = [get_current_stock, get_weather]
rendered_tools = render_text_description(tools)
system_prompt = f"""You are an assistant that has access to the following set of tools.
Here are the names and descriptions for each tool:

{rendered_tools}

Given the user input, return the name and input of the tool to use.
Return your response as a JSON blob with 'name' and 'arguments' keys.
The value associated with the 'arguments' key should be a dictionary of parameters."""

def tool_chain(model_output):
    print(f"model_output: {model_output}")
    tool_map = {tool.name: tool for tool in tools}
    chosen_tool = tool_map[model_output["name"]]
    return itemgetter("arguments") | chosen_tool

@app.route('/')
def index():
    return '<h1>Server is active</h1>'

@socket.on('message')
def handle_prompt(data):
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("user", "{input}")]
    )
    chain = prompt | model | JsonOutputParser() | tool_chain
    emit(chain.invoke({'input': data}))

if __name__ == '__main__':
    socket.run(app, port=5000, host="0.0.0.0")