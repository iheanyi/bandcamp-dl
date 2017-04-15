import re

import demjson


class BandcampJSON:
    def __init__(self, body):
        self.body = body
        self.targets = ['TralbumData', 'EmbedData', 'pagedata']
        self.json_data = []

    def generate(self) -> list:
        """Iterate through targets grabbing needed data"""
        for target in self.targets:
            if target[:4] == 'page':
                self.get_pagedata()
            else:
                self.regex = re.compile(r"(?<=var\s" + target + "\s=\s).*?(?=};)", re.DOTALL)
                self.target = target
                self.js_to_json()
        return self.json_data

    def get_pagedata(self):
        """Grab bandcamp pagedata JSON"""
        pagedata = self.body.find('div', {'id': 'pagedata'})['data-blob']
        # Add pagedata to the list of JSON strings
        self.json_data.append(pagedata)

    def get_js(self):
        """Get <script> element containing the data we need and return the raw JS"""
        self.js_data = self.body.find("script", {"src": False}, text=re.compile(self.target)).string
        self.extract_data(self.js_data)

    def extract_data(self, js: str):
        """Extract values from JS dictionary

        :param js: Raw JS
        """
        self.js_data = self.regex.search(js).group().replace('" + "', '') + "}"

    def js_to_json(self):
        """Convert JavaScript dictionary to JSON"""
        self.get_js()
        # Decode with demjson first to reformat keys and lists
        decoded_js = demjson.decode(self.js_data)
        # Encode to make valid JSON, add to list of JSON strings
        self.json_data.append(demjson.encode(decoded_js))
