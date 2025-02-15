from unittest import TestCase, main
from unittest.mock import MagicMock, patch, call

from src import check


class TestFileCheck(TestCase):

    def setUp(self):
        file = "webpage.html"
        check_type = "size"
        old_file = "webpage_old.html"
        self.test_filecheck = check.FileCheck(file, check_type, old_file)

    def test_init(self):
        file = "webpage.html"
        check_type = "size"
        old_file = "webpage_old.html"
        tol = 0.07
        test_filecheck = check.FileCheck(file, check_type, old_file, tol)
        self.assertEqual(test_filecheck.checked_file, file)
        self.assertEqual(test_filecheck.check_type, check_type)
        self.assertEqual(test_filecheck.check_agaist, old_file)
        self.assertEqual(test_filecheck.tolerance, tol)

    @patch('src.check._get_size')
    def test_check_size(self, get_size_mock):
        tolerance = 0.05
        check_content = "Some str of 100 characters"
        check_against_content = "Some str of 104 characters"
        self.test_filecheck.tolerance = tolerance
        self.test_filecheck.check_file_content = check_content
        self.test_filecheck.check_against_content = check_against_content

        # Case 1: Within tolerance
        get_size_mock.side_effect = [100, 104]
        expected_calls = [call(check_content), call(check_against_content)]
        expected_return = None
        result = self.test_filecheck.check_size()
        get_size_mock.assert_has_calls(expected_calls)
        self.assertEqual(result, expected_return)

        # Case 2: Larger than tolerance
        get_size_mock.side_effect = [100, 106]
        expected_calls = [call(check_content), call(check_against_content)]
        expected_return_2 = 6/100
        result = self.test_filecheck.check_size()
        get_size_mock.assert_has_calls(expected_calls)
        self.assertEqual(result, expected_return_2)

    @patch('src.check.len')
    def test__get_size(self, len_mock):
        content = "abcde"
        s = len(content)
        len_mock.return_value = s
        size = self.test_filecheck._get_size(content)
        len_mock.assert_called_with(content)
        self.assertEqual(size, s)

    @patch('src.validatehtml.ChkHtmlStructure')
    def test_check_html(self, chkhtml_mock):
        instance_mock = MagicMock()
        chkhtml_mock.return_value = instance_mock
        errors = {'unclosed_opening': ['html'], 'unexpected_closing': ['/body']}
        instance_mock.run_check.return_value = errors
        content = "some-html-content"
        self.test_filecheck.check_file_content = content

        html_errors = self.test_filecheck.check_html()
        self.assertEqual(html_errors, errors)
        chkhtml_mock.assert_called_once()
        instance_mock.run_check.assert_called_with(content)

    def test_check_size(self):
        pass

    @patch('src.check.FileCheck._load_from_file')
    @patch('src.check.FileCheck._load_from_url')
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
        self.test_filecheck.check_agaist = path_old_file
        self.test_filecheck._load_contents()
        load_file_mock.assert_has_calls(expected_file_calls)
        load_url_mock.assert_not_called()
        self.assertEqual(self.test_filecheck.check_file_content, load_file_return_values[0])
        self.assertEqual(self.test_filecheck.check_against_content, load_file_return_values[1])

        load_file_mock.reset_mock()

        # Case 2: Load file + load url
        load_file_return_value = ["Content_for_single_call"]
        load_file_mock.side_effect = load_file_return_value
        url = "somewebsite.com"

        self.test_filecheck.check_agaist = url
        self.test_filecheck._load_contents(against_file=False)
        load_file_mock.assert_called_once()
        load_file_mock.assert_called_with(path_file)
        load_url_mock.assert_called_once()
        load_url_mock.assert_called_with(url)
        self.assertEqual(self.test_filecheck.check_file_content, load_file_return_value[0])
        self.assertEqual(self.test_filecheck.check_against_content, load_url_return_value)

    @patch('src.check.open')
    def test__load_from_file(self, open_mock):
        file_mock = MagicMock()
        fake_content = "<some html file content>"
        file_mock.read.return_value = fake_content
        open_mock.return_value.__enter__.return_value = file_mock
        file_path = "path/to/some/file"

        output = self.test_filecheck._load_from_file(file_path)
        open_mock.assert_called_with(file_path, "r")
        file_mock.read.assert_called_once()

        self.assertEqual(output, fake_content)

    @patch('src.check.requests')
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
