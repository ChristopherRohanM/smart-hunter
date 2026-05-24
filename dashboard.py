from openai import OpenAI
import streamlit as st
import sqlite3
import pandas as pd
import re
from PyPDF2 import PdfReader

client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

st.set_page_config(
    page_title="Smart Hunter",
    layout="wide"
)

# LOAD JOBS FROM DATABASE
connection = sqlite3.connect("jobs.db")
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("SELECT * FROM jobs")

jobs = cursor.fetchall()

connection.close()

# TITLE
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

uploaded_resume = st.file_uploader(
    "📄 Upload Resume",
    type=["txt", "pdf"]
)

resume_text = ""

if uploaded_resume is not None:

    if uploaded_resume.type == "application/pdf":

        pdf_reader = PdfReader(uploaded_resume)

        for page in pdf_reader.pages:

            text = page.extract_text()

            if text:
                resume_text += text

    else:

        resume_text = uploaded_resume.read().decode("utf-8")

    st.success("Resume Uploaded Successfully 😄")

    with st.spinner("🤖 AI is analyzing resume..."):

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert recruiter."
                },
                {
                    "role": "user",
                    "content": f"Summarize this resume:\n\n{resume_text}"
                }
            ]
        )

        ai_summary = response.choices[0].message.content

    st.markdown("## 🤖 AI Resume Summary")

    st.write(ai_summary)

else:

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

            connection = sqlite3.connect("jobs.db")

            cursor = connection.cursor()

            cursor.execute("""
            INSERT INTO jobs (
                title,
                company,
                location,
                url,
                status,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                title,
                company,
                location,
                url,
                status,
                ""
            ))

            connection.commit()

            connection.close()

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
            job["notes"]
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

                if resume_text != "":

                    with st.spinner("🤖 AI evaluating candidate fit..."):

                        fit_response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are an expert technical recruiter."
                                },
                                {
                                    "role": "user",
                                    "content": f"""
                                    Resume:
                                    {resume_text}

                                    Job:
                                    Title: {job["title"]}
                                    Company: {job["company"]}
                                    Notes: {job["notes"]}

                                    Explain why this candidate is or is not a good fit.
                                    Keep it short and recruiter-friendly.
                                    """
                                }
                            ]
                        )

                        fit_analysis = fit_response.choices[0].message.content

                    st.info(fit_analysis)

                if st.button(
                    "✉️ Generate Outreach",
                    key=str(job["id"]) + "_outreach"
                ):

                    with st.spinner("🤖 AI writing recruiter outreach..."):

                        outreach_response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are an expert recruiter writing LinkedIn outreach."
                                },
                                {
                                    "role": "user",
                                    "content": f"""
                                    Resume:
                                    {resume_text}

                                    Job:
                                    Title: {job["title"]}
                                    Company: {job["company"]}

                                    Write a professional recruiter outreach message.
                                    Keep it concise and friendly.
                                    """
                                }
                            ]
                        )

                        outreach_message = outreach_response.choices[0].message.content

                    st.markdown("### ✉️ AI Outreach Message")

                    st.write(outreach_message)

                st.markdown(
                    f"[🔗 Open Job Link]({job['url']})"
                )

                notes = st.text_area(
                    "📝 Notes",
                    value=job["notes"],
                    key=str(job["id"]) + "_notes"
                )

                if notes != job["notes"]:

                    connection = sqlite3.connect("jobs.db")

                    cursor = connection.cursor()

                    cursor.execute("""
                    UPDATE jobs
                    SET notes = ?
                    WHERE id = ?
                    """, (
                        notes,
                        job["id"]
                    ))

                    connection.commit()

                    connection.close()

                    st.rerun()

            with col2:

                delete_button = st.button(
                    "🗑️ Delete",
                    key=str(job["id"])
                )

                if delete_button:

                    connection = sqlite3.connect("jobs.db")

                    cursor = connection.cursor()

                    cursor.execute("""
                    DELETE FROM jobs
                    WHERE id = ?
                    """, (
                        job["id"],
                    ))

                    connection.commit()

                    connection.close()

                    st.rerun()

                updated_status = st.selectbox(
                    "Update Status",
                    ["New", "Applied", "Interview"],
                    index=["New", "Applied", "Interview"].index(job["status"]),
                    key=str(job["id"]) + "_status"
                )

                if updated_status != job["status"]:

                    connection = sqlite3.connect("jobs.db")

                    cursor = connection.cursor()

                    cursor.execute("""
                    UPDATE jobs
                    SET status = ?
                    WHERE id = ?
                    """, (
                        updated_status,
                        job["id"]
                    ))

                    connection.commit()

                    connection.close()

                    st.rerun()