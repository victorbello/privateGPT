import requests
import os
import time
import csv
import sys
from fake_useragent import UserAgent

# Create a UserAgent object to generate a fake user agent string
ua = UserAgent()

# Create a Session object to persist cookies across requests
session = requests.Session()

# Define the base URL of your API
BASE_API_URL = "https://issaquah.civicweb.net/api/document/{}/getchildlist?includeAll=true&page=1&resultsPerPage=1000&documentIdList=&_={}"
FILE_URL = "https://issaquah.civicweb.net/filepro/document/{}/{}.pdf"

def get_json_from_api(url):
    # Call the API and convert the result to JSON
    try:
        response = session.get(url, headers={'User-Agent': ua.random})
        response.raise_for_status()  # Raise exception if the request failed
    except requests.HTTPError as e:
        if e.response.status_code == 403:
            print("Received 403 error. Retrying in 2 seconds...")
            time.sleep(2)  # Wait 2 seconds
            response = session.get(url, headers={'User-Agent': ua.random})
            response.raise_for_status()  # Raise exception if the request failed again
        else:
            raise  # Raise any other exceptions
    return response.json()

def process_objects(object_list, csv_writer):
    for obj in object_list:
        # Get the ID and Title of each object
        id = obj['Id']
        title = obj['Title']
        print(f"Processing {title} with id {id}")

        # Construct the URL for this object, including the current Unix timestamp
        epoch = int(time.time())  # Current Unix timestamp
        url = BASE_API_URL.format(id, epoch)

        # If the object has children, get them
        if obj['HasChildren']:
            # Get the list of child objects and process them
            children_json = get_json_from_api(url)
            process_objects(children_json, csv_writer)
        else:
            # If the object has no children, write the associated file URL to the CSV file
            file_url = FILE_URL.format(id, title)
            csv_writer.writerow([id, title, file_url])  # Write data row

def main():
    # Check if enough command-line arguments were provided
    if len(sys.argv) != 3:
        print("Usage: python script.py <initial_id> <csv_file>")
        sys.exit(1)

    # Get the initial ID and CSV file name from the command-line arguments
    initial_id = sys.argv[1]
    csv_file_name = sys.argv[2]

    # Open the CSV file
    csv_file = open(csv_file_name, "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["ID", "Title", "URL"])  # Write header row

    # Call the API to get the initial list of objects
    initial_epoch = int(time.time())  # Current Unix timestamp
    initial_url = BASE_API_URL.format(initial_id, initial_epoch)
    initial_json = get_json_from_api(initial_url)

    # Process the list of objects
    process_objects(initial_json, csv_writer)

    # Close the CSV file
    csv_file.close()

if __name__ == "__main__":
    main()
