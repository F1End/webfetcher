from unittest import TestCase, main
from unittest.mock import MagicMock, patch, call

from src import validatehtml


class TestChkHtmlStructure(TestCase):

    @patch('src.validatehtml.re')
    def setUp(self, re_mock):
        self.regex_mock = MagicMock()
        re_mock.compile.return_value = self.regex_mock
        self.test_checker = validatehtml.ChkHtmlStructure()

    @patch("src.validatehtml.re")
    def test_init(self, re_mock):
        fake_reg_compl = "compiled re"
        re_mock.compile.return_value = fake_reg_compl
        expected_regex_call = r'<(/?\w+)[^>]*>'
        default_check = True
        default_exception = False
        expected_closing_tags = set(("area", "base", "br",
                                     "col", "embed", "hr",
                                     "img", "input", "link",
                                     "meta", "param", "source",
                                     "track", "wbr"))
        default_stack_value = []
        default_errors = {"unclosed_opening": [],
                          "unexpected_closing": []}
        test_validator = validatehtml.ChkHtmlStructure()

        re_mock.compile.assert_called_with(expected_regex_call)
        self.assertEqual(test_validator.raise_exception, default_exception)
        self.assertEqual(test_validator.full_check, default_check)
        self.assertEqual(test_validator.pattern, fake_reg_compl)
        self.assertEqual(test_validator.self_closing_tags, expected_closing_tags)
        self.assertEqual(test_validator.tag_stack, default_stack_value)
        self.assertEqual(test_validator.errors, default_errors)

    @patch("src.validatehtml.ChkHtmlStructure._process_tag")
    @patch("src.validatehtml.ChkHtmlStructure._process_outcome")
    def test_run_checks(self, mock_process_outcome, mock_process_tag):
        fake_html_cotent = "<some> <\html> <content>"
        match_mock1, match_mock2, match_mock3 = MagicMock(), MagicMock(), MagicMock()
        group_mock = MagicMock()
        fake_tag_call_args = ["tag1", "tag2", "tag3"]
        group_mock.lower.side_effect = fake_tag_call_args
        match_mock1.group.return_value = group_mock
        match_mock2.group.return_value = group_mock
        match_mock3.group.return_value = group_mock
        self.test_checker.pattern.finditer.return_value = [match_mock1, match_mock2, match_mock3]

        self.test_checker.run_checks(fake_html_cotent)
        self.test_checker.pattern.finditer.assert_called_with(fake_html_cotent)
        match_mock1.group.assert_called_with(1)
        match_mock2.group.assert_called_with(1)
        match_mock3.group.assert_called_with(1)
        self.assertEqual(group_mock.lower.call_count, 3)
        mock_process_tag.assert_has_calls([call(fake_tag_call_args[0]),
                                          call(fake_tag_call_args[1]),
                                          call(fake_tag_call_args[2])])
        mock_process_outcome.assert_called_once()

    @patch("src.validatehtml.ChkHtmlStructure._move_errors_from_stack")
    @patch("src.validatehtml.ChkHtmlStructure._return_errors")
    def test__process_outcome(self, return_err_mock, move_err_mock):
        # Case 1: No errors
        self.test_checker._process_outcome()
        move_err_mock.assert_called_once()
        return_err_mock.assert_not_called()

        move_err_mock.reset_mock()
        return_err_mock.reset_mock()

        # Case 2: There are errors of both types
        self.test_checker.errors = {"unclosed_opening": ["head"],
                                    "unexpected_closing": ["/body"]}
        self.test_checker._process_outcome()
        move_err_mock.assert_called_once()
        return_err_mock.assert_called_once()

        move_err_mock.reset_mock()
        return_err_mock.reset_mock()

        # Case 3: Only opening errors
        self.test_checker.errors = {"unclosed_opening": ["head"],
                                    "unexpected_closing": []}
        self.test_checker._process_outcome()
        move_err_mock.assert_called_once()
        return_err_mock.assert_called_once()

        move_err_mock.reset_mock()
        return_err_mock.reset_mock()

        # Case 4: Only closing errors
        self.test_checker.errors = {"unclosed_opening": [],
                                    "unexpected_closing": ["/body"]}
        self.test_checker._process_outcome()
        move_err_mock.assert_called_once()
        return_err_mock.assert_called_once()

        move_err_mock.reset_mock()
        return_err_mock.reset_mock()



    def test__mover_errors_from_stack(self):
        # Case 1: Errors in stack (unclosed openings)
        unclosed = ["head", "body"]
        self.test_checker.tag_stack = unclosed

        self.test_checker._move_errors_from_stack()
        self.assertEqual(self.test_checker.errors["unclosed_opening"], unclosed)
        self.assertEqual(self.test_checker.tag_stack, [])

        # Case 2: No errors
        unclosed_mock = MagicMock()
        self.test_checker.errors = unclosed_mock

        self.test_checker._move_errors_from_stack()
        unclosed_mock.append.assert_not_called()
        self.assertEqual(self.test_checker.errors, unclosed_mock)


    @patch("src.validatehtml.ChkHtmlStructure._process_closing_tag")
    def test__process_tag(self, process_closing_mock):
        # Case 1: Opening tag
        tag = "head"
        self.test_checker._process_tag(tag)
        self.assertEqual(self.test_checker.tag_stack, [tag])
        # reset setUp
        self.test_checker.tag_stack = []

        # Case 2: Closing tag
        tag = "/head"
        self.test_checker._process_tag(tag)
        process_closing_mock.assert_called_with(tag)
        process_closing_mock.reset_mock()

        # Case 3: Self-closing tag
        tag = "img"
        self.test_checker._process_tag(tag)
        self.assertEqual(self.test_checker.tag_stack, [])
        process_closing_mock.assert_not_called()

    @patch("src.validatehtml.ChkHtmlStructure._return_errors")
    def test__process_error(self, return_err_mock):
        # Case 1: Opening tag
        tag = "body"

        self.test_checker._process_error(tag, opening_tag=True)
        self.assertEqual(self.test_checker.errors["unclosed_opening"], [tag])
        self.assertEqual(self.test_checker.errors["unexpected_closing"], [])
        return_err_mock.assert_not_called()
        # reset setUp
        self.test_checker.errors["unclosed_opening"] = []
        self.test_checker.errors["unexpected_closing"] = []

        # Case 2: Closing tag
        tag = "/body"

        self.test_checker._process_error(tag, opening_tag=False)
        self.assertEqual(self.test_checker.errors["unclosed_opening"], [])
        self.assertEqual(self.test_checker.errors["unexpected_closing"], [tag])
        return_err_mock.assert_not_called()
        # reset setUp
        self.test_checker.errors["unexpected_closing"] = []
        self.test_checker.errors["unexpected_closing"] = []

        # Case 3: Full check is true
        self.test_checker.full_check = False
        tag = "<body>"
        self.test_checker._process_error(tag, opening_tag=True)
        self.assertEqual(self.test_checker.errors["unclosed_opening"], [tag])
        self.assertEqual(self.test_checker.errors["unexpected_closing"], [])
        return_err_mock.assert_called_once()

        # reset setUp
        self.test_checker.errors["unclosed_opening"] = []
        self.test_checker.errors["unexpected_closing"] = []

    @patch("src.validatehtml.ChkHtmlStructure._process_error")
    def _process_closing_tag(self, process_error_mock):
        tag = "/head"

        # Case 1: matching opening in stack
        self.test_checker.tag_stack = ["head"]
        self.test_checker._process_closing_tag(tag)
        self.assertEqual(self.test_checker.tag_stack, [])
        process_error_mock.assert_not_called()

        # Case 2: empty stack
        self.test_checker.tag_stack = []
        self.test_checker._process_closing_tag(tag)
        process_error_mock.assert_called_with(tag, opening_tag=False)
        process_error_mock.reset_mock()

        # Case 3: not empty and not matching
        self.test_checker.tag_stack = ["head", "body"]
        self.test_checker._process_closing_tag(tag)
        process_error_mock.assert_called_with(tag, opening_tag=False)

    def test__return_errors(self):
        # Case 1: raise_exception is False
        errors = {"unclosed_opening": ["head"], "unexpected_closing": ["/body"]}
        self.test_checker.errors = errors
        returned_err = self.test_checker._return_errors()

        self.assertEqual(returned_err, errors)

        # Case 2: raise_exception is True
        self.test_checker.raise_exception = True
        self.assertRaises(Exception, self.test_checker._return_errors)
