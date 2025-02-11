
from unittest import TestCase, main
from unittest.mock import MagicMock, patch


from src import fetch


class TestFetchSite(TestCase):
    def test_init(self):
        url = "https://somewebsite.com"
        default_content = None
        default_content_time = None
        test_fetch = fetch.FetchSite(url)

        self.assertEqual(test_fetch.url, url)
        self.assertEqual(test_fetch.content, default_content)
        self.assertEqual(test_fetch.content_time, default_content_time)

    @patch("src.fetch.FetchSite._timestamp_content")
    @patch("src.fetch.requests")
    def test_download_content(self, requests_mock, timestamp_mock):
        response_mock = MagicMock()
        fake_content = "<fake site content>"
        response_mock.content = fake_content
        requests_mock.get.return_value = response_mock
        url = "https://somewebsite.com"

        test_fetch = fetch.FetchSite(url)
        test_fetch_chain = test_fetch.download_content()  # testing return_self

        timestamp_mock.assert_called_once()
        requests_mock.get.assert_called_with(url)
        self.assertEqual(test_fetch.content, fake_content)
        self.assertEqual(test_fetch, test_fetch_chain)  # testing return_self

    @patch("src.fetch.open")
    @patch("src.fetch.FetchSite._format_full_path")
    def test_to_file(self, format_path_mock, open_mock):
        file_mock = MagicMock()
        open_mock.return_value.__enter__.return_value = file_mock

        mocked_filepath = "some/file/path.txt"
        format_path_mock.return_value = mocked_filepath

        content_mock = "Website_content"

        url = "https://somewebsite.com/somepage.html"
        fetch_test = fetch.FetchSite(url)
        fetch_test.content = content_mock

        # Case 1 (default): timestamp -> T, file_name and output dir -> None
        fetch_test.to_file()
        format_path_mock.assert_called_with(add_timestamp=True,
                                            file_name=None,
                                            output_dir=None)
        open_mock.assert_called_with(mocked_filepath, "wb")
        file_mock.write.assert_called_with(content_mock)


    @patch("src.fetch.Path")
    def test__format_filename(self, path_mock):
        # Setup
        filename = "somefile.txt"
        path_mock.return_value = filename

        url_mock = MagicMock()
        fake_url_split = ["https:", "", "somewebsite.com", "somepage.html"]
        url_mock.rsplit.return_value = fake_url_split

        content_time_mock = MagicMock()
        fake_time_str = "2025-02-11-21-05-30"
        content_time_mock.strftime.return_value = fake_time_str
        expected_format_call = "%Y-%m-%d-%H-%M-%S"

        fetch_test = fetch.FetchSite(url_mock)
        fetch_test.content_time = content_time_mock

        # Case 1 (default): timestamp -> T, file_name -> None
        expected_output = fake_time_str + "_" + fake_url_split[-1]
        result_1 = fetch_test._format_filename()
        path_mock.assert_not_called()
        url_mock.rsplit.assert_called_with('/', 1)
        content_time_mock.strftime.assert_called_with(expected_format_call)
        self.assertEqual(result_1, expected_output)

        url_mock.reset_mock()
        content_time_mock.reset_mock()
        path_mock.reset_mock()

        # Case 2 : timestamp -> T, file_name -> somefile.txt
        expected_output = fake_time_str + "_" + filename
        result_2 = fetch_test._format_filename(file_name=filename)
        path_mock.assert_called_with(filename)
        url_mock.rsplit.assert_not_called()
        content_time_mock.strftime.assert_called_with(expected_format_call)
        self.assertEqual(result_2, expected_output)

        url_mock.reset_mock()
        content_time_mock.reset_mock()
        path_mock.reset_mock()

        # Case 3 : timestamp -> F, file_name -> somefile.txt
        expected_output = filename
        result_2 = fetch_test._format_filename(add_timestamp=False, file_name=filename)
        path_mock.assert_called_with(filename)
        url_mock.rsplit.assert_not_called()
        content_time_mock.strftime.assert_not_called()
        self.assertEqual(result_2, expected_output)

        url_mock.reset_mock()
        content_time_mock.reset_mock()
        path_mock.reset_mock()

        # Case 4 : timestamp -> F, file_name -> None
        expected_output = fake_url_split[-1]
        result_2 = fetch_test._format_filename(add_timestamp=False)
        path_mock.assert_not_called()
        url_mock.rsplit.assert_called_with('/', 1)
        content_time_mock.strftime.assert_not_called()
        self.assertEqual(result_2, expected_output)

        url_mock.reset_mock()
        content_time_mock.reset_mock()
        path_mock.reset_mock()

    @patch("src.fetch.Path")
    @patch("src.fetch.FetchSite._format_filename")
    def test__format_full_path(self, format_fn_mock, path_mock):
        # Setup
        url = "https://somewebsite.com"
        test_fetch = fetch.FetchSite(url)
        mock_output_filename = "somefile.txt"
        format_fn_mock.return_value = mock_output_filename

        path_instance_mock = MagicMock()
        path_mock.return_value = path_instance_mock
        expected_output_with_dir = "/some/dir/path.txt"
        path_instance_mock.joinpath.return_value = expected_output_with_dir

        # Case 1: Output dir exists
        filename = "some_filename"
        output_dir = "/some/dir"
        result_1 = test_fetch._format_full_path(file_name=filename, output_dir=output_dir)
        format_fn_mock.assert_called_with(add_timestamp=True, file_name=filename)
        path_mock.assert_called_with(output_dir)
        path_instance_mock.joinpath.assert_called_with(mock_output_filename)
        self.assertEqual(result_1, expected_output_with_dir)

        format_fn_mock.reset_mock()
        path_mock.reset_mock()
        path_instance_mock.reset_mock()

        # Case 2: No output dir specified
        filename = "some_filename"
        output_dir = "/some/dir"
        result_1 = test_fetch._format_full_path(file_name=filename)
        format_fn_mock.assert_called_with(add_timestamp=True, file_name=filename)
        path_mock.assert_not_called()
        path_instance_mock.joinpath.assert_not_called()
        self.assertEqual(result_1, mock_output_filename)

        format_fn_mock.reset_mock()
        path_mock.reset_mock()
        path_instance_mock.reset_mock()

    @patch("src.fetch.datetime.datetime")
    def test__timestamp_content(self, datetime_mock):
        timestamp = "Some timestamp"
        datetime_mock.now.return_value = timestamp
        url = "https://somewebsite.com"

        test_fetch = fetch.FetchSite(url)
        test_fetch._timestamp_content()

        datetime_mock.now.assert_called_once()
        self.assertEqual(test_fetch.content_time, timestamp)


if __name__ == '__main__':
    main()
