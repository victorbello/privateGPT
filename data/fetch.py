import requests
import os
import time
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
    response = session.get(url, headers={'User-Agent': ua.random})
    response.raise_for_status()  # Raise exception if the request failed
    return response.json()

def download_file(url, local_filename):
    # Download a file from a URL
    headers = {'User-Agent': ua.random, 'Referer': url}
    with session.get(url, stream=True, headers=headers) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename

def process_objects(object_list, parent_directory):
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
            # Create a new directory for this object
            new_directory = os.path.join(parent_directory, title)
            os.makedirs(new_directory, exist_ok=True)

            # Get the list of child objects and process them in the new directory
            children_json = get_json_from_api(url)
            process_objects(children_json, new_directory)
        else:
            # If the object has no children, download the associated file
            file_url = FILE_URL.format(id, title)
            file_path = os.path.join(parent_directory, f"{title}.pdf")
            download_file(file_url, file_path)

def main():
    # Call the API to get the initial list of objects
    initial_id = "3338"  # ID of the initial object
    initial_epoch = int(time.time())  # Current Unix timestamp
    initial_url = BASE_API_URL.format(initial_id, initial_epoch)
    initial_json = get_json_from_api(initial_url)

    # Process the list of objects
    process_objects(initial_json, ".")

if __name__ == "__main__":
    main()
