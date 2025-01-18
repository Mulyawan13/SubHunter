import subprocess
import httpx
import os
from concurrent.futures import ThreadPoolExecutor

ascii_art = r"""

   _____           _       _    _                   _                 
  / ____|         | |     | |  | |                 | |                
 | (___    _   _  | |__   | |__| |  _   _   _ __   | |_    ___   _ __ 
  \___ \  | | | | | '_ \  |  __  | | | | | | '_ \  | __|  / _ \ | '__|
  ____) | | |_| | | |_) | | |  | | | |_| | | | | | | |_  |  __/ | |   
 |_____/   \__,_| |_.__/  |_|  |_|  \__,_| |_| |_|  \__|  \___| |_|  by mulyawan13
"""

print(ascii_art)

def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.splitlines()
    except Exception as e:
        print(f"Error running command '{command}': {e}")
        return []

def find_subdomains(domain):
    """Use Subfinder and Assetfinder to find subdomains."""
    print(f"[INFO] Finding subdomains for: {domain}")

    subfinder_command = f"subfinder -silent -d {domain}"
    assetfinder_command = f"assetfinder --subs-only {domain}"

    subfinder_results = run_command(subfinder_command)
    assetfinder_results = run_command(assetfinder_command)

    return set(subfinder_results + assetfinder_results)

def check_active_subdomains(subdomains):
    """Check active subdomains using Httpx for both HTTP and HTTPS."""
    active_subdomains = []

    def check_subdomain(subdomain):
        for protocol in ["http", "https"]:
            try:
                url = f"{protocol}://{subdomain}"
                response = httpx.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"[ACTIVE] {url}")
                    active_subdomains.append(url)
                    break  # No need to check both protocols if one is active
            except httpx.RequestError:
                continue

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(check_subdomain, subdomains)

    return active_subdomains

def main():
    domain = input("Enter the domain to scan: ").strip()
    if not domain:
        print("[ERROR] Please provide a valid domain.")
        return

    # Step 1: Find subdomains
    subdomains = find_subdomains(domain)
    print(f"[INFO] Found {len(subdomains)} subdomains.")

    # Step 2: Check active subdomains
    print("[INFO] Checking active subdomains...")
    active_subdomains = check_active_subdomains(subdomains)

    # Step 3: Save results to file
    output_file = f"final_subdomain_live_{domain}.txt"
    with open(output_file, "w") as f:
        for subdomain in active_subdomains:
            f.write(f"{subdomain}\n")

    print(f"[INFO] Active subdomains saved to {output_file}")

if __name__ == "__main__":
    main()
