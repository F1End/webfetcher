"""
Run checks on file output (website content) from fetch module
"""
import requests
from typing import Optional
from pathlib import Path

from src import validatehtml


class FileCheck:
    def __init__(self, checked_file: str, check_type: dict, tolerance: float = 0.05):
        self.checked_file = checked_file
        self.check_type = check_type
        self.tolerance = tolerance
        self.check_file_content = None
        self.check_against_content = None
        self.check_map = {"html_structure": self.check_html,
                          "against_site": self.check_against_site,
                          "against_file": self.check_against_file}

    def run_checks(self):
        issues = []
        for check, param in self.check_type.items():
            flagged = self.check_map[check](param)
            if flagged:
                issues.append(flagged)
        if issues:
            raise Exception(issues)

    def check_against_file(self, check_against: str) -> Optional[str]:
        self._load_contents(check_against, against_file=True)
        ratio = self.check_size()
        if ratio:
            return self._format_size_diff_msg(check_against, ratio)

    def check_against_site(self, check_against: str) -> Optional[str]:
        self._load_contents(check_against, against_file=False)
        ratio = self.check_size()
        if ratio:
            return self._format_size_diff_msg(check_against, ratio)

    def _format_size_diff_msg(self, check_against: str, ratio: float):
        msg = f"Size difference is {ratio} against {check_against}" \
              f", which is above threshold {self.tolerance}."
        return msg

    def check_html(self, full_check: bool = True) -> str:
        self.check_file_content = self._load_from_file(self.checked_file)
        errors = validatehtml.ChkHtmlStructure(full_check=full_check).run_checks(self.check_file_content)
        return errors

    def check_size(self):
        difference = self._get_size(self.check_file_content) \
                     - self._get_size(self.check_against_content)
        ratio = abs(difference) / self._get_size(self.check_file_content)
        if ratio > self.tolerance:
            return ratio

    def check_content(self):
        raise NotImplemented

    def check_minimum_content(self):
        raise NotImplemented

    def _load_contents(self, check_against: str, against_file: bool = True):
        self.check_file_content = self._load_from_file(self.checked_file)
        if against_file:
            self.check_against_content = self._load_from_file(check_against)
        else:
            self.check_against_content = self._load_from_url(check_against)

    def _load_from_file(self, file_path) -> str:
        file_path = Path(file_path)
        with open(file_path) as file:
            data = file.read()
        return data

    def _load_from_url(self, url: str) -> str:
        response = requests.get(url)
        content = response.content
        return content

    def _get_size(self, content: str) -> int:
        return len(content)
