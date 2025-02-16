"""
Checking if a file (received in str) has valid html structure
If there are unopened closing tags or unclosed openings -> broken.

"""
import re


class HTMLStructureError(Exception):
    def __init__(self, errors, msg="Inconsistencies in HTML structure found."):
        self.unclosed = errors["unclosed_opening"]
        self.unopened = errors["unexpected_closing"]
        self.msg = msg
        super().__init__(msg)

    def format_errors(self):
        msg = ""
        if self.unopened:
            format_unopened = "; ".join(str(tag) for tag in self.unopened)
            msg += f"\nUnopened closing tags: {format_unopened}"
        if self.unclosed:
            format_unclosed = "; ".join(str(tag) for tag in self.unclosed)
            msg += f"\nUnclosed opening tags: {format_unclosed}"
        return msg

    def __str__(self):
        return self.msg + self.format_errors()


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
        cleaned_html_content = self._clean_content(html_content)
        for match in self.pattern.finditer(cleaned_html_content):
            tag = match.group(1).lower()
            self._process_tag(tag)
        return self._process_outcome()

    def _clean_content(self, html_content: str) -> str:
        extract_comments = re.sub(r'<!--.*?-->', "", html_content, flags=re.DOTALL)
        extract_embedded = re.sub(r'<script.*?</script>|<style.*?</style>',
                                  "", extract_comments, flags=re.DOTALL)
        return extract_embedded

    def _process_outcome(self):
        self._move_errors_from_stack()
        errors = len(self.errors["unclosed_opening"]) + len(self.errors["unexpected_closing"])
        if errors:
            return self._return_errors()

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
        tag_stack_empty = not self.tag_stack
        last_opening_different = self.tag_stack[-1] != tag_name
        unopened_closing_tag = tag_stack_empty or last_opening_different
        if unopened_closing_tag:
            self._process_error(tag, opening_tag=False)
        else:
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
            raise HTMLStructureError(errors=self.errors, msg=f"Errors in HTML structure: \n{self.errors}")
        return self.errors
