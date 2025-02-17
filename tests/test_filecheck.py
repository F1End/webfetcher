from unittest import TestCase, main
from unittest.mock import MagicMock, patch, call

from src import filecheck


class TestFileCheck(TestCase):

    def setUp(self):
        file = "webpage.html"
        check_type = "size"
        old_file = "webpage_old.html"
        self.test_filecheck =filecheck.FileCheck(file, check_type, old_file)

    def test_init(self):
        file = "webpage.html"
        check_type = {"html_structure": True}
        tol = 0.07
        test_filecheck =filecheck.FileCheck(file, check_type, tol)
        self.assertEqual(test_filecheck.checked_file, file)
        self.assertEqual(test_filecheck.check_type, check_type)
        self.assertEqual(test_filecheck.tolerance, tol)

    @patch('src.filecheck.FileCheck.check_html')
    @patch('src.filecheck.FileCheck.check_against_site')
    @patch('src.filecheck.FileCheck.check_against_file')
    def test_run_checks(self, mock_html_chk, mock_site_chk, mock_file_chk):
        html_value = True
        url = "somewebsite.com/page.html"
        old_file = "path/to/my/file.html"
        # need to mack check_map due to patch not being able to mock calls this way
        fake_check_map = {"html_structure": mock_html_chk,
                          "against_site": mock_site_chk,
                          "against_file": mock_file_chk}
        mock_file_chk.return_value = None
        mock_site_chk.return_value = None
        mock_html_chk.return_value = None

        # Case 1: No issues are found
        checks = {"html_structure": True,
                  "against_site": url,
                  "against_file": old_file}
        self.test_filecheck.check_map = fake_check_map
        self.test_filecheck.check_type = checks
        self.test_filecheck.run_checks()
        mock_file_chk.assert_called_with(old_file)
        mock_site_chk.assert_called_with(url)
        mock_html_chk.assert_called_with(html_value)

        mock_file_chk.reset_mock()
        mock_site_chk.reset_mock()
        mock_html_chk.reset_mock()

        # Case 2: At least some issue is found
        mock_file_chk.return_value = None
        mock_site_chk.return_value = None
        mock_html_chk.return_value = "Some html issue is returned"

        self.assertRaises(Exception,self.test_filecheck.run_checks)
        mock_file_chk.assert_called_with(old_file)
        mock_site_chk.assert_called_with(url)
        mock_html_chk.assert_called_with(html_value)

    @patch('src.filecheck.FileCheck._get_size')
    def test_check_size(self, get_size_mock):
        tolerance = 0.05
        check_content = "Some str of 100 characters"
        check_against_content = "Some str of 104 characters"
        self.test_filecheck.tolerance = tolerance
        self.test_filecheck.check_file_content = check_content
        self.test_filecheck.check_against_content = check_against_content

        # Case 1: Within tolerance
        get_size_mock.side_effect = [100, 104, 100]
        expected_calls = [call(check_content), call(check_against_content)]
        expected_return = None
        result = self.test_filecheck.check_size()
        get_size_mock.assert_has_calls(expected_calls)
        self.assertEqual(result, expected_return)

        # Case 2: Larger than tolerance
        get_size_mock.side_effect = [100, 106, 100]
        expected_calls = [call(check_content), call(check_against_content)]
        expected_return_2 = 6/100
        result = self.test_filecheck.check_size()
        get_size_mock.assert_has_calls(expected_calls)
        self.assertEqual(result, expected_return_2)

    @patch('src.filecheck.len')
    def test__get_size(self, len_mock):
        content = "abcde"
        s = len(content)
        len_mock.return_value = s
        size = self.test_filecheck._get_size(content)
        len_mock.assert_called_with(content)
        self.assertEqual(size, s)

    @patch('src.validatehtml.ChkHtmlStructure')
    @patch('src.filecheck.FileCheck._load_from_file')
    def test_check_html(self, load_from_f_mock, chkhtml_mock):
        instance_mock = MagicMock()
        chkhtml_mock.return_value = instance_mock
        errors = {'unclosed_opening': ['html'], 'unexpected_closing': ['/body']}
        instance_mock.run_checks.return_value = errors
        content = "some-html-content"
        load_from_f_mock.return_value = content

        html_errors = self.test_filecheck.check_html()
        self.assertEqual(html_errors, errors)
        chkhtml_mock.assert_called_with(full_check=True)
        load_from_f_mock.assert_called_with(self.test_filecheck.checked_file)
        instance_mock.run_checks.assert_called_with(content)

    @patch('src.filecheck.FileCheck._load_contents')
    @patch('src.filecheck.FileCheck.check_size')
    @patch('src.filecheck.FileCheck._format_size_diff_msg')
    def test_check_against_file(self, mock_format_msg, mock_check_size, mock_load_cont):
        # Case 1: Ratio is ok (no return)
        mock_check_size.return_value = None
        old_file_str = "some/file/path.html"

        ratio = self.test_filecheck.check_against_file(old_file_str)
        mock_load_cont.assert_called_with(old_file_str, against_file=True)
        mock_check_size.assert_called_once()
        mock_format_msg.assert_not_called()
        self.assertEqual(ratio, None)

        mock_check_size.reset_mock()

        # Case 2: Ratio is not ok -> return value
        diff = 0.15
        mock_check_size.return_value = diff
        old_file_str = "some/file/path.html"
        return_msg = "Formatted_msg"
        mock_format_msg.return_value = return_msg

        ratio = self.test_filecheck.check_against_file(old_file_str)
        mock_load_cont.assert_called_with(old_file_str, against_file=True)
        mock_check_size.assert_called_once()
        mock_format_msg.assert_called_with(old_file_str, diff)
        self.assertEqual(ratio, return_msg)

    @patch('src.filecheck.FileCheck._load_contents')
    @patch('src.filecheck.FileCheck.check_size')
    @patch('src.filecheck.FileCheck._format_size_diff_msg')
    def test_check_against_site(self, mock_format_msg, mock_check_size, mock_load_cont):
        # Case 1: Ratio is ok (no return)
        mock_check_size.return_value = None
        url = "somewebsite.com/page.html"

        ratio = self.test_filecheck.check_against_site(url)
        mock_load_cont.assert_called_with(url, against_file=False)
        mock_check_size.assert_called_once()
        mock_format_msg.assert_not_called()
        self.assertEqual(ratio, None)

        mock_check_size.reset_mock()

        # Case 2: Ratio is not ok -> return value
        diff = 0.15
        mock_check_size.return_value = diff
        old_file_str = "some/file/path.html"
        return_msg = "Formatted_msg"
        mock_format_msg.return_value = return_msg

        ratio = self.test_filecheck.check_against_site(url)
        mock_load_cont.assert_called_with(url, against_file=False)
        mock_check_size.assert_called_once()
        mock_format_msg.assert_called_with(url, diff)
        self.assertEqual(ratio, return_msg)

    def _format_size_diff_msg(self):
        ratio = 0.1
        check_against = "path/to/old_file.html"
        expected_msg = f"Size difference is {ratio} against {check_against}" \
                       f", which is above threshold {self.test_filecheck.tolerance}."
        actual_msg = self.test_filecheck._format_size_diff_msg(check_against, ratio)
        self.assertEqual(expected_msg, actual_msg)

    @patch('src.filecheck.FileCheck._load_from_file')
    @patch('src.filecheck.FileCheck._load_from_url')
    def test__load_contents(self, load_url_mock, load_file_mock):
        # Case 1: Load file + load file
        load_file_return_values = ["Content_for_first_call", "Content_for_second_call",
                                   "Content_for_third_call"]
        load_url_return_value = "Content_from_url"
        load_file_mock.side_effect = load_file_return_values
        load_url_mock.return_value = load_url_return_value
        path_file = "some/path/file.html"
        path_old_file = "some/path/old_file.html"
        expected_file_calls = [call(path_file), call(path_old_file)]

        self.test_filecheck.checked_file = path_file
        self.test_filecheck._load_contents(path_old_file)
        load_file_mock.assert_has_calls(expected_file_calls)
        load_url_mock.assert_not_called()
        self.assertEqual(self.test_filecheck.check_file_content, load_file_return_values[0])
        self.assertEqual(self.test_filecheck.check_against_content, load_file_return_values[1])

        load_file_mock.reset_mock()

        # Case 2: Load file + load url
        load_file_return_value = ["Content_for_single_call"]
        load_file_mock.side_effect = load_file_return_value
        url = "somewebsite.com"

        self.test_filecheck._load_contents(url, against_file=False)
        load_file_mock.assert_called_once()
        load_file_mock.assert_called_with(path_file)
        load_url_mock.assert_called_once()
        load_url_mock.assert_called_with(url)
        self.assertEqual(self.test_filecheck.check_file_content, load_file_return_value[0])
        self.assertEqual(self.test_filecheck.check_against_content, load_url_return_value)

    @patch('src.filecheck.open')
    @patch('src.filecheck.Path')
    def test__load_from_file(self, path_mock, open_mock):
        file_mock = MagicMock()
        fake_content = "<some html file content>"
        file_mock.read.return_value = fake_content
        open_mock.return_value.__enter__.return_value = file_mock
        file_path = "path/to/some/file"
        path_output = f"Path{file_path}"
        path_mock.return_value = path_output

        output = self.test_filecheck._load_from_file(file_path)
        path_mock.assert_called_with(file_path)
        open_mock.assert_called_with(path_output)
        file_mock.read.assert_called_once()

        self.assertEqual(output, fake_content)

    @patch('src.filecheck.requests')
    def test__load_from_url(self, requests_mock):
        request_get_mock = MagicMock()
        fake_site_content = "<Some content downloaded from web>"
        request_get_mock.content = fake_site_content
        requests_mock.get.return_value = request_get_mock
        check_against_url = "some_web_url"
        self.test_filecheck.check_agaist = check_against_url

        output = self.test_filecheck._load_from_url(check_against_url)
        requests_mock.get.assert_called_with(check_against_url)
        self.assertEqual(output, fake_site_content)


if __name__ == '__main__':
    main()
