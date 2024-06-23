from flask import Flask, request, jsonify
import queue

app = Flask(__name__)

# API key for authentication
API_KEY = "your_actual_api_key_here"  # مقدار کلید API را اینجا قرار دهید


# Decorator to check for a valid API key in request headers

def require_api_key(f):
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('api-key')
        print(f"Received API key: {api_key}")  # Debugging line to print received API key
        if api_key == API_KEY:
            return f(*args, **kwargs)
        else:
            print("Invalid API key")  # Debugging line to indicate invalid API key
            return jsonify({'message': 'Invalid API key'}), 403
    decorated_function.__name__ = f.__name__
    return decorated_function

# Initialize the queue for requests
request_queue = queue.Queue()
latest_status = {"status": "off"}

@app.route('/requests', methods=['GET', 'POST'])
def requests_handler():
    if request.method == 'GET':
        if request_queue.empty():
            return jsonify({'message': 'No requests in queue'}), 404
        else:
            last_response = request_queue.get()
            return jsonify(last_response)

    elif request.method == 'POST':
        data = request.get_json()
        if data and 'command' in data:  # Assuming the key 'command' is used in POST requests
            request_queue.put(data)
            latest_status["status"] = data['command']
            return jsonify({'message': 'Request added to queue', 'queue_length': request_queue.qsize()})
        else:
            return jsonify({'message': 'Invalid data or command key missing'}), 400

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(latest_status), 200

if __name__ == '__main__':
    app.run(port=7000)
