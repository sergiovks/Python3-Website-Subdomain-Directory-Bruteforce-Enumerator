import argparse
import requests
from termcolor import colored
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

parser = argparse.ArgumentParser(description='Directory/Subdomain enumeration on a website')
parser.add_argument('-w', '--wordlist', metavar='', required=True, help='Path to the wordlist to use')
parser.add_argument('-t', '--threads', metavar='', type=int, default=10, choices=range(1, 1001), help='Number of threads to use (default: 10)')
parser.add_argument('-s', '--subdomains', action='store_true', help='Enable subdomain enumeration mode')
parser.add_argument('-d', '--directories', action='store_true', help='Enable directory enumeration mode (default)')
parser.add_argument('-f', '--add-slash', action='store_true', help='Add a slash at the end of directory paths')
parser.add_argument('url', metavar='', help='URL of the website to enumerate')
args = parser.parse_args()

wordlist = open(args.wordlist, 'r')
url = args.url
num_threads = args.threads

if args.subdomains:
    target = urlparse(url).netloc
    subdomains = [f"{sub}.{target}" for sub in wordlist.read().split()]
    wordlist.close()
    wordlist = subdomains
else:
    wordlist = wordlist.read().split()

def scan_path(path):
    if args.add_slash:
        path = path.strip() + "/"
    else:
        path = path.strip()
    full_url = url + "/" + path
    try:
        response = requests.get(full_url)
        status_code = response.status_code
        if status_code >= 200 and status_code < 300:
            print(colored(full_url + " [{}]".format(status_code), 'green'))
        elif status_code >= 300 and status_code < 400:
            print(colored(full_url + " [{}]".format(status_code), 'blue'))
        elif status_code >= 400 and status_code < 500:
            print(colored(full_url + " [{}]".format(status_code), 'red'))
        elif status_code >= 500:
            print(colored(full_url + " [{}]".format(status_code), 'yellow'))
    except requests.exceptions.RequestException as e:
        print(colored(full_url + " [Error]: {}".format(e), 'magenta'))

with ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = []
    for line in wordlist:
        futures.append(executor.submit(scan_path, line))
    for future in futures:
        future.result()

wordlist.close()
