

{
    "title":"title of the movie",
    "releaseYear":"when the movie was released",
    "genre":"genre of the movie",
    "coverUrl":"url-to-image-in-cloud-storage"
}


from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.common.by import By
from decouple import config
from bs4 import BeautifulSoup

SBR_WEBDRIVER = config("SBR_WEBDRIVER", default=None)

# Debugging: Print the SBR_WEBDRIVER to ensure it is loaded correctly
print(f"SBR_WEBDRIVER: {SBR_WEBDRIVER}")

if not SBR_WEBDRIVER:
    raise ValueError("SBR_WEBDRIVER is not set. Please check your environment variables or .env file.")

def scrape(url=None, body_only=True, solve_captcha=False, wait_seconds=2):
    print('Connecting to Scraping Browser...')
    sbr_connection = Remote(command_executor=SBR_WEBDRIVER, options=ChromeOptions())
    html = ""
    with sbr_connection as driver:
        print(f'Connected! Navigating to {url}')
        driver.get(url)
        if wait_seconds > 0:
            driver.implicitly_wait(wait_seconds)
        if solve_captcha:
            # CAPTCHA handling: If you're expecting a CAPTCHA on the target page, use the following code snippet to check the status of Scraping Browser's automatic CAPTCHA solver
            print('Waiting captcha to solve...')
            solve_res = driver.execute('executeCdpCommand', {
                'cmd': 'Captcha.waitForSolve',
                'params': {'detectTimeout': 10000},
            })
            print('Captcha solve status:', solve_res['value']['status'])
        print('Navigated! Scraping page content...')
        html = driver.page_source
        if body_only:
            soup = BeautifulSoup(html, 'html.parser')
            body = soup.find('body')
            html = body.decode_contents() if body else ''
    return html

def extract_movie_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    job_listings = soup.find_all('article', class_='job-tile')
    jobs = []
    for job in job_listings:
        # Extract the project title
        title_tag = job.find('h2', class_='job-tile-title')
        title = title_tag.get_text(strip=True) if title_tag else 'N/A'

        # Extract the job description
        description = job.find('p', class_='mb-0 text-body-sm').text.strip() if job.find('p', class_='mb-0 text-body-sm') else 'No Description'

        # Extract job attributes (skills/tech stack)
        skills = []
        skill_tags = job.find_all('span', class_='air3-token')
        for skill in skill_tags:
            skills.append(skill.get_text(strip=True))

        # Store the extracted information
        jobs.append({
            'Project Title': title,
            'Description': description,
            'Skills': skills
        })
    return jobs

BASE_URL = "https://net9jaseries.com/tag/"

genre_types = ["action", "adventure", "comedy", "thriller", "horror", "crime", "sci-fi", "romance"]

for genre in genre_types:
    query_url =  BASE_URL + genre
    html_content = scrape()