# 🔐 PIN Bruteforcer

A fast, flexible brute-force utility for numeric PIN-based logins — built for CTFs, ethical hacking, and security research.

This tool dynamically generates numeric (or custom charset) PINs in user-defined length ranges, brute-forces login endpoints, and reports valid credentials.

> ⚠️ **For educational and authorized testing only.** Do not use this tool on systems you do not own or have permission to test.

---

## 🚀 Features

- ✅ Multi-threaded brute forcing
- ✅ Supports configurable digit ranges (`--min-digits`, `--max-digits`)
- ✅ Custom character sets (`--charset`)
- ✅ Delay control between attempts
- ✅ Live status updates with attempt counter
- ✅ Verbose mode for progress tracking
- ✅ Output saved to `hits.txt`

---

## 📦 Requirements

- Python 3.x
- `requests` library (install via `pip install requests`)

---

## 🛠 Usage

```bash
python3 bruteforcer.py --min-digits 4 --max-digits 6 --threads 10 --delay 0.1 --verbose
