from fastapi import FastAPI
import json
import requests
import os

app = FastAPI()


# -----------------------------
# HOME
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "Smart Hunter is alive 😄"
    }


# -----------------------------
# LOAD JOBS
# -----------------------------
def load_jobs():

    if not os.path.exists("jobs.json"):
        return []

    with open("jobs.json", "r") as file:
        return json.load(file)


# -----------------------------
# SAVE JOBS
# -----------------------------
def save_jobs(jobs):

    with open("jobs.json", "w") as file:
        json.dump(jobs, file, indent=4)


# -----------------------------
# GET ALL JOBS
# -----------------------------
@app.get("/jobs")
def get_jobs():

    jobs = load_jobs()

    return jobs


# -----------------------------
# ADD JOB
# -----------------------------
@app.get("/add-job")
def add_job(
    title: str,
    company: str,
    location: str,
    url: str,
    status: str
):

    jobs = load_jobs()

    new_job = {
        "title": title,
        "company": company,
        "location": location,
        "url": url,
        "status": status
    }

    jobs.append(new_job)

    save_jobs(jobs)

    return {
        "message": "New job added 😄",
        "job": new_job
    }


# -----------------------------
# FETCH REAL JOBS
# -----------------------------
@app.get("/fetch-jobs")
def fetch_jobs():

    url = "https://remotive.com/api/remote-jobs?search=recruiter"

    response = requests.get(url, timeout=10)

    data = response.json()

    jobs = []

    keywords = [
        "recruiter",
        "talent",
        "staffing",
        "sourcer",
        "recruitment",
        "us staffing",
        "recruiting",
        "technical recruiter",
        "acquisition"
    ]

    for job in data["jobs"]:

        title = job["title"].lower()

        if any(keyword in title for keyword in keywords):

            jobs.append({
                "title": job["title"],
                "company": job["company_name"],
                "location": job["candidate_required_location"],
                "url": job["url"],
                "status": "New"
            })

    save_jobs(jobs)

    return {
        "total_jobs_found": len(jobs),
        "jobs": jobs
    }