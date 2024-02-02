import requests
import csv
import json

"""
    Don't forget to install the dependency ==> 'pip install requests'
"""


class Scraper:

    def __init__(self):
        self.base_url = "https://www.gutenberg.org/cache/epub/"
        self.session = requests.session()
        self.csv_file = 'resource/gutenberg_metadata.csv'
        self.db_file = "resource/db/books.json"

    def get_url_and_id(self, link: str):
        id = link.split("/")[-1]
        url = f"{self.base_url}{id}/pg{id}.txt"
        return url, id

    def scrape(self, url: str, id: str) -> bool:
        response = self.session.get(url, stream=True)
        filename = f"resource/books/{id}.txt"
        if response.ok:
            chunk_size = 1024  # 1 KB
            with open(filename, "wb") as f:
                # Iterate over the response content in chunks
                for chunk in response.iter_content(chunk_size=chunk_size):
                    # Process the chunk as needed
                    if chunk:
                        f.write(chunk)
            return True
        return False

    def run(self):
        threshold = 1664
        fetched = 0
        db = {}
        # Open the CSV file in read mode
        with open(self.csv_file, 'r') as file:
            # Create a CSV reader object as a dictionary reader
            csv_reader = csv.DictReader(file)

            # Iterate through each row in the CSV file
            for row in csv_reader:
                url, id = self.get_url_and_id(row["Link"])
                if self.scrape(url, id):
                    fetched += 1
                    print("Downloading .... ", round(fetched / threshold, 2) * 100, "%")
                    data = {
                        "title": row["Title"],
                        "author": row["Author"],
                        "category": row["Bookshelf"],
                        "id": id
                    }
                    db[id] = data
                if fetched == threshold:
                    break
        self.store(db)
        print("========== Done ==========")

    def store(self, data):
        with open(self.db_file, "w") as f:
            json.dump(data, f)


if __name__ == "__main__":
    # It takes around 5 minutes
    # Spec 16gb ram cpu i7
    # 6 cores
    Scraper().run()
