# webfetcher
Cli tool to download website and save html content into file.

Note: for now works only on html sites


How to run:
For fetching website:
Use fetch.py to kick off script. Pass website link with switch --url. Additional functions can be shown with --help switch. If output_file switch is not used, script will create a name automatically.
Sample command:
python3 fetch.py --url https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html --output_dir ~/scripts/download --timestamp


For checking downloaded file:
Use check.py to kick off script. Pass file to be checked with switch --file. Additional functions can be shown with --help switch.
Sample command:
