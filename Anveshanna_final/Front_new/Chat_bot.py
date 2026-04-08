import re
import requests
import openai
import os
import sqlite3
from flask import Flask, request, jsonify, render_template, session
from datetime import datetime

app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "local-development-secret")


# Azure OpenAI API configuration
openai.api_type = "azure"
openai.api_base = "https://gourav-openai-service.openai.azure.com/"
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")

# Define the path to the database
DATABASE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Databases")
DATABASE_PATH = os.path.join(DATABASE_FOLDER, "internsync.db")

def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_info(user_id):
    """Get basic user information"""
    conn = get_db_connection()
    try:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        return dict(user) if user else {}
    except Exception as e:
        print(f"Error getting user info: {e}")
        return {}
    finally:
        conn.close()

def get_user_enrollments(user_id):
    """Get courses a user has enrolled in"""
    conn = get_db_connection()
    try:
        enrollments = conn.execute('''
            SELECT e.*, c.course_name 
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.user_id = ?
        ''', (user_id,)).fetchall()
        
        return [dict(enrollment) for enrollment in enrollments]
    except Exception as e:
        print(f"Error getting enrollments: {e}")
        return []
    finally:
        conn.close()

def get_user_progress(user_id):
    """Get user's learning progress"""
    conn = get_db_connection()
    try:
        progress = conn.execute('''
            SELECT * FROM user_progress
            WHERE user_id = ?
            ORDER BY completed_at DESC
        ''', (user_id,)).fetchall()
        
        return [dict(p) for p in progress]
    except Exception as e:
        print(f"Error getting user progress: {e}")
        return []
    finally:
        conn.close()

def get_available_resources():
    """Get list of available resources"""
    conn = get_db_connection()
    try:
        resources = conn.execute('''
            SELECT * FROM resources
            ORDER BY id
        ''').fetchall()
        
        return [dict(resource) for resource in resources]
    except Exception as e:
        print(f"Error getting resources: {e}")
        return []
    finally:
        conn.close()

def markdown_to_html(text):
    """Convert Markdown-style text (bold, italic, code) to HTML for chatbot responses."""
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)  # Bold (**text**)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)  # Italic (*text*)
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)  # Inline code (`code`)
    text = text.replace("\n", "<br>")  # New line handling
    return text

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")

    # Check if user is authenticated - this doesn't have a return statement
    if 'user_id' not in session:
        return jsonify({"response": "Please log in to use the chatbot."})

    user_id = session['user_id']
    print(f"User ID from session: {user_id}")  # Debug log
    
    # Get user data from database
    user_info = get_user_info(user_id)
    enrollments = get_user_enrollments(user_id)
    progress = get_user_progress(user_id)
    resources = get_available_resources()
    
    print(f"User info: {user_info}")  # Debug log
    print(f"Enrollments: {enrollments}")  # Debug log
    
    if not user_input:
        return jsonify({"response": "Please enter a message."})

    try:
        # Build system message with user context (simplified for clarity)
        system_message = f"""
You are an AI assistant for InternSync. You HAVE ACCESS to the user's data and should use it.
User: {user_info.get('username', 'User')} (ID: {user_id})
Enrollments: {', '.join([e.get('course_name', 'Unknown') for e in enrollments]) if enrollments else 'None'}
Recent Progress: {len(progress)} items
Available Resources: {len(resources)} items

Answer based on this user data. NEVER say you don't have access to their information.
"""
        
        print(f"System message: {system_message}")  # Debug log
        
        # Using Azure OpenAI API with user context
        response = openai.ChatCompletion.create(
            engine="gpt-4o-mini",  # Azure deployment name
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        bot_reply = response.choices[0].message.content
        
        # Debug logging
        print(f"Bot reply before formatting: {bot_reply}")
        
        # Convert Markdown-style text to HTML
        bot_reply = markdown_to_html(bot_reply)
        
        return jsonify({"response": bot_reply})
        
    except Exception as e:
        print(f"Azure OpenAI API Error: {str(e)}")
        return jsonify({"response": f"API Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
