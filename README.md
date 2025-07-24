# Job Bot - AI-Powered Job Analysis Tool

This application analyzes job listings and provides personalized career advice by comparing your skills with job requirements using AI.

## Features

- Scrapes job listings from Google Jobs via ScraperAPI
- Extracts required skills and qualifications from job postings using Claude AI
- Analyzes skill match between your profile and job requirements
- Provides personalized career advice and learning recommendations
- Saves analysis results to JSON file for review

## Prerequisites

- Python 3.7 or higher
- ScraperAPI account and API key
- Anthropic API account and API key

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.env` file in the project root with your API keys:**

   ```
   SCRAPER_API_KEY=your_scraper_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

3. **Get your API keys:**
   - **ScraperAPI:** Sign up at https://www.scraperapi.com/
   - **Anthropic:** Sign up at https://console.anthropic.com/

## Usage

Run the application:

```bash
python job-bot.py
```

The script will prompt you for:

- Job type you're looking for (e.g., "Software Engineer", "Data Scientist")
- Preferred location (optional, defaults to US)
- Your skills (comma-separated list)

The application will:

1. Search for relevant job listings
2. Analyze the top 5 jobs found
3. Extract required skills for each position
4. Compare your skills with job requirements
5. Generate personalized career advice
6. Save results to `job_analysis_results.json`

## Output

- Console output showing analysis progress and results
- JSON file with detailed analysis for each job
- Match percentages and specific recommendations

## Files

- `job-bot.py` - Main application script
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (create this file)
- `job_analysis_results.json` - Analysis output (generated after running)

## API Usage

- **ScraperAPI:** Used for job scraping (Google Jobs endpoint)
- **Anthropic Claude:** Used for skill extraction and analysis

**Note:** API usage will incur costs based on your plan limits.

## Thanks

https://www.youtube.com/watch?v=zz1VKNiCB4M
