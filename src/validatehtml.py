"""
Checking if a file (received in str) has valid html structure
If there are unopened closing tags or unclosed openings -> broken.

"""
import re


# class HTMLStructureError(Exception):
#     def __init__(self, opening_errors, closing_errors):


class ChkHtmlStructure:
    def __init__(self, full_check: bool = True, raise_exception: bool = False):
        """
        :param full_check: if T -> Find all issues and then return/raise exception,
                           if F -> First issue found will interrupt the script
        :param raise_exception: if T -> Raises exception
                        if F -> Return dict with errors
        """
        tag_regex = r"<(/?\w+)[^>]*>"
        self.raise_exception = raise_exception
        self.full_check = full_check
        self.pattern = re.compile(tag_regex)
        self.self_closing_tags = {"area", "base", "br",
                                  "col", "embed", "hr",
                                  "img", "input", "link",
                                  "meta", "param", "source",
                                  "track", "wbr"}
        self.tag_stack = []
        self.errors = {"unclosed_opening": [],
                       "unexpected_closing": []}

    def run_checks(self, html_content: str):
        for match in self.pattern.finditer(html_content):
            tag = match.group(1).lower()
            self._process_tag(tag)

        self._process_outcome()

    def _process_outcome(self):
        self._move_errors_from_stack()
        errors = len(self.errors["unclosed_opening"]) + len(self.errors["unexpected_closing"])
        if errors:
            self._return_errors()

    def _move_errors_from_stack(self):
        if self.tag_stack:
            for not_closed in self.tag_stack:
                self.errors["unclosed_opening"].append(not_closed)
            self.tag_stack = []

    def _process_tag(self, tag: str):
        if tag.startswith("/"):
            self._process_closing_tag(tag)
        elif tag not in self.self_closing_tags:
            self.tag_stack.append(tag)

    def _process_closing_tag(self, tag: str):
        tag_name = tag[1:]
        unopened_closing_tag = (not self.tag_stack or self.tag_stack[-1] != tag_name)
        if unopened_closing_tag:
            self._process_error(tag, opening_tag=False)
        self.tag_stack.pop()

    def _process_error(self, tag: str, opening_tag: True):
        if opening_tag:
            self.errors["unclosed_opening"].append(tag)
        else:
            self.errors["unexpected_closing"].append(tag)
        if self.full_check is False:
            self._return_errors()

    def _return_errors(self) -> dict:
        if self.raise_exception:
            raise Exception(f"Errors in HTML structure: \n{self.errors}")
        return self.errors
