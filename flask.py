from flask import Flask, request, jsonify


app = Flask(__name__)


# API key for authentication
API_KEY = "your_api_key_here"


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


request_queue = []


@app.route('/requests', methods=['GET', 'POST'])
@require_api_key
def requests_handler():
    if request.method == 'GET':
        if len(request_queue) == 0:
            return jsonify({'message': 'No requests in queue'}), 404
        else:
            last_response = request_queue.pop(0)
            return jsonify(last_response)


    elif request.method == 'POST':
        data = request.get_json()
        if data and 'state' in data:
            request_queue.append(data)
            return jsonify({'message': 'Request added to queue', 'queue_length': len(request_queue)})
        else:
            return jsonify({'message': 'Invalid data or state key missing'}), 400


if __name__ == '__main__':
    app.run(port=7000)
