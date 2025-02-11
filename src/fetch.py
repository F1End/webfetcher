"""
Download website content from url and save to file
"""
import datetime
import requests
from pathlib import Path
from typing import Union


class FetchSite:
    def __init__(self, url: str) -> None:
        self.url = url
        self.content = None
        self.content_time = None

    def download_content(self):
        self._timestamp_content()
        response = requests.get(self.url)
        self.content = response.content
        return self

    def to_file(self, add_timestamp: bool = True, file_name: str = None, output_dir: str = None) -> None:
        output_full_path = self._format_full_path(add_timestamp=add_timestamp,
                                                  file_name=file_name,
                                                  output_dir=output_dir)

        with open(output_full_path, "wb") as file:
            file.write(self.content)

    def _format_filename(self, add_timestamp: bool = True, file_name: Union[str, None] = None) -> str:
        if file_name:
            output_name = Path(file_name)
        else:
            output_name = self.url.rsplit('/', 1)[-1]

        if add_timestamp:
            output_name = self.content_time.strftime("%Y-%m-%d-%H-%M-%S") + "_" + str(output_name)
        return output_name

    def _format_full_path(self, add_timestamp: bool = True, file_name: Union[str, None] = None,
                          output_dir: Union[str, None] = None) -> Path:
        output_name = self._format_filename(add_timestamp=add_timestamp, file_name=file_name)
        if output_dir:
            output_path = Path(output_dir)
            output_name = output_path.joinpath(output_name)
        return output_name

    def _timestamp_content(self) -> None:
        time = datetime.datetime.now()
        self.content_time = time
