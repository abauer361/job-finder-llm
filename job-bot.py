import requests
import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

scraper_api_key = os.getenv("SCRAPER_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# payload = {
#     "api_key": scraper_api_key,
#     "query": "Forward Deployed Engineer",
#     "country": "us",
#     "sort_by": "date",
#     "output_format": "json",
#     "num": "700",
# }

# r = requests.get('https://api.scraperapi.com/structured/google/jobs', params=payload)
# print(r.text)

client = Anthropic(api_key=anthropic_api_key)

def scrape_jobs(query="Forward Deployed Engineer", country="us", num=5):
    """
    Scrape jobs from ScraperAPI's Google Jobs endpoint
    """
    
    payload = { 
        'api_key': scraper_api_key, 
        'query': query, 
        'country_code': country,
        'sort_by': "date",
        'num': str(num)
    }
    try:
        r = requests.get('https://api.scraperapi.com/structured/google/jobs', params=payload)
        r.raise_for_status()

        # Parse the JSON response
        response_data = json.loads(r.content)

        # Return jobs_results directly if available
        if "jobs_results" in response_data:
            print(f"Scraped {len(response_data['jobs_results'])} jobs.")
            return {"jobs": response_data["jobs_results"]}
        else:
            return response_data
    except Exception as e:
        print(f"Error scraping jobs: {e}")
        return None
    

def extract_job_skills(job):
    """
    Use LLM to extract skills from job description
    """

    title = job.get("title", "")
    company = job.get("company_name", "")
    location = job.get("location", "")

    # Note: The job description isn't available in the payload
    # We will infer skills from the job title and company instead

    # Prepare a prompt for the LLM
    prompt = f"""
    Based on the following job listing information, identify the skills, qualifications, and experience required:

    Job Title: {title}
    Company: {company}  
    Location: {location}

    Please infer and extract:
    1. Required technical skills (programming languages, frameworks, tools, etc.)
    2. Domain knowledge areas
    3. Estimated years of experience required
    4. Typical education requirements for this role
    5. Likely soft skills needed

    Note that you are inferring these requirements based solely on the job title and company.

    Format as structured JSON.
    Keys should be:
    - technical_skills
    - domain_knowledge
    - years_of_experience
    - education_requirements
    """

    # Call the LLM
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            system="You are an AI specialist in job analysis and skill extraction. You are given a job title and company name and you need to infer the skills, qualifications, and experience required for the role. Please respond with valid JSON format.",
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse the JSON response
        return json.loads(response.content[0].text)
    except Exception as e:
        print(f"Error extracting job skills: {e}")
        return None
    
    
def analyze_skills_match(user_skills, job_skills):
    """
    Compare user skills to job requirements and calculate match percentage
    """

    prompt = f"""
    Compare the following user skills with the job requirements and calculate the match percentage:

    User Skills:
    {json.dumps(user_skills)}

    Job Requirements:
    {json.dumps(job_skills)}

    Please provide:
    1. Overall match percentage (0-100%)
    2. Matched skills list
    3. Missing skills list
    4. Recommended learning path to close the skill gap
    5. Specific resources (courses, projects) to learn the missing skills

    Format as structured JSON.
    Keys should be:
    - overall_match_percentage
    - matched_skills
    - missing_skills
    - learning_path
    - resources
    """

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            system="You are an AI specialist in job analysis and skill matching. You are given a user's skills and a job requirements and you need to compare them and provide a detailed analysis. Please respond with valid JSON format.",
            messages=[{"role": "user", "content": prompt}]
        )
    # Parse the JSON response
        return json.loads(response.content[0].text)
    except Exception as e:
        print(f"Error analyzing skills match: {e}")
        return None
    

def generate_career_advice(match_analysis, job):
    """
    Generate personalized career advice based on skill match analysis
    """

    title = job.get("title", "")
    company = job.get("company_name", "")
    match_percentage = match_analysis.get("overall_match_percentage", [])
    missing_skills = match_analysis.get("missing_skills", [])
    learning_path = match_analysis.get("learning_path", "")
    resources = match_analysis.get("resources", [])

    prompt = f"""
    Create personalized career advice for a candidate applying for the following job given the skill match analysis:

    Job Title: {title}
    Company: {company}
    Match Percentage: {match_percentage}
    Missing Skills: {missing_skills}

    The advice should be encouraging but realistic, including:
    1. A summary of their readiness for the role
    2. The key gaps they need to address
    3. A step by step action plan with timeline
    4. Specific resources (courses, projects) to learn the missing skills
    5. Alternative roles they might be better suited for now

    Make the advice actionable and specific
    """

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            system="You are an AI career coach specializing in job search and career development. You are given a skill match analysis and a job listing and you need to generate personalized career advice for a candidate applying for the job.",
            messages=[{"role": "user", "content": prompt}]
        )
    # Parse the JSON response
        return response.content[0].text
    except Exception as e:
        print(f"Unable to generate career advice: {e}")
        return None
    

def main():
    # Get user input
    job_query = input(
        "What type of job are you looking for? "
    )
    user_location = input(
        "Preferred location (must be in US, blank for US as a whole): "
    )
    user_skills = input(
        "List your skills (comma separated e.g. Python, SQL, AWS, etc.): "
    )

    print("\nAnalyzing your job search...")

    # Parse user skills
    user_skills = [skill.strip() for skill in user_skills.split(",")]

    # Configure search params
    country = "us" # Default to US
    if user_location:
        query = f"{job_query} in {user_location}"
    else:
        query = job_query

    # Scrape jobs
    jobs_data = scrape_jobs(query)

    if not jobs_data:
        print("No jobs found or an error occurred during scraping. Please try again.")
        exit(1)
    
    print(f"Found {len(jobs_data['jobs'])} job listings.")

    # Process top 5 jobs (or fewer if less than 5 are available)
    top_jobs = jobs_data['jobs'][: min(5, len(jobs_data['jobs']))]
    results = []

    for i, job in enumerate(top_jobs):
        title = job.get("title", "Untitled Position")
        company = job.get("company_name", "Unknown Company")
        location = job.get("location", "Unknown Location")

        print(f"\n{"="*50}")
        print(f"\nProcessing job {i+1}/{len(top_jobs)}:")
        print(f"Title: {title}")
        print(f"Company: {company}")
        print(f"Location: {location}")
        print(f"{"="*50}\n")

        # Extract job skills
        print("Extracting job skills...")
        job_skills = extract_job_skills(job)
        if not job_skills:
            print("Unable to extract job skills. Skipping...")
            continue

        # Analyze skills match
        print("Analyzing skills match...")
        match_analysis = analyze_skills_match(user_skills, job_skills)
        if not match_analysis:
            print("Unable to analyze skills match. Skipping...")
            continue

        # Generate advice
        print("Generating personalized career advice...")
        advice = generate_career_advice(match_analysis, job)
        if not advice:
            print("Unable to generate career advice. Skipping...")
            continue
        
        # Store results
        results.append({
            "job": job,
            "skills_required": job_skills,
            "match_analysis": match_analysis,
            "advice": advice
        })

    print("\n=========== RESULTS ===========\n")
    for i, result in enumerate(results):
        job = result["job"]
        match = result["match_analysis"]

        print(f"Job: {i+1}: {job.get('title', 'Untitled Position')}")
        print(f"Company: {job.get('company_name', 'Unknown Company')}")
        print(f"Location: {job.get('location', 'Unknown Location')}")
        print(f"Match: {match.get('overall_match_percentage', 'N/A')}%")
        print(f"Link: {job.get('link', 'N/A')}")
        print("\n=== ADVICE ===\n")
        print(result["advice"])
        print("\n" + "="*50 + "\n")

    with open("job_analysis_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nJob analysis complete! Results saved to job_analysis_results.json")
        
if __name__ == "__main__":
    main()