import requests
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
import time
from collections import deque
from datetime import datetime
import urllib3

# Suppress SSL warnings for cleaner terminal output
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ANSI Color Codes
RED = "\033[91m"
RESET = "\033[0m"

def banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    # Print the banner logo in Red
    print(RED + """
    ██╗███╗   ██╗███████╗██╗███╗   ██╗██╗████████╗██╗   ██╗
    ██║████╗  ██║██╔════╝██║████╗  ██║██║╚══██╔══╝╚██╗ ██╔╝
    ██║██╔██╗ ██║█████╗  ██║██╔██╗ ██║██║   ██║    ╚████╔╝ 
    ██║██║╚██╗██║██╔══╝  ██║██║╚██╗██║██║   ██║     ╚██╔╝  
    ██║██║ ╚████║██║     ██║██║ ╚████║██║   ██║      ██║   
    ╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝      ╚═╝   
    >> Recursive Deep-Scan Suite | Version 1.0
    >> Author: Abhilash
    """ + RESET) # Reset immediately after the banner
    print("[*] Initializing Infinity Engine... Please wait.")
    print("[*] Press Ctrl+C at any time to gracefully save progress and exit.")

class Infinity:
    def __init__(self, target_url):
        self.target_url = target_url.strip("/")
        self.domain = self.target_url.replace("http://", "").replace("https://", "").replace(":", "_").split('/')[0]
        
        self.wordlist = [] 
        self.results_file = f"infinity_{self.domain}_deep_scan.txt"
        self.found_dirs = set()
        self.auto_extensions = [".php", ".html", ".js", ".txt", ".bak", ".zip", ".conf", ".log", ".old"]
        self.max_w = 5 

    def log(self, data):
        """Appends only the clean, unformatted URL target to the file."""
        with open(self.results_file, "a", encoding="utf-8", errors="ignore") as f:
            f.write(f"{data}\n")

    def parse_text_into_words(self, text, discovered_set):
        """Helper to safely filter and extract clean keywords matching character rules."""
        pattern = r'\b[a-zA-Z0-9.\-_]{1,%d}\b' % self.max_w
        found_words = re.findall(pattern, text.lower())
        for word in found_words:
            word = word.strip()
            word = word.replace("/", "").replace("\\", "")
            if word and not any(c in word for c in "()# "):
                discovered_set.add(word)

    def harvest_site_lexicon(self, max_depth=5):
        """Phase 1: Extracts paths from robots.txt and crawls initial HTML to build baseline custom scope."""
        print(f"\n[*] [PHASE 1] Launching Auto-Generating LexiconEngine...")
        headers = {'User-Agent': 'Mozilla/5.0 Infinity/5.0'}
        discovered_words = set()

        # Step A: Parse robots.txt
        robots_url = f"{self.target_url}/robots.txt"
        try:
            robots_res = requests.get(robots_url, headers=headers, timeout=5, verify=False)
            if robots_res.status_code == 200 and robots_res.text.strip():
                for line in robots_res.text.splitlines():
                    line = line.strip()
                    if line.lower().startswith("allow:") or line.lower().startswith("disallow:"):
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            path_value = parts[1].strip()
                            path_value = path_value.replace("*", "").replace("$", "")
                            
                            tokens = re.split(r'[/\\]', path_value)
                            for t in tokens:
                                t = t.strip()
                                if t and len(t) <= self.max_w:
                                    if not any(c in t for c in "()# "):
                                        discovered_words.add(t)
        except Exception:
            pass

        # Step B: Spider HTML tree
        visited = set()
        queue = deque([(self.target_url, 0)])

        while queue:
            url, depth = queue.popleft()
            if depth > max_depth or url in visited: continue
            visited.add(url)
            try:
                res = requests.get(url, headers=headers, timeout=5, verify=False)
                if res.status_code != 200: continue
                soup = BeautifulSoup(res.text, 'html.parser')
                for junk in soup(["script", "style"]): junk.extract()
                
                self.parse_text_into_words(soup.get_text(), discovered_words)

                if depth < max_depth:
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href.startswith('/') or self.target_url in href:
                            full_link = requests.compat.urljoin(self.target_url, href)
                            if full_link not in visited:
                                queue.append((full_link, depth + 1))
            except Exception: 
                continue

        self.wordlist = sorted(list(discovered_words))
        print(f"[+] Custom Wordlist Generation Ready! Total found keys: {len(self.wordlist)}")

    def load_dictionary_file(self, file_path):
        """Phase 2: Ingests external dictionary file selections securely."""
        print(f"\n[*] [PHASE 2] Ingesting selected file reference: {file_path}")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                static_words = []
                for line in f:
                    cleaned = line.strip()
                    if cleaned.startswith("/"):
                        cleaned = cleaned[1:]
                    if cleaned and not cleaned.startswith("#"):
                        static_words.append(cleaned)
            
            self.wordlist = list(set(self.wordlist + static_words))
            print(f"[+] Successfully merged entries from {file_path}.")
            print(f"[+] Total active combined scanning workspace: {len(self.wordlist)} paths.")
        else:
            print(f"[!] Error: Target wordlist path file '{file_path}' could not be resolved.")

    def live_crawl_discovered_branch(self, branch_url):
        """Crawls a newly discovered subdirectory dynamically to extract unique target parameters on-the-fly."""
        headers = {'User-Agent': 'Mozilla/5.0 Infinity/5.0'}
        new_keywords = set()
        try:
            res = requests.get(branch_url, headers=headers, timeout=4, verify=False)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                for junk in soup(["script", "style"]): junk.extract()
                
                self.parse_text_into_words(soup.get_text(), new_keywords)
                
                added_count = 0
                for word in new_keywords:
                    if word not in self.wordlist:
                        self.wordlist.append(word)
                        added_count += 1
                if added_count > 0:
                    tqdm.write(f"  [!] Live Harvester added {added_count} new keywords extracted from: {branch_url}")
        except Exception:
            pass

    def scan_dirs_recursive(self, max_depth=3):
        """Phase 3: Execution of the optimized subdirectory brute-force strategy with live branching feedback."""
        queue = deque([(self.target_url, 0)])
        self.found_dirs.add(self.target_url)

        print("-" * 30)
        print(f"START_TIME: {datetime.now().strftime('%c')}")
        print(f"URL_BASE: {self.target_url}/")
        print("-" * 30)

        try:
            while queue:
                base_url, depth = queue.popleft()
                if depth >= max_depth: continue

                print(f"\n---- Scanning URL: {base_url}/ (Depth: {depth}) ----")
                current_scan_list = list(self.wordlist)
                
                for word in tqdm(current_scan_list, desc=f"Level {depth}", leave=False):
                    full_url = f"{base_url}/{word}"
                    if full_url in self.found_dirs: continue

                    try:
                        res = requests.get(full_url, timeout=3, verify=False, allow_redirects=False)
                        
                        if res.status_code in [200, 204, 301, 302, 307, 308, 403]:
                            prefix = "==> DIRECTORY:" if res.status_code in [301, 302] else "+"
                            
                            # Print ONLY the discovered subdirectory URL link in RED
                            tqdm.write(f"{prefix} {RED}{full_url}/{RESET} (CODE:{res.status_code}|SIZE:{len(res.content)})")
                            
                            self.log(f"{full_url}/")
                            self.found_dirs.add(full_url)
                            
                            if word not in self.wordlist:
                                self.wordlist.append(word)
                            
                            has_extension = any(word.endswith(ext) for ext in self.auto_extensions)
                            
                            if res.status_code < 400 and word not in ["index.html", "index.php"] and not has_extension:
                                queue.append((full_url, depth + 1))
                                self.live_crawl_discovered_branch(full_url)
                            
                            for ext in self.auto_extensions:
                                f_url = f"{full_url}{ext}"
                                try:
                                    f_res = requests.head(f_url, timeout=2, verify=False)
                                    if f_res.status_code == 200:
                                        # Print ONLY the discovered file extension URL link in RED
                                        tqdm.write(f"  + {RED}{f_url}{RESET} (CODE:200|SIZE:{f_res.headers.get('Content-Length', '0')})")
                                        self.log(f_url)
                                except Exception:
                                    continue
                                    
                    except Exception: 
                        continue
        except KeyboardInterrupt:
            print(f"\n\n[!] User Interrupted Scan. Session entries saved cleanly at: {self.results_file}")

def main():
    # 1. Shows banner immediately
    banner()
    
    # 2. Displays a countdown routine during the 5-second wait
    print("\n")
    for i in range(5, 0, -1):
        print(f"\r[*] Loading input interface modules... Prompting in {i} seconds...", end="", flush=True)
        time.sleep(1)
    print("\r[*] Input modules loaded successfully.                                     ", flush=True)
    
    # 3. Prompt for target input
    target = input("\nEnter Target URL: ")
    if not target.startswith("http"):
        target = "http://" + target

    tool = Infinity(target)
    
    print("\n[?] Target Lexicon Engine Configuration")
    w_max = input("MAXIMUM path character width ceiling? (default 5): ")
    tool.max_w = int(w_max) if w_max.isdigit() else 5
    
    tool.harvest_site_lexicon(max_depth=5)
    
    print("\n[?] Secondary Dictionary File Selection")
    print(" [1] Use default list (common.txt)")
    print(" [2] Manually input custom wordlist path")
    choice = input("Select an option (1 or 2): ").strip()
    
    if choice == "2":
        custom_path = input("Enter the absolute or relative path to your wordlist file: ").strip()
        tool.load_dictionary_file(custom_path)
    else:
        tool.load_dictionary_file("common.txt")

    if not tool.wordlist:
        print("[!] Execution stopped: Active memory workspace contains 0 elements.")
        return

    if input("\n[?] Launch Live-Loop Adaptive Recursive Scan? (y/n): ").lower() == 'y':
        d_limit = input("[?] Set Max Depth (default 3): ")
        depth = int(d_limit) if d_limit.isdigit() else 3
        tool.scan_dirs_recursive(max_depth=depth)

    print(f"\n" + "-"*30)
    print(f"END_TIME: {datetime.now().strftime('%c')}")
    print(f"[***] Operation Completed. Clean log stored inside: {tool.results_file}")

if __name__ == "__main__":
    main()