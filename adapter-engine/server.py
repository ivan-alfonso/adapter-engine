from os import truncate
from flask import Flask, request, abort
from system_adaptation import adapt_system
import json
import _thread

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        _thread.start_new_thread(adapt_system, (request.json,))
        return 'success', 200
    else:
        abort(400)

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")
