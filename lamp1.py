from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = "your_api_key_here"

def require_api_key(f):
    def decorated_function(*args, **kwargs):
        if request.headers.get('api-key') == API_KEY:
            return f(*args, **kwargs)
        else:
            return jsonify({'message': 'Invalid API key'}), 403
    decorated_function.__name__ = f.__name__
    return decorated_function

lamp_states = {
    'lamp_1': False,
    'lamp_2': False,
    'lamp_3': False,
    'lamp_4': False,
}

@app.route('/get_lamp_state/<lamp_name>', methods=['GET'])
@require_api_key
def get_lamp_state(lamp_name):
    if lamp_name in lamp_states:
        return jsonify({'state': lamp_states[lamp_name]})
    else:
        return jsonify({'message': 'Lamp not found'}), 404

@app.route('/turn_on_lamp/<lamp_name>', methods=['POST'])
@require_api_key
def turn_on_lamp(lamp_name):
    if lamp_name in lamp_states:
        lamp_states[lamp_name] = True
        return jsonify({'message': f'{lamp_name} turned on'})
    else:
        return jsonify({'message': 'Lamp not found'}), 404

@app.route('/turn_off_lamp/<lamp_name>', methods=['POST'])
@require_api_key
def turn_off_lamp(lamp_name):
    if lamp_name in lamp_states:
        lamp_states[lamp_name] = False
        return jsonify({'message': f'{lamp_name} turned off'})
    else:
        return jsonify({'message': 'Lamp not found'}), 404
    
if __name__ == '__main__':
    app.run(port=7000)

