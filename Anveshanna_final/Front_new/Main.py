from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
import sqlite3
import hashlib
import os,subprocess,sys
import re
#import pyautogui
import WebScraper  # Import the WebScraper module to access the global variable
import requests
import openai

# Set up Azure OpenAI API credentials
openai.api_type = "azure"
openai.api_base = "https://gourav-openai-service.openai.azure.com/"  # Replace with your Azure OpenAI endpoint
openai.api_version = "2023-05-15"  # Use the latest API version
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")


YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"


# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "local-development-secret")


# Define the path to the Databases folder and database file
DATABASE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Databases")
DATABASE_PATH = os.path.join(DATABASE_FOLDER, "internsync.db")(__file__)), "Databases")
DATABASE_PATH = os.path.join(DATABASE_FOLDER, "internsync.db")
# Database connection function
def connect_db():tion function
    try:ect_db():
        # Ensure the Databases folder exists
        if not os.path.exists(DATABASE_FOLDER):
            os.makedirs(DATABASE_FOLDER)OLDER):
            os.makedirs(DATABASE_FOLDER)
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Allows fetching rows as dictionaries
        conn.row_factory = sqlite3.Row  # Allows fetching rows as dictionaries
        # Create the users table if it doesn't exist
        cursor = conn.cursor()le if it doesn't exist
        cursor.execute("""or()
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULLNULL,
            )   password TEXT NOT NULL
        """))
        conn.commit()
        conn.commit()
        # Create the ratings table if it doesn't exist
        cursor = conn.cursor()able if it doesn't exist
        cursor.execute("""or()
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,TOINCREMENT,
                video_id TEXT NOT NULL,L,
                rating_type TEXT NOT NULL CHECK (rating_type IN ('like', 'dislike')),
                UNIQUE(user_id, video_id)  -- Ensure each user can rate a video only once
            )   UNIQUE(user_id, video_id)  -- Ensure each user can rate a video only once
        """))
        conn.commit()
        conn.commit()
        # Add progress tracking table
        cursor.execute("""cking table
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,(
                user_id INTEGER NOT NULL,TOINCREMENT,
                course_name TEXT NOT NULL,
                video_id TEXT,XT NOT NULL,
                project_id TEXT,
                completion_type TEXT CHECK (completion_type IN ('video', 'project')),
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,video', 'project')),
                UNIQUE(user_id, course_name, video_id, project_id)
            )   UNIQUE(user_id, course_name, video_id, project_id)
        """))
        conn.commit()
        conn.commit()
        print("✅ Database connected successfully!")
        return conntabase connected successfully!")
    except sqlite3.Error as e:
        print(f"❌ Database connection error: {e}")
        return Noneatabase connection error: {e}")
        return None
# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
    return hashlib.sha256(password.encode()).hexdigest()

# ------------------------- IMP TOPICS -------------------------
# ------------------------- IMP TOPICS -------------------------
def get_top_industry_topics(subject):
    """Fetches the top 5 industry-relevant topics for placements in a given subject using ChatGPT."""
    """Fetches the top 5 industry-relevant topics for placements in a given subject using ChatGPT."""
    prompt = f"""
    List exactly 5 most important topics in {subject} for industry and placements.
    Format: Return only the topic names, one per line, without numbers or bullets.
    Example:Return only the topic names, one per line, without numbers or bullets.
    Topic One
    Topic Two
    Topic Three
    Topic Foure
    Topic Five
    """ic Five
    """
    try:
        response = openai.ChatCompletion.create(
            engine="gpt-4o-mini",  # Changed to correct engine name
            messages=[{"role": "user", "content": prompt}],ine name
            temperature=0.5,": "user", "content": prompt}],
            max_tokens=1005,
        )   max_tokens=100
        )
        # Split response into lines and clean up
        topics_text = response["choices"][0]["message"]["content"]
        topics_array = [topic.strip() for topic in topics_text.split('\n') if topic.strip()]
        topics_array = [topic.strip() for topic in topics_text.split('\n') if topic.strip()]
        # Ensure we have exactly 5 topics
        topics_array = topics_array[:5]cs
        topics_array = topics_array[:5]
        return topics_array
    except Exception as e:y
        print(f"Error: {str(e)}")
        return []rror: {str(e)}")
        return []
#Function to get resources
def search_youtube_videos(query, max_results=3):
    """Search for top YouTube videos related to the given query."""
    url = "https://www.googleapis.com/youtube/v3/search"n query."""
    params = {ps://www.googleapis.com/youtube/v3/search"
        "part": "snippet",
        "q": query + " tutorial",
        "maxResults": max_results,
        "type": "video",x_results,
        "key": YOUTUBE_API_KEY
    }   "key": YOUTUBE_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()t(url, params=params)
    data = response.json()
    videos = []
    for item in data.get("items", []):
        video_title = item["snippet"]["title"]
        video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        videos.append((video_title, video_url))atch?v={item['id']['videoId']}"
        videos.append((video_title, video_url))
    return videos
    return videos
# ------------------------- ROUTES -------------------------
# ------------------------- ROUTES -------------------------
# Home Page
@app.route('/')
def home():'/')
    return render_template('Home.html')
    return render_template('Home.html')
# List Internships Page
@app.route('/list_intern')
def list_intern():intern')
    if "user_id" not in session:
        return redirect(url_for("login"))
        return redirect(url_for("login"))
    conn = connect_db()
    jobs = conn.execute('SELECT role, company, link FROM courses').fetchall()
    conn.close()execute('SELECT role, company, link FROM courses').fetchall()
    print("Fetched jobs:", jobs)  # Debugging
    return render_template('list_intern.html', courses=jobs)
    return render_template('list_intern.html', courses=jobs)
@app.route("/search", methods=["POST"])
def search_internships():hods=["POST"])
    if "user_id" not in session:
        return redirect(url_for("login"))
        return redirect(url_for("login"))
    # Handle form data from POST request
    query = request.form.get("query", "").strip().lower()
    company = request.form.get("company", "").strip()er()
    location = request.form.get("location", "").strip() or "India"
    job_title = request.form.get("job_title", "").strip()r "India"
    job_title = request.form.get("job_title", "").strip()
    # Debugging: Print received data
    print(f"Received data - Query: {query}, Company: {company}, Location: {location}, Job Title: {job_title}")
    print(f"Received data - Query: {query}, Company: {company}, Location: {location}, Job Title: {job_title}")
    # Store job_title in session
    session['job_title'] = job_title
    session['job_title'] = job_title
    # Run the web scraper to get fresh results
    try:n the web scraper to get fresh results
        print(f"Running WebScraper with: company={company}, location={location}, job_title={job_title or query}")
        subprocess.run(["python", "WebScraper.py", company or query, location, job_title or query], check=True)")
    except subprocess.CalledProcessError as e:py", company or query, location, job_title or query], check=True)
        print(f"Error running WebScraper.py: {e}")
        print(f"Error running WebScraper.py: {e}")
    # Redirect to the list_intern page to display results
    return redirect(url_for("list_intern"))isplay results
    return redirect(url_for("list_intern"))
@app.route("/store_query", methods=["POST"])
def store_query():_query", methods=["POST"])
    if "user_id" not in session:
        return jsonify({"success": False, "message": "You must be logged in to perform this action."}), 401
        return jsonify({"success": False, "message": "You must be logged in to perform this action."}), 401
    data = request.json
    query = data.get("query", "").strip()
    if not query:get("query", "").strip()
        return jsonify({"success": False, "message": "Invalid query data."}), 400
        return jsonify({"success": False, "message": "Invalid query data."}), 400
    session["query"] = query  # Store the query in the session
    print("Query stored in session:", query)  # Debuggingssion
    return jsonify({"success": True, "message": "Query stored successfully."})
    return jsonify({"success": True, "message": "Query stored successfully."})
@app.route("/enroll", methods=["POST"])
def enroll():enroll", methods=["POST"])
    if "user_id" not in session:
        return jsonify({"message": "You must be logged in to enroll"}), 401
        return jsonify({"message": "You must be logged in to enroll"}), 401
    user_id = session["user_id"]
    query = session.get("query")  # Retrieve the query from the session
    query = session.get("query")  # Retrieve the query from the session
    if not query:
        return jsonify({"message": "No query found. Please search first."}), 400
        return jsonify({"message": "No query found. Please search first."}), 400
    print("Query retrieved from session for enrollment:", query)  # Debugging
    print("Query retrieved from session for enrollment:", query)  # Debugging
    conn = connect_db()
    cursor = conn.cursor()
    print(query)n.cursor()
    skills = get_top_industry_topics(query)
    for skill in skills:ustry_topics(query)
        print(f"Top YouTube videos for {skill}:")
        videos = search_youtube_videos(skill)}:")
        for title, url in videos:ideos(skill)
            print(f"- {title}: {url}")
            cursor.execute(""" {url}")
                INSERT INTO resources (user_id, course_name,resource_title,resource_url) 
                VALUES (?, ?, ?,?)ces (user_id, course_name,resource_title,resource_url) 
            """, (user_id,query, title,url))
            conn.commit(),query, title,url))
        print("\n")mmit()
        print("\n")
    try:
        # Insert enrollment into the database
        cursor.execute("""t into the database
            INSERT INTO enrollments (user_id, course_name, enrollment_date) 
            VALUES (?, ?, DATE('now'))ser_id, course_name, enrollment_date) 
        """, (user_id, query))('now'))
        conn.commit(), query))
        return jsonify({"message": f"Successfully enrolled in {query}!"})
    except sqlite3.IntegrityError: f"Successfully enrolled in {query}!"})
        return jsonify({"message": "Already enrolled in this internship!"}), 409
    finally:rn jsonify({"message": "Already enrolled in this internship!"}), 409
        conn.close()
        conn.close()
@app.route("/login", methods=["GET", "POST"])
def login():/login", methods=["GET", "POST"])
    if request.method == "POST":
        email = request.form["email"]
        password = hash_password(request.form["password"])  # Hash entered password
        password = hash_password(request.form["password"])  # Hash entered password
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users WHERE email = ? AND password = ?", (email, password))
        table = cursor.fetchone(), username FROM users WHERE email = ? AND password = ?", (email, password))
        conn.close()or.fetchone()
        conn.close()
        if table:
            session["user_id"] = table[0]
            session["username"] = table[1]
            flash("Login successful! Redirecting to dashboard...", "success")
            return redirect(url_for("Login_success"))ashboard...", "success")
        else:eturn redirect(url_for("Login_success"))
            #pyautogui.alert("Invlaid Credentials ", "Alert")
            flash("Invalid email or password!", "danger")rt")
            return redirect(url_for("Login_failure"))er")
            return redirect(url_for("Login_failure"))
    return render_template("Login.html")
    return render_template("Login.html")
# ----------------- REGISTER FUNCTION -----------------
@app.route("/register", methods=["GET", "POST"])-------
def register():gister", methods=["GET", "POST"])
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = hash_password(request.form["password"])
        password = hash_password(request.form["password"])
        conn = connect_db()
        cursor = conn.cursor()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                           (name, email, password))name, email, password) VALUES (?, ?, ?)", 
            conn.commit()  (name, email, password))
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))ou can now log in.", "success")
        except sqlite3.IntegrityError:ogin"))
            flash("User already exists!", "danger")
        finally:h("User already exists!", "danger")
            conn.close()
            conn.close()
    return render_template("register.html")
    return render_template("register.html")
# ----------------- DASHBOARD FUNCTION -----------------
@app.route("/dashboard")BOARD FUNCTION -----------------
def dashboard():hboard")
    if "user_id" not in session:
        flash("Please log in to access your dashboard.", "warning")
        return redirect(url_for("login"))ur dashboard.", "warning")
        return redirect(url_for("login"))
    return f"Welcome, {session['username']}! This is your dashboard."
    return f"Welcome, {session['username']}! This is your dashboard."
# ----------------- LOGOUT FUNCTION -----------------
@app.route("/logout")OGOUT FUNCTION -----------------
def logout():logout")
    session.pop("user_id", None)
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))", "info")
    return redirect(url_for("home"))
# ----------------- HOME LOGGED IN FUNCTION -----------------
@app.route("/home_logged_in")ED IN FUNCTION -----------------
def home_logged_in():ged_in")
    return render_template("Home_logged_in.html")
    return render_template("Home_logged_in.html")


# ----------------- LOGIN FAILURE FUNCTION -----------------
@app.route("/Login_failure")ILURE FUNCTION -----------------
def Login_failure():ailure")
    return render_template("Login_failure.html")
    return render_template("Login_failure.html")
# ----------------- LOGIN SUCCESS FUNCTION -----------------
@app.route("/Login_success")CCESS FUNCTION -----------------
def Login_success():uccess")
    return render_template("Login_success.html")
    return render_template("Login_success.html")
# // ...existing code...
# // ...existing code...
@app.route("/resources")
def resources():ources")
    if "user_id" not in session:
        return redirect(url_for("login"))
        return redirect(url_for("login"))
    return render_template("resources.html")
    return render_template("resources.html")
# Keep only this version of get_enrolled_internships
@app.route("/get_enrolled_internships")d_internships
def get_enrolled_internships():nships")
    if "user_id" not in session:
        return jsonify([])ssion:
        return jsonify([])
    user_id = session["user_id"]
    conn = connect_db()user_id"]
    cursor = conn.cursor()
    cursor = conn.cursor()
    cursor.execute("""
        WITH ecute("""
        video_counts AS (
            SELECT course_name, COUNT(*) as total_videos
            FROM resourcesname, COUNT(*) as total_videos
            WHERE user_id = ?
            GROUP BY course_name
        ),  GROUP BY course_name
        progress AS (
            SELECT  (
                course_name,
                COUNT(CASE WHEN completion_type = 'video' THEN 1 END) as completed_videos,
                COUNT(CASE WHEN completion_type = 'project' THEN 1 END) as completed_projects
            FROM user_progressN completion_type = 'project' THEN 1 END) as completed_projects
            WHERE user_id = ?s
            GROUP BY course_name
        )   GROUP BY course_name
        SELECT 
            e.course_name, 
            e.enrollment_date,
            COALESCE(p.completed_videos, 0) as completed_videos,
            COALESCE(p.completed_projects, 0) as completed_projects,
            COALESCE(vc.total_videos, 0) as total_videosed_projects,
        FROM enrollments etal_videos, 0) as total_videos
        LEFT JOIN progress p ON e.course_name = p.course_name
        LEFT JOIN video_counts vc ON e.course_name = vc.course_name
        WHERE e.user_id = ?nts vc ON e.course_name = vc.course_name
    """, (user_id, user_id, user_id))
    """, (user_id, user_id, user_id))
    internships = cursor.fetchall()
    conn.close()= cursor.fetchall()
    conn.close()
    internships_list = []
    for internship in internships:
        internships_list.append({:
            "course_name": internship[0],
            "date_posted": internship[1],
            "progress": {: internship[1],
                "videos": internship[2],
                "total_videos": internship[4],
                "projects": internship[3],[4],
                "total_projects": 3  # Fixed number of projects per course
            }   "total_projects": 3  # Fixed number of projects per course
        })  }
        })
    return jsonify(internships_list)
    return jsonify(internships_list)

# VIDEOS
# VIDEOS
@app.route("/videos")
def videos():videos")
    if "user_id" not in session:
        return redirect(url_for("login"))
        return redirect(url_for("login"))
    return render_template("videos.html")
    return render_template("videos.html")
@app.route("/get_enrolled_videos")
def get_enrolled_videos():videos")
    if "user_id" not in session:
        return jsonify([])  # Return empty list if user is not logged in
        return jsonify([])  # Return empty list if user is not logged in
    user_id = session["user_id"]
    course_name = request.args.get("course_name", "").strip()  # Retrieve course_name from query parameters
    course_name = request.args.get("course_name", "").strip()  # Retrieve course_name from query parameters
    print(f"Received course_name: {course_name}")  # Debugging: Log the course_name
    print(f"Received course_name: {course_name}")  # Debugging: Log the course_name
    if not course_name:
        print("Error: course_name is missing or empty")  # Debugging: Log the error
        return jsonify({"message": "Course name is required"}), 400g: Log the error
        return jsonify({"message": "Course name is required"}), 400
    conn = connect_db()
    cursor = conn.cursor()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT resources.resource_title, resources.resource_url
        FROM resourceses.resource_title, resources.resource_url
        WHERE resources.user_id = ? AND resources.course_name = ?
    """, (user_id, course_name))= ? AND resources.course_name = ?
    """, (user_id, course_name))
    resources = cursor.fetchall()
    print(f"Fetched resources: {resources}")  # Debugging: Log the fetched resources
    conn.close()hed resources: {resources}")  # Debugging: Log the fetched resources
    conn.close()
    resources_list = []
    for resource in resources:
        resources_list.append({
            "resource_name": resource[0],
            "resource_url": resource[1],,
        })  "resource_url": resource[1],
        })
    return jsonify(resources_list)
    return jsonify(resources_list)
# // ...existing code...
# // ...existing code...
# Route to handle video ratings
@app.route("/rate_video", methods=["POST"])
def rate_video():_video", methods=["POST"])
    if "user_id" not in session:
        return jsonify({"message": "You must be logged in to rate videos"}), 401
        return jsonify({"message": "You must be logged in to rate videos"}), 401
    user_id = session["user_id"]
    data = request.jsonuser_id"]
    video_id = data.get("video_id")
    rating_type = data.get("rating_type")
    rating_type = data.get("rating_type")
    if not video_id or rating_type not in ["like", "dislike"]:
        return jsonify({"message": "Invalid data"}), 400ike"]:
        return jsonify({"message": "Invalid data"}), 400
    conn = connect_db()
    cursor = conn.cursor()
    cursor = conn.cursor()
    try:
        # Insert or update the rating
        cursor.execute(""" the rating
            INSERT INTO ratings (user_id, video_id, rating_type)
            VALUES (?, ?, ?)ngs (user_id, video_id, rating_type)
            ON CONFLICT(user_id, video_id) DO UPDATE SET rating_type = excluded.rating_type
        """, (user_id, video_id, rating_type))UPDATE SET rating_type = excluded.rating_type
        conn.commit(), video_id, rating_type))
        return jsonify({"message": "Rating submitted successfully!"})
    except sqlite3.Error as e:ge": "Rating submitted successfully!"})
        print(f"❌ Database error: {e}")
        return jsonify({"message": "An error occurred"}), 500
    finally:rn jsonify({"message": "An error occurred"}), 500
        conn.close()
        conn.close()
# Route to fetch video ratings
@app.route("/get_video_ratings", methods=["GET"])
def get_video_ratings():atings", methods=["GET"])
    video_id = request.args.get("video_id")
    video_id = request.args.get("video_id")
    if not video_id:
        return jsonify({"message": "Video ID is required"}), 400
        return jsonify({"message": "Video ID is required"}), 400
    conn = connect_db()
    cursor = conn.cursor()
    cursor = conn.cursor()
    try:
        # Fetch the total likes and dislikes for the video
        cursor.execute("""likes and dislikes for the video
            SELECT ute("""
                SUM(CASE WHEN rating_type = 'like' THEN 1 ELSE 0 END) AS likes,
                SUM(CASE WHEN rating_type = 'dislike' THEN 1 ELSE 0 END) AS dislikes
            FROM ratings WHEN rating_type = 'dislike' THEN 1 ELSE 0 END) AS dislikes
            WHERE video_id = ?
        """, (video_id,))d = ?
        result = cursor.fetchone()
        return jsonify({"likes": result["likes"] or 0, "dislikes": result["dislikes"] or 0})
    except sqlite3.Error as e:": result["likes"] or 0, "dislikes": result["dislikes"] or 0})
        print(f"❌ Database error: {e}")
        return jsonify({"message": "An error occurred"}), 500
    finally:rn jsonify({"message": "An error occurred"}), 500
        conn.close()
        conn.close()
#--------------------PROJECTS------------------
#--------------------PROJECTS------------------

def get_projects_for_company(company_name):
    """Generate project ideas for a given company using Azure OpenAI."""
    prompt = f"""Generate 3 project ideas for {company_name} internship in this exact format:
    prompt = f"""Generate 3 project ideas for {company_name} internship in this exact format:
### Project 1: **[Project Name]**
### Project 1: **[Project Name]**
#### Problem Statement:
[Problem description]t:
[Problem description]
#### Tech Stack:
- **Languages**: [languages]
- **Frameworks**: [frameworks]
- **Libraries**: [libraries]s]
- **Database**: [database]s]
- **Frontend**: [frontend]
- **Frontend**: [frontend]
#### Unique Features:
- [Feature 1]eatures:
- [Feature 2]
- [Feature 3]
- [Feature 4]
- [Feature 4]
---
---
[Repeat format for Projects 2 and 3]
"""peat format for Projects 2 and 3]
"""
    response = openai.ChatCompletion.create(
        engine="gpt-4o-mini",pletion.create(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,": "user", "content": prompt}],
        max_tokens=1000  # Increased max_tokens for longer response
    )   max_tokens=1000  # Increased max_tokens for longer response
    )
    return response["choices"][0]["message"]["content"]
    return response["choices"][0]["message"]["content"]
# PROJECTS
# PROJECTS
@app.route("/projects")
def projects():ojects")
    if "user_id" not in session:
        return redirect(url_for("login"))
        return redirect(url_for("login"))
    return render_template("projects.html")
    return render_template("projects.html")
@app.route("/get_projects")
def get_projects():ojects")
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
        return jsonify({"error": "Not logged in"}), 401
    course_name = request.args.get("course_name", "").strip()
    print(f"Received course name in get_projects: {course_name}")  # Debug log
    print(f"Received course name in get_projects: {course_name}")  # Debug log
    if not course_name:
        return jsonify({"error": "Course name required"}), 400
        return jsonify({"error": "Course name required"}), 400
    try:
        print(f"Calling get_projects_for_company with: {course_name}")  # Debug log
        projects = get_projects_for_company(course_name)course_name}")  # Debug log
        print(f"Generated projects response: {projects}")  # Debug log
        return jsonify({"projects": projects})projects}")  # Debug log
    except Exception as e:rojects": projects})
        print(f"Error generating projects: {e}")
        return jsonify({"error": str(e)}), 500")
        return jsonify({"error": str(e)}), 500
#--------------------ChatBOt------------------
#--------------------ChatBOt------------------
def markdown_to_html(text):
    """Convert Markdown-style text (bold, italic, code) to HTML for chatbot responses."""
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)  # Bold (**text**)s."""
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)  # Italic (*text*)d (**text**)
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)  # Inline code (`code`)
    text = text.replace("\n", "<br>")  # New line handling Inline code (`code`)
    return text.replace("\n", "<br>")  # New line handling
    return text

@app.route("/chat", methods=["POST"])
def chat():"/chat", methods=["POST"])
    try:
        data = request.json
        user_input = data.get("message", "")    user_input = data.get("message", "")

        print("Session data:", dict(session))  # Log all session data
                return jsonify({"response": "Please enter a message."})
        if 'user_id' not in session:
            print("No user_id in session")
            return jsonify({"response": "Please log in to use the chatbot."})I_KEY}",
   "Content-Type": "application/json"
        user_id = session['user_id']    }
        print(f"User ID from session: {user_id}")
        
        # Add more detailed debugging
        # Rest of function remains the same   "messages": [{"role": "user", "content": user_input}]
    except Exception as e:    }
        print(f"Unexpected error in chat route: {str(e)}")
        return jsonify({"response": "An error occurred. Please try again."})
OQ_ENDPOINT, json=payload, headers=headers)
# Add new route to mark item as completed        response.raise_for_status()
@app.route("/mark_completed", methods=["POST"])
def mark_completed():        bot_reply = response.json()["choices"][0]["message"]["content"]
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
            bot_reply = markdown_to_html(bot_reply)
    data = request.json
    user_id = session["user_id"]        return jsonify({"response": bot_reply})
    course_name = data.get("course_name")
    item_id = data.get("item_id")ception as e:
    completion_type = data.get("type")  # 'video' or 'project'
            return jsonify({"response": f"API Error: {str(e)}"})
    conn = connect_db()
    cursor = conn.cursor()
    pleted", methods=["POST"])
    try:
        if completion_type == "video":
            cursor.execute("""    return jsonify({"error": "Not logged in"}), 401
                INSERT INTO user_progress (user_id, course_name, video_id, completion_type)
                VALUES (?, ?, ?, 'video')
            """, (user_id, course_name, item_id))
        else:e_name")
            cursor.execute("""
                INSERT INTO user_progress (user_id, course_name, project_id, completion_type)completion_type = data.get("type")  # 'video' or 'project'
                VALUES (?, ?, ?, 'project')
            """, (user_id, course_name, item_id))
        conn.commit()cursor = conn.cursor()
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"message": "Already marked as completed"}), 409"video":
    finally:
        conn.close() (user_id, course_name, video_id, completion_type)

"", (user_id, course_name, item_id))
@app.route("/check_completion")
def check_completion():
    if "user_id" not in session:user_id, course_name, project_id, completion_type)
        return jsonify({"completed": False}), 401
r_id, course_name, item_id))
    user_id = session["user_id"]
    item_id = request.args.get("item_id") True})
    course_name = request.args.get("course_name")
    completion_type = request.args.get("type")rn jsonify({"message": "Already marked as completed"}), 409

    if not all([item_id, course_name, completion_type]):        conn.close()
        return jsonify({"completed": False, "error": "Missing parameters"}), 400

    conn = connect_db()letion")
    cursor = conn.cursor()

    try:        return jsonify({"completed": False}), 401
        if completion_type == "video":
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM user_progress e")
                    WHERE user_id = ?     completion_type = request.args.get("type")
                    AND course_name = ? 
                    AND video_id = ? 
                    AND completion_type = 'video'        return jsonify({"completed": False, "error": "Missing parameters"}), 400
                )
            """, (user_id, course_name, item_id))
        else:    cursor = conn.cursor()
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM user_progress "video":
                    WHERE user_id = ? 
                    AND course_name = ? 
                    AND project_id = ? _progress 
                    AND completion_type = 'project'
                ) ? 
            """, (user_id, course_name, item_id))
   AND completion_type = 'video'
        result = cursor.fetchone()[0] == 1
        return jsonify({"completed": result})"", (user_id, course_name, item_id))
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"completed": False, "error": str(e)}), 500
    finally:_progress 
        conn.close()
 

def get_available_resources():   AND completion_type = 'project'
    """Get list of available resources"""
    conn = connect_db()            """, (user_id, course_name, item_id))
    try:
        resources = conn.execute('''
            SELECT * FROM resourceseted": result})
            ORDER BY id
        ''').fetchall()
        rn jsonify({"completed": False, "error": str(e)}), 500
        return [dict(resource) for resource in resources]
    except Exception as e:        conn.close()
        print(f"Error getting resources: {e}")
        return []
    finally:
        conn.close()lable resources"""
 = connect_db()

if __name__ == '__main__':'
    app.run(debug=True)    app.run(debug=True)