from flask import Flask, render_template, request, redirect
import sqlite3
import subprocess

app = Flask(__name__)

def get_db_connection():
    with sqlite3.connect('jobs_data.db') as conn:
        conn.row_factory = sqlite3.Row
        return conn

@app.route('/')
def index():
    conn = get_db_connection()
    jobs = conn.execute('SELECT role, company, link FROM jobs').fetchall()
    conn.close()
    return render_template('hph.html', jobs=jobs)

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get("query", "").strip()
    company = request.form.get("company", "").strip()
    location = request.form.get("location", "India").strip()
    job_title = request.form.get("job_title", "").strip()

    try:
        # Run web scraper script
        subprocess.run(["python", "Webscrap.py", company, location, job_title], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Webscrap.py: {e}")

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
