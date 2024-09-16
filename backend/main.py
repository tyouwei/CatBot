from flask import Flask, request, jsonify
from flask_cors import CORS
from bot import CatBot

app = Flask(__name__)
CORS(app)
bot = CatBot()

@app.route('/process', methods=['POST'])
def process_message():
    data = request.json
    input_message = data.get('input')
    
    response_message = bot.generate_response(input_message)
    return jsonify({'response': response_message})

if __name__ == '__main__':
    app.run(port=5000)
