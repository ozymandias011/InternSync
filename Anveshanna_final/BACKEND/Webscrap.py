import sqlite3
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def create_database():
    conn = sqlite3.connect("jobs_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            company TEXT,
            link TEXT UNIQUE,
            date_posted TEXT
        )
    """)
    conn.commit()
    conn.close()

def clear_database():
    """Flush old job listings before storing new ones."""
    conn = sqlite3.connect("jobs_data.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs")  # Clear old data
    conn.commit()
    conn.close()

def store_job(role, company, link, date_posted):
    conn = sqlite3.connect("jobs_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO jobs (role, company, link, date_posted) 
        VALUES (?, ?, ?, ?)
    """, (role, company, link, date_posted))
    conn.commit()
    conn.close()

def scrape_jobs(company="", location="India", job_title=""):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Clear old data before scraping
    clear_database()

    # Only use these three keywords: Intern, Internship, Internships
    keywords = "intern OR internship OR internships"
    if job_title:
        keywords = f"{job_title} ({keywords})"
    if company:
        keywords = f"{company} ({keywords})"
    
    # Construct LinkedIn Search URL
    search_url = f"https://www.linkedin.com/jobs/search?keywords={keywords}&location={location}"
    print(f"\U0001F30D Fetching: {search_url}")
    
    driver.get(search_url)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".job-search-card")))

        jobs = driver.find_elements(By.CSS_SELECTOR, ".job-search-card")
        for job in jobs[:10]:  
            role = job.find_element(By.CSS_SELECTOR, ".base-search-card__title").text.strip()
            company_name = job.find_element(By.CSS_SELECTOR, ".base-search-card__subtitle").text.strip()
            link = job.find_element(By.TAG_NAME, "a").get_attribute("href")

            # Handle Date Posted (Optional)
            date_posted = "Unknown"
            try:
                date_elem = job.find_element(By.CSS_SELECTOR, ".job-search-card__listdate")
                date_posted = date_elem.text.strip()
            except:
                pass  

            # Ensure we only store internship jobs
            if any(word in role.lower() for word in ["intern", "internship", "internships"]):
                store_job(role, company_name, link, date_posted)

    finally:
        driver.quit()

if __name__ == "__main__":
    create_database()
    
    # Safe argument handling (avoids index errors)
    company = sys.argv[1] if len(sys.argv) > 1 else ""
    location = sys.argv[2] if len(sys.argv) > 2 else "India"
    job_title = sys.argv[3] if len(sys.argv) > 3 else ""

    scrape_jobs(company, location, job_title)
