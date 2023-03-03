import argparse
import requests
from termcolor import colored
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, urljoin
from tqdm import tqdm
import sys

def banners():
    print("""
    ************************************************
        Web: Directory Subdomain Bruteforce Tool
        Author: sergiovks
    ************************************************
    """)
banners

parser = argparse.ArgumentParser(description='Directory/Subdomain enumeration on a website')
parser.add_argument('-w', '--wordlist', metavar='', required=True, help='Path to the wordlist to use')
parser.add_argument('-t', '--threads', metavar='', type=int, default=10, choices=range(1, 1001), help='Number of threads to use (default: 10)')
parser.add_argument('-s', '--subdomains', action='store_true', help='Enable subdomain enumeration mode')
parser.add_argument('-d', '--directories', action='store_true', help='Enable directory enumeration mode (default)')
parser.add_argument('-f', '--add-slash', action='store_true', help='Add a slash at the end of directory paths')
parser.add_argument('-u', '--url', metavar='', required=True, help='URL of the website to scan')
parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit')
args = parser.parse_args()

def display_help():
    print("Usage: python3 dirsub.py [OPTIONS]\n")
    print("Options:")
    print("  -w, --wordlist <PATH>  Path to the wordlist to use")
    print("  -t, --threads <INT>    Number of threads to use (default: 10)")
    print("  -s, --subdomains       Enable subdomain enumeration mode")
    print("  -d, --directories      Enable directory enumeration mode (default)")
    print("  -f, --add-slash        Add a slash at the end of directory paths")
    print("  -u, --url <URL>        URL of the website to scan")
    print("  -h, --help             Show this help message and exit")
    sys.exit()

def validate_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def read_wordlist(file_path):
    try:
        with open(file_path, 'r') as wordlist_file:
            return wordlist_file.read().split()
    except IOError:
        print(colored(f"Error: Failed to read wordlist file: {file_path}", 'magenta'))
        sys.exit()

if not args.wordlist or not args.url:
    display_help()

if not validate_url(args.url):
    print(colored(f"Error: Invalid URL: {args.url}", 'magenta'))
    sys.exit()

wordlist = read_wordlist(args.wordlist)
num_threads = args.threads

if not wordlist:
    print(colored("Error: The wordlist file is empty!", 'magenta'))
    sys.exit()

if args.subdomains:
    scan_subdomains(args.url)
    sys.exit()

def scan_subdomains(url):
    target = urlparse(url).netloc
    for subdomain in wordlist:
        subdomain_url = f"{subdomain}.{target}"
        try:
            response = requests.get(f"http://{subdomain_url}", timeout=5)
            if response.status_code < 400:
                print(colored(f"[*] Discovered subdomain: {subdomain_url}", "green"))
                scan_subdomains(subdomain_url)
        except:
            pass
    
def scan_paths(url):
    for line in wordlist:
        if args.add_slash:
            path = line.strip() + "/"
        else:
            path = line.strip()
        full_url = urljoin(url, path)
        try:
            response = requests.get(full_url, timeout=5)
            status_code = response.status_code
            if status_code >= 200 and status_code < 300:
                print(colored(full_url + " [{}]".format(status_code), 'green'))
            elif status_code >= 300 and status_code < 400:
                print(colored(full_url + " [{}]".format(status_code), 'blue'))
            elif status_code >= 400 and status_code < 500:
                print(colored(full_url + " [{}]".format(status_code), 'red'))
            elif status_code >= 500:
                print(colored(full_url + " [{}]".format(status_code), 'yellow'))
        except requests.exceptions.Timeout:
            print(colored(full_url + " [Error]: Connection timeout", 'magenta'))
        except requests.exceptions.RequestException as e:
            print(colored(full_url + " [Error]: {}".format(e), 'magenta'))
        pbar.update(1)

with ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = []
    if args.subdomains:
        pbar = tqdm(total=len(wordlist), desc='Subdomain Scan')
    else:
        pbar = tqdm(total=len(wordlist), desc='Directory Scan')
    for line in wordlist:
        futures.append(executor.submit(scan_path, line))
    for future in futures:
        future.result()
    pbar.close()

file.close()
