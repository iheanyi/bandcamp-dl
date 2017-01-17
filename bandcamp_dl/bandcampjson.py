import demjson
import re


class BandcampJSON:
    def __init__(self, body, var_name: str, js_data=None):
        self.body = body
        self.var_name = var_name
        self.js_data = js_data
        self.regex = re.compile(r"(?<=var\s" + var_name + "\s=\s).*?(?=};)", re.DOTALL)

    def get_js(self) -> str:
        """Get <script> element containing the data we need and return the raw JS

        :return js_data: Raw JS as str
        """
        self.js_data = self.body.find("script", {"src": False}, text=re.compile(self.var_name)).string
        return self.js_data

    def extract_data(self, js: str) -> str:
        """Extract values from JS dictionary

        :param js: Raw JS
        :return: Contents of dictionary as str
        """
        self.js_data = self.regex.search(js).group().replace('" + "', '') + "}"
        return self.js_data

    def js_to_json(self) -> str:
        """Convert JavaScript dictionary to JSON

        :return: JSON as str
        """
        js = self.get_js()
        data = self.extract_data(js)
        # Decode with demjson first to reformat keys and lists
        js_data = demjson.decode(data)
        # Encode to make valid JSON
        js_data = demjson.encode(js_data)
        return js_data
