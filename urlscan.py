import configparser
import os
import sys
import argparse
from seleniumwire import webdriver
from urllib.parse import urlparse
import tldextract

def get_base_domain(netloc):
  ext = tldextract.extract(netloc)
  return f"{ext.domain}.{ext.suffix}" if ext.domain and ext.suffix else netloc

def scan_website(args):
  target_url = args.url
  output_path = os.path.join(args.config['OUTPUT']['raw_dir'],args.output)
  level = args.level
  # Set browser options (headless optional)
  options = webdriver.ChromeOptions()
  options.add_argument('--ignore-certificate-errors')
  options.add_argument('--headless')  # Optional: run in background

  # Start Selenium Wire WebDriver
  driver = webdriver.Chrome(options=options)

  # Visit the target site
  print(f"Visiting: {target_url}")
  driver.get(target_url)

  # Extract all requested URLs
  urls = set()
  for request in driver.requests:
    if request.response:
      parsed_url = urlparse(request.url)
      # domain = parsed_url.netloc
      domain = ""
      if level == 1:
        parsed_url = urlparse(request.url)
        domain = get_base_domain(parsed_url.netloc)
      elif level == 2:
        parsed_url = urlparse(request.url)
        domain = parsed_url.netloc
      elif level == 3:
        domain = request.url
      
      if domain:
          urls.add(domain)

  if output_path:
    dir_path = args.config['OUTPUT']['raw_dir']

    if not os.path.isdir(dir_path):
      os.makedirs(dir_path)
    # Export to file
    with open(output_path, "w") as f:
      for domain in sorted(urls):
        f.write(domain + "\n")

    print(f"Scanned {len(urls)} unique domains. Saved to {output_path}")
  else:
    # Print the unique domains
    print("Domains contacted by the website:")
    for domain in sorted(urls):
      print(domain)

  # Clean up
  driver.quit()

def aggregate_files(args):
  all_urls = set()
  input_dir = args.config['OUTPUT']['raw_dir']
  output_file = args.config['OUTPUT']['aggr_file']

  for filename in os.listdir(input_dir):
    filepath = os.path.join(input_dir, filename)
    if filename.endswith(".txt") and os.path.isfile(filepath):
      with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
          url = line.strip()
          if url:
            all_urls.add(url)

  with open(output_file, "w", encoding="utf-8") as f:
    for url in sorted(all_urls):
      f.write(url + "\n")

  print(f"Aggregated {len(all_urls)} unique URLs into {output_file}")

def get_config_path(filename):
  if getattr(sys, 'frozen', False):
    # PyInstaller executable
    application_path = os.path.dirname(sys.executable)
  else:
    # regular Python script
    application_path = os.path.dirname(os.path.abspath(__file__))
  
  return os.path.join(application_path, filename)

def load_config(config_file_path):
  config = configparser.ConfigParser()
  files_read = config.read(config_file_path)

  if not files_read:
    print(f"Error: Could not read configuration file at {config_file_path}")
    print("Please ensure 'config.ini' exists in the same directory as the script.")
    exit(1)

  print(f"Successfully read configuration from: {files_read[0]}")

  return config

def generate_config(config_file_path):
  config = configparser.ConfigParser()
  config['OUTPUT'] = {
      'raw_dir': 'collection',
      'aggr_file': 'aggregated.txt'
  }

  with open(config_file_path, 'w') as configfile:
    config.write(configfile)
  print(f"Created a default config.ini at: {config_file_path}")

if __name__ == "__main__":
  # config checking and generation
  config_file_path = get_config_path('config.ini')
  if not os.path.exists(config_file_path):
    generate_config(config_file_path)

  try:
    config = load_config(config_file_path)
  except Exception as e:
    print(f"Failed to read config.ini at {config_file_path}: {e}")

  parser = argparse.ArgumentParser(description="Tool to scan domains or URLs loaded by a website")
  subparsers = parser.add_subparsers(dest='command', help='Available commands')

  scan = subparsers.add_parser('scan', help='scan domains or URLs loaded by a website')
  scan.add_argument('--url', required=True, help="Target website URL (e.g., https://example.com)")
  scan.add_argument('--output', '-o', default="output.txt", help="Output file path (e.g., example.txt)")
  scan.add_argument('--level', '-l', type=int, default=1, help="Number 1-3; 1 = base domain; 2 = sub domains; 3 = full url")
  scan.set_defaults(func=scan_website)

  aggr = subparsers.add_parser('aggregate', help='Aggregate all text files into a single file')
  aggr.set_defaults(func=aggregate_files)

  args = parser.parse_args()
  setattr(args, 'config', config)

  if hasattr(args, 'func'):
    args.func(args)
  else:
    parser.print_help()