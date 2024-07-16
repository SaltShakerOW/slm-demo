import socketio
from socketio.exceptions import TimeoutError
sio = socketio.SimpleClient()
import os, dotenv

dotenv.load_dotenv('.env')

try:
    sio.connect(os.getenv('APP_DOCKER_ADDRESS'))
    print('my sid is', sio.sid)
except Exception as e:
    print(f"Connection Failed: {e}")
else:
    while True:
        query = input("Query: ")
        if query == "exit":
            break
        else:
            sio.emit('message', query)

        try:
            event = sio.receive(timeout=60)
        except TimeoutError:
            print('Timed out waiting for event. Please try again.')
        else:
            print(event[0])



        
