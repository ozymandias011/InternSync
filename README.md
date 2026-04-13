# 🚀 InternSync – Internship Discovery & Learning Platform  

## 📌 Overview  
InternSync is a web-based internship discovery platform that helps students find internships and learn the required skills efficiently.  

It automates internship search using web scraping and enhances listings by extracting required skills and mapping them to learning resources.  

---

## ✨ Features  

### 🔍 Internship Search  
- Search internships by role (e.g., Frontend Intern) or company name  
- Dynamically fetch internship listings  

### 🤖 Web Scraping (LinkedIn)  
- Built using Selenium  
- Extracts job title, company name, and internship details  

### 🧠 Skill Extraction  
- Processes job descriptions  
- Identifies required skills for each internship  

### 🎥 Learning Resource Integration  
- Uses YouTube Data API  
- Fetches relevant videos for each skill  

### 📊 Internship Data Management  
- Stores internship data in SQLite3  
- Optimized queries for faster search  

### 🔐 Authentication  
- User Sign Up / Login system  
- JWT-based authentication  

---

## 🛠️ Tech Stack  

- **Frontend:** HTML, CSS  
- **Backend:** Flask (Python)  
- **Database:** SQLite3  
- **Web Scraping:** Selenium  
- **API:** YouTube Data API  
- **Authentication:** JWT  

---

## 🏗️ Project Structure  

```
Anveshanna_final/
├── BACKEND/
│   ├── static/              
│   ├── templates/           
│   ├── Webscrap.py          
│   ├── app.py               
│   └── jobs_data.db         
│
├── Databases/               
│
├── Front_new/
│   ├── static/
│   ├── templates/
│   ├── Chat_bot.py
│   ├── Main.py
│   ├── WebScraper.py
│   ├── cleardb.py
│   ├── projects.py
│   ├── resources.py
│   └── tempCodeRunnerFile.py
```


---


## ⚙️ Setup & Installation  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/ozymandias011/InternSync.git
cd InternSync
### 2️⃣ Create Virtual Environment  
```bash
python -m venv venv
```

---

### 3️⃣ Activate Virtual Environment  

#### ▶️ Windows:
```bash
venv\Scripts\activate
```

#### 4️⃣ Mac/Linux:
```bash
source venv/bin/activate
```
### 5️⃣ Run the Application  
```bash
python app.py
```

---

### 6️⃣ Open in Browser  
```
http://127.0.0.1:5000
```

## 📌 How It Works  

1. User searches for an internship  
2. Selenium scraper fetches listings  
3. System extracts skills from job descriptions  
4. YouTube API fetches learning videos  
5. Results display internship details, skills, and resources  

---

## 🎯 Use Case  
- Students looking for internships  
- Beginners who want guided skill learning  
- One platform for internships + preparation  

---

## 🚀 Future Improvements  
- Progress tracking dashboard  
- Resume-based recommendations  
- Advanced filtering system  
- Admin panel  

