"""
Script to call via command line to QC the file (downloaded via fetch.py).
"""
from argparse import ArgumentParser

from src.filecheck import FileCheck


def parse_args():
    parser = ArgumentParser(description="Check downloaded html file for potential corruption.")

    parser.add_argument("--file",
                        help="Path to file that is to be checked.",
                        required=True)
    parser.add_argument("--tol", type=float, default=0.05,
                        help="Acceptable difference between files in float."
                        "e.g., for 15% acceptable differene \n--tol 0.15"
                        "\ndefaults to 5% (not applicable to html_structure check)")
    parser.add_argument("--html_structure", action="store_true",
                        help="Check file for open/closing html tag irregularities.")
    parser.add_argument("--against_file",
                        help="Previously saved file to compare against. "
                        "e.g.\n--against file u1/hist/my_file.html")
    parser.add_argument("--against_site",
                        help="Download content from url to check against."
                        "e.g.\n--against_site somewebsite.com/page-1.html")

    arguments = parser.parse_args()
    checks = {}
    check_options = ["html_structure", "against_file", "against_site"]
    for opt in check_options:
        if vars(arguments)[opt]:
            checks[opt] = vars(arguments)[opt]
    arguments.check_types = checks
    return arguments


if __name__ == "__main__":
    args = parse_args()
    FileCheck(args.file, check_type=args.check_types, tolerance=args.tol).run_checks()
