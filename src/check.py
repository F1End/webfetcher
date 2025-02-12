"""
Run checks on file output (website content) from fetch module
"""
from io import BytesIO
import requests

import html5lib
from bs4 import BeautifulSoup

# class to load file to run checks on
class FileCheck:
    def __init__(self, checked_file: str, check_type: str, check_against: str, tolerance: float = 0.95):
        self.checked_file = checked_file
        self.check_type = check_type
        self.check_agaist = check_against
        self.tolerance = tolerance
        self.check_file_content = None
        self.check_against_content = None

    def run_check(self):
        raise NotImplemented

    def check_html(self) -> str:
        htmlparser = html5lib.HTMLParser(strict=True)
        try:
            htmlparser.parse(BytesIO(self.check_against_content))
            return "HTML is valid"
        except Exception as e:
            return f"Errors occured during loading: {e}"
        # try:
        #     soup = BeautifulSoup(self.check_file_content, 'html.parser')
        #     if soup.find():
        #         return "HTML is valid"
        # except Exception as e:
        #     return f"Errors occured during loading: {e}"



    def check_size(self):
        raise NotImplemented

    def check_content(self):
        raise NotImplemented

    def check_minimum_content(self):
        raise NotImplemented

    def _load_contents(self, against_file: bool = True):
        self.check_file_content = self._load_from_file(self.checked_file)
        if against_file:
            self.check_against_content = self._load_from_file(self.check_agaist)
            print(f"Checking against {self.check_agaist}")
        else:
            self.check_against_content = self._load_from_url(self.check_agaist)

    def _load_from_file(self, file_path) -> str:
        with open(file_path,"r") as file:
            data = file.read()
        return data

    def _load_from_url(self, url: str) -> str:
        response = requests.get(url)
        content = response.content
        return content

    def _get_size(self, content: str) -> int:
        raise NotImplemented

    def _get_file_content(self):
        raise NotImplemented

    def _load_url_content(self):
        raise NotImplemented