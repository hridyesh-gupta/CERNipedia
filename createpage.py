import requests
import csv
import pandas as pd

# IMPORTANT: Update these values while pushing to production
API_URL = "http://localhost/CERNipedia/api.php"  # Change this to your MediaWiki's api.php URL
WIKI_USERNAME = "PageCreatorBot"      # Change this to your bot account's username
WIKI_PASSWORD = "Hridyesh@1"      # Change this to your bot account's password
CSV_FILENAME = "table.csv"   # Change this to the name of your CSV file

# No need to edit below this line
def main():
    """
    Main function to log in, read CSV, and create wiki pages.
    """
    session = requests.Session()

    # Login to the wiki and get an edit token
    csrf_token = login_to_wiki(session)
    if not csrf_token:
        print("Login failed. Exiting.")
        return

    print("Login successful. Ready to create pages.")

    already_exists_rows = []  # To collect rows whose pages already exist

    # Read the CSV file and create pages
    try:
        with open(CSV_FILENAME, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                page_title = row.get('title')
                page_content = row.get('content')

                if not page_title or not page_content:
                    print(f"Skipping row with missing title or content: {row}")
                    continue

                if page_exists(session, page_title):
                    print(f"Page '{page_title}' already exists. Skipping.")
                    already_exists_rows.append({'title': page_title, 'content': page_content})
                    continue

                create_page(session, page_title, page_content, csrf_token)
    
    except FileNotFoundError:
        print(f"Error: The file '{CSV_FILENAME}' was not found.")
    except Exception as e:
        print(f"An error occurred while reading the CSV or creating pages: {e}")

    # After processing, print all rows whose pages already existed
    if already_exists_rows:
        print("\nPages that already existed (title + content from CSV):")
        for row in already_exists_rows:
            print(f"Title: {row['title']}\nContent: {row['content']}\n{'-'*40}")
    else:
        print("\nNo pages were skipped due to already existing titles.")

def login_to_wiki(session):
    """
    Logs into MediaWiki using the API and retrieves a CSRF token for editing.
    """
    print(f"Attempting to log in as '{WIKI_USERNAME}'...")

    # Step 1: Get a login token
    response = session.get(API_URL, params={
        'action': 'query',
        'meta': 'tokens',
        'type': 'login',
        'format': 'json'
    })
    response.raise_for_status()
    login_token = response.json()['query']['tokens']['logintoken']

    # Step 2: Use the login token to log in
    response = session.post(API_URL, data={
        'action': 'login',
        'lgname': WIKI_USERNAME,
        'lgpassword': WIKI_PASSWORD,
        'lgtoken': login_token,
        'format': 'json'
    })
    response.raise_for_status()
    if response.json()['login']['result'] != 'Success':
        print(f"Login failed: {response.json()['login']['reason']}")
        return None
    
    # Step 3: Get the CSRF token (for editing pages)
    response = session.get(API_URL, params={
        'action': 'query',
        'meta': 'tokens',
        'format': 'json'
    })
    response.raise_for_status()
    csrf_token = response.json()['query']['tokens']['csrftoken']
    
    return csrf_token

def page_exists(session, title):
    response = session.get(API_URL, params={
        'action': 'query',
        'titles': title,
        'format': 'json'
    })
    response.raise_for_status()
    pages = response.json()['query']['pages']
    page = next(iter(pages.values()))
    return '-1' not in pages  # If pageid is -1, the page does not exist

def create_page(session, title, content, token):
    """
    Creates or edits a page on the wiki.
    """
    print(f"Creating page: '{title}'...")
    try:
        response = session.post(API_URL, data={
            'action': 'edit',
            'title': title,
            'text': content,
            'summary': 'Page created automatically by script',
            'token': token,
            'format': 'json',
            'bot': True # Mark this edit as a bot edit
        })
        response.raise_for_status()
        result = response.json()

        if 'edit' in result and result['edit']['result'] == 'Success':
            print(f"Successfully created or updated page '{title}'.")
        else:
            print(f"Failed to create page '{title}'. Response: {result}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while creating page '{title}': {e}")


if __name__ == "__main__":
    main()