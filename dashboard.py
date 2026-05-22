import streamlit as st
import json
import pandas as pd
import re

st.set_page_config(
    page_title="Smart Hunter",
    layout="wide"
)

# LOAD JOBS
with open("jobs.json", "r") as file:
    jobs = json.load(file)

st.title("🎯 Smart Hunter Dashboard")
# SIDEBAR
st.sidebar.title("📊 Smart Hunter Analytics")

total_jobs = len(jobs)

applied_jobs = len([
    job for job in jobs
    if job["status"] == "Applied"
])

interview_jobs = len([
    job for job in jobs
    if job["status"] == "Interview"
])

new_jobs = len([
    job for job in jobs
    if job["status"] == "New"
])

st.sidebar.metric("Total Jobs", total_jobs)
st.sidebar.metric("New Jobs", new_jobs)
st.sidebar.metric("Applied Jobs", applied_jobs)
st.sidebar.metric("Interview Jobs", interview_jobs)

# SEARCH
search = st.text_input("🔍 Search Jobs")

# STATUS FILTER
status_filter = st.selectbox(
    "🎯 Filter By Status",
    ["All", "New", "Applied", "Interview"]
)

# TOTAL JOBS
st.subheader(f"Total Jobs Found: {len(jobs)}")
# AI MATCH SECTION
st.markdown("## 🤖 AI Resume Match")

resume_text = st.text_area(
    "Paste Resume Text"
)

resume_words = re.findall(
    r"\w+",
    resume_text.lower()
)

# ADD JOB SECTION
with st.expander("➕ Add New Job"):

    with st.form("add_job_form", clear_on_submit=True):

        title = st.text_input("Job Title")
        company = st.text_input("Company")
        location = st.text_input("Location")
        url = st.text_input("Job URL")

        status = st.selectbox(
            "Status",
            ["New", "Applied", "Interview"]
        )

        submitted = st.form_submit_button("Save Job")

        if submitted:

            new_job = {
                "title": title,
                "company": company,
                "location": location,
                "url": url,
                "status": status
            }

            jobs.append(new_job)

            with open("jobs.json", "w") as file:
                json.dump(jobs, file, indent=4)

            st.success("Job Added Successfully 😄")

            st.rerun()


# JOB CARDS
for job in jobs:

    matches_search = (
        search.lower() in job["title"].lower()
        or search.lower() in job["company"].lower()
        or search.lower() in job["location"].lower()
    )

    matches_status = (
        status_filter == "All"
        or job["status"] == status_filter
    )

    if matches_search and matches_status:
        job_text = (
            job["title"] + " " +
            job["company"] + " " +
            job.get("notes", "")
        ).lower()

        job_words = re.findall(
            r"\w+",
            job_text
        )

        matching_words = set(resume_words).intersection(job_words)

        if len(job_words) > 0:
            match_score = int(
                (len(matching_words) / len(job_words)) * 100
            )
        else:
            match_score = 0

        with st.container():

            st.markdown("----")

            col1, col2 = st.columns([4, 1])

            with col1:

                st.subheader(job["title"])

                st.write(f"🏢 Company: {job['company']}")
                st.write(f"📍 Location: {job['location']}")
                st.write(f"📌 Status: {job['status']}")
                st.write(f"🤖 Match Score: {match_score}%")

                st.markdown(
                    f"[🔗 Open Job Link]({job['url']})"
                )
                notes = st.text_area(
                    "📝 Notes",
                    value=job.get("notes", ""),
                    key=job["title"] + "_notes"
                )

                if notes != job.get("notes", ""):

                    job["notes"] = notes

                    with open("jobs.json", "w") as file:
                        json.dump(jobs, file, indent=4)

                    st.rerun()

            with col2:
                delete_button = st.button(
                    "🗑️ Delete",
                    key=job["title"]
                )

                if delete_button:

                    jobs.remove(job)

                    with open("jobs.json", "w") as file:
                        json.dump(jobs, file, indent=4)

                    st.rerun()

                updated_status = st.selectbox(
                    "Update Status",
                    ["New", "Applied", "Interview"],
                    index=["New", "Applied", "Interview"].index(job["status"]),
                    key=job["title"] + "_status"
                )

                if updated_status != job["status"]:

                    job["status"] = updated_status

                    with open("jobs.json", "w") as file:
                        json.dump(jobs, file, indent=4)

                    st.rerun()	