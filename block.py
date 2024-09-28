from mitmproxy import http
from flask import Flask, request as flask_request, render_template_string, jsonify
import threading
import os

app = Flask(__name__)

keywords = [b'gaming', b'Gaming', b'GAMING']

def request(flow: http.HTTPFlow) -> None:
    if flow.request.method in ["PUT", "POST"] and flow.request.host == "lms.snuchennai.edu.in":
        if flow.request.multipart_form:
            for part in flow.request.multipart_form.parts:
                if part.filename and part.filename.endswith('.c'):
                    flow.kill()

def response(flow: http.HTTPFlow) -> None:
    if flow.response:
        if flow.response.content:
            if any(keyword in flow.response.content for keyword in keywords):
                flow.kill()

        if flow.request.path.endswith('.exe'):
            flow.kill()

        if flow.request.path.endswith('.c') and flow.request.host == "lms.snuchennai.edu.in":
            flow.kill()

        content_type = flow.response.headers.get("Content-Type", "") and flow.request.host == "lms.snuchennai.edu.in"
        if "text/x-c" in content_type:
            flow.kill()


@app.route('/')
def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">

    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Firewall Chat AI</title>
    <style>
        body {
        font-family: Arial, sans-serif;
        background-color: #f4f4f4;
        margin: 0;
        padding: 0;
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        }

        .container {
        width: 100%;
        max-width: 300px;
        padding: 20px;
        background-color: white;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        text-align: center;
        }

        input[type=text] {
        width: 91.9%;
        padding: 10px;
        margin: 10px 0;
        border: 1px solid #ccc;
        border-radius: 4px;
        }

        .button {
        padding: 10px 20px;
        background-color: #4CAF50;
        border-radius: 4px;
        color: white;
        border: none;
        cursor: pointer;
        width: 100%;
        }

        .button:hover {
        background-color: #45a049;
        }

        h2 {
        margin-bottom: 20px;
        }
    </style>
    </head>

    <body>
    <div class="container">
        <div>
        <h2>Firewall Chat AI</h2>
        <form id="keywordForm">
            <input type="text" id="message" name="message" placeholder="Block chess content"> <!-- Removed label -->
            <input class="button" type="submit">
        </form>
        <p id="responseMessage"></p>
        </div>
    </div>

    <script>
        const form = document.getElementById('keywordForm');
        form.addEventListener('submit', async function (event) {
        event.preventDefault();
        const message = document.getElementById('message').value;

        const response = await fetch('/add_keyword', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `message=${message}`
        });

        const result = await response.json();
        const responseMessage = document.getElementById('responseMessage');
        if (result.status === 'success') {
            responseMessage.textContent = `Keyword added: ${result.added_keyword}`;
        } else {
            responseMessage.textContent = result.message;
        }
        });
    </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/add_keyword', methods=['POST'])
def add_keyword():
    message = flask_request.form['message']
    print(f"Received message: {message}")
    words = message.split()
    if len(words) > 1:
        new_keyword = words[1].encode('utf-8')  # Convert second word to bytes
        keywords.append(new_keyword)  # Add the new keyword to the list
        print(f"Added keyword: {new_keyword}")  # Debug output
        return jsonify({"status": "success", "added_keyword": new_keyword.decode()})
    else:
        return jsonify({"status": "error", "message": "Please provide at least two words."})

def run_flask():
    app.run(port=9999, debug=True, use_reloader=False, threaded=True)

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()
