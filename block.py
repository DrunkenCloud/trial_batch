from mitmproxy import http
from flask import Flask, request as flask_request, render_template_string, jsonify
import threading
import os

app = Flask(__name__)

keywords = [b'gaming', b'Gaming', b'GAMING']
granular_settings = {}

def request(flow: http.HTTPFlow) -> None:
    if flow.request.method in ["PUT", "POST"]:
        # Check for keywords in granular_settings and specific target website
        for keyword, target_website in granular_settings.items():
            if keyword in [b'upload']:
                # Block all uploads for that website
                if flow.request.host == target_website:
                    flow.kill()
                    return
            elif keyword in flow.request.content and target_website.encode('utf-8') in flow.request.host.encode('utf-8'):
                flow.kill()
                return

        # Original check for specific host and filename
        if flow.request.host == "lms.snuchennai.edu.in" and flow.request.multipart_form:
            for part in flow.request.multipart_form.parts:
                if part.filename and part.filename.endswith('.c'):
                    flow.kill()

def response(flow: http.HTTPFlow) -> None:
    if flow.response and flow.response.content:
        # Check for keywords in granular_settings and specific target website
        for keyword, target_website in granular_settings.items():
            if b'download' in keyword:
                # Block all downloads for that website
                if flow.request.host == target_website:
                    flow.kill()
                    return
            elif keyword in flow.response.content and target_website.encode('utf-8') in flow.request.host.encode('utf-8'):
                flow.kill()
                return

        # Original checks for response content, path, and content type
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
        <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='favicon.ico') }}">
        <style>
            :root {
                --bg-color: #343541;
                --text-color: #ECECF1;
                --input-bg: #40414F;
                --user-msg-bg: #5B5C6B;
                --ai-msg-bg: #444654;
                --accent-color: #10A37F;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                height: 100vh;
                display: flex;
                flex-direction: column;
                background-color: var(--bg-color);
                color: var(--text-color);
            }

            .chat-container {
                display: flex;
                flex-direction: column;
                height: 100vh;
                max-width: 800px;
                margin: 0 auto;
                border: 1px solid var(--input-bg);
            }

            .chat-header {
                background-color: var(--input-bg);
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid var(--user-msg-bg);
            }

            .chat-header h1 {
                margin: 0;
                font-size: 1.5em;
                color: var(--accent-color);
            }

            .avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background-color: var(--accent-color);
                display: flex;
                justify-content: center;
                align-items: center;
                color: var(--text-color);
                font-weight: bold;
            }

            .chat-messages {
                flex-grow: 1;
                overflow-y: auto;
                padding: 20px;
                display: flex;
                flex-direction: column;
            }

            .message {
                max-width: 80%;
                padding: 12px 16px;
                margin-bottom: 15px;
                border-radius: 15px;
                word-wrap: break-word;
                line-height: 1.4;
            }

            .user-message {
                align-self: flex-end;
                background-color: var(--user-msg-bg);
                color: var(--text-color);
            }

            .ai-message {
                align-self: flex-start;
                background-color: var(--ai-msg-bg);
                color: var(--text-color);
            }

            .chat-input {
                display: flex;
                padding: 15px;
                background-color: var(--input-bg);
            }

            .chat-input input {
                flex-grow: 1;
                padding: 12px;
                border: 1px solid var(--user-msg-bg);
                border-radius: 8px;
                margin-right: 10px;
                background-color: var(--bg-color);
                color: var(--text-color);
                font-size: 16px;
            }

            .chat-input button {
                padding: 12px 20px;
                background-color: var(--accent-color);
                color: var(--text-color);
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                transition: background-color 0.3s ease;
            }

            .chat-input button:hover {
                background-color: #0D8C6D;
            }

            /* Scrollbar Styles */
            ::-webkit-scrollbar {
                width: 10px;
            }

            ::-webkit-scrollbar-track {
                background: var(--bg-color);
            }

            ::-webkit-scrollbar-thumb {
                background: var(--user-msg-bg);
                border-radius: 5px;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: var(--accent-color);
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <h1>Firewall Chat AI</h1>
                <div class="avatar">AI</div>
            </div>
            <div class="chat-messages" id="chatMessages"></div>
            <form class="chat-input" id="chatForm">
                <input type="text" id="userInput" placeholder="Block chess content" required>
                <button type="submit">Send</button>
            </form>
        </div>

        <script>
            const chatMessages = document.getElementById('chatMessages');
            const chatForm = document.getElementById('chatForm');
            const userInput = document.getElementById('userInput');

            chatForm.addEventListener('submit', async function(event) {
                event.preventDefault();
                const message = userInput.value.trim();
                if (!message) return;

                // Add user message to chat
                addMessage(message, 'user');
                userInput.value = '';

                try {
                    const response = await fetch('/add_keyword', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded'
                        },
                        body: `message=${encodeURIComponent(message)}`
                    });

                    const result = await response.json();

                    console.log(result);
                    let aiMessage;
                    if (result.status === 'success1') {
                        aiMessage = `Now blocking ${result.added_keyword} Content`;
                    } else if (result.status === 'success2') {
                        aiMessage = `Now blocking ${result.added_keyword} for ${result.target_website}`;
                    } else {
                        aiMessage = result.message;
                    }

                    console.log(aiMessage);

                    // Add AI response to chat
                    addMessage(aiMessage, 'ai');
                } catch (error) {
                    console.error('Error:', error);
                    addMessage('An error occurred. Please try again.', 'ai');
                }
            });

            function addMessage(content, sender) {
                const messageElement = document.createElement('div');
                messageElement.classList.add('message', `${sender}-message`);
                messageElement.textContent = content;
                chatMessages.appendChild(messageElement);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
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
    
    if len(words) == 3:
        new_keyword = words[1].encode('utf-8')  # Convert second word to bytes
        keywords.append(new_keyword)  # Add the new keyword to the list
        print(f"Added keyword: {new_keyword}")  # Debug output
        return jsonify({"status": "success1", "added_keyword": new_keyword.decode()})
    
    elif len(words) == 4:
        new_keyword = words[1].encode('utf-8')
        target_website = words[3]
        granular_settings[new_keyword] = target_website  # Add to granular settings dictionary
        print(f"Added keyword: {new_keyword} for website: {target_website}")  # Debug output
        return jsonify({"status": "success2", "added_keyword": new_keyword.decode(), "target_website": target_website})
    
    else:
        return jsonify({"status": "error", "message": "Invalid input. Please provide either three words or four words."})

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

def run_flask():
    app.run(port=9999, debug=True, use_reloader=False, threaded=True)
    app = Flask(_name_, static_folder="dist", template_folder="dist")

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()