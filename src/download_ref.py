#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
from urllib.request import urlretrieve
from urllib.parse import urljoin
from html.parser import HTMLParser
import shutil


SENATE_PAGE = "https://facultysenate.tamu.edu"
MSR_PAGE = urljoin(
    SENATE_PAGE, "important-faculty-updates/minumum-syllabus-requirements"
)


class MSRParser(HTMLParser):
    links = []

    def handle_starttag(self, tag, attrs):
        """Store .docx links from hrefs in an HTML document.

        Parameters
        ----------
        tag : str
            An HTML string
        attrs : list
            Tag attributes
        """
        if tag != "a":
            return

        for attr, val in attrs:
            if attr == "href" and val.endswith("docx"):
                link = Path(val)
                self.links.append(link)

    def _prompt_user(self):
        """Prompt a user to download a .docx file.

        Returns
        -------
        int
            The index position of the file to download
        """
        output = [
            f"[{i + 1}] {link.name}" for i, link in enumerate(self.links)
        ]
        output = "\n".join(output)

        while True:
            err = f"Invalid input. Must be a number: 1-{len(self.links)}\n"
            select = input(
                f"Select one of the following to download:\n{output}\nDownload: "
            )
            try:
                select = int(select)
            except ValueError:
                print(err)
                continue
            if 0 <= (select - 1) <= len(self.links):
                break
            else:
                print(err)

        return select - 1

    def download(self, filename=None):
        """Download a .docx file.

        Parameters
        ----------
        filename : Path
            Name of the output file
        """
        select = self._prompt_user()
        to_download = urljoin(SENATE_PAGE, str(self.links[select]))
        path, headers = urlretrieve(to_download)
        filename = self.links[select].name if not filename else filename
        shutil.move(path, filename)


def main(args):
    """Run the script."""
    path, headers = urlretrieve(MSR_PAGE)
    with open(path, "r") as fin:
        html = fin.read()

    parser = MSRParser()
    parser.feed(html)
    parser.download(args.filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download a .docx reference file"
    )
    parser.add_argument(
        "-f", "--filename", type=Path, default=None, help="Name of the file"
    )
    args = parser.parse_args()
    main(args)
