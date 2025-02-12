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
        tol = 0.97
        test_filecheck = check.FileCheck(file, check_type, old_file, tol)
        self.assertEqual(test_filecheck.checked_file, file)
        self.assertEqual(test_filecheck.check_type, check_type)
        self.assertEqual(test_filecheck.check_agaist, old_file)
        self.assertEqual(test_filecheck.tolerance, tol)

    def test_get_file_size(self):
        pass

    def test_check_html(self):
        pass
        # file = "webpage.html"
        # check_type = "size"
        # old_file = "webpage_old.html"
        # tol = 0.97
        # test_filecheck = check.FileCheck(file, check_type, old_file, tol)
        #
        # # Case 1: valid html
        # valid_html = """<!DOCTYPE html><html><head></head><body></body></html>"""
        # test_filecheck.check_file_content = valid_html
        # expected = "HTML is valid"
        # validate = test_filecheck.check_html()
        # self.assertEqual(validate, expected)
        #
        # # Case2: invalid html
        # invalid_html = """<!DOCTYPE html><html><head></head>"""
        # # invalid_html = """<html><head></head></html>"""
        # test_filecheck.check_file_content = invalid_html
        # expected = True
        # validate = test_filecheck.check_html()
        # print(validate)
        # # self.assertEqual(validate, expected)

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
