# ---------------------------------------------
# Prompts
# ---------------------------------------------
def prompt_job_analysis(job_text: str):
    return f"""
You are an expert hiring manager.

Analyze this job description:

1. Provide a 3–5 bullet summary of the role.
2. List top 10 required skills (technical + soft).
3. Extract explicit requirements:
   - years of experience
   - education
   - location
   - programming languages
4. Suggest 5–10 keywords for ATS optimization.

JOB DESCRIPTION:
{job_text}
"""


def prompt_cv_analysis(cv_text: str):
    return f"""
You are an expert recruiter.

Analyze this CV:

1. Summarize candidate in 3–5 bullets.
2. List skills grouped into:
   - Technical
   - Tools/Frameworks
   - Domain Knowledge
   - Soft Skills
3. Identify the candidate's seniority level.
4. List 5–10 strong points.
5. Give 5–10 improvement suggestions.

CV:
{cv_text}
"""


def prompt_match(job: str, cv: str):
    return f"""
Compare this job description with the CV.

1. Give a match score (0–100).
2. Explain your reasoning.
3. List strong matches.
4. List missing skills.
5. Suggest improvements to make the CV fit the role better.
6. Give the client an overall advice with respect to the job and CV

JOB:
{job}

CV:
{cv}
"""