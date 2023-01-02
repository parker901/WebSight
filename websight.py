import os
import sys
import socket
import argparse
import threading
import queue
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tabulate import tabulate


def main():
    # Parse command-line arguments
    args = parse_args()
    ips_list_file = args.ips_list_file
    screenshots_dir = args.screenshots_dir
    timeout = args.timeout
    ports = args.ports
    threads = args.threads

    # Print the ASCII art banner
    print_banner()

    # Get a list of IP addresses that have the specified ports open
    ips = get_ips_with_open_port(ports, ips_list_file)

    ips = list(set(ips))  # Remove duplicates

    # Take screenshots of the websites at the IP addresses
    take_screenshots(ips, screenshots_dir, timeout, ports, threads)

    # Print the results of the screenshotting
    print_results(screenshots_dir, ports)

def print_banner():
    """Print the ASCII art banner."""
    print('''
#  ___       __    ______ ____________        ______ _____ 
#  __ |     / /_______  /___  ___/__(_)______ ___  /___  /_
#  __ | /| / /_  _ \\_  __ \\____ \\__  /__  __ `/_  __ \\  __/
#  __ |/ |/ / /  __/  /_/ /___/ /_  / _  /_/ /_  / / / /_  
#  ____/|__/  \\___//_.___//____/ /_/  _\\__, / /_/ /_/\\__/  
#                                     /____/               
-----------------------------------------------------------------------------------
''')


def get_ips_with_open_port(ports, ip_list_file):
    open_ips = []
    ip_list = get_ip_list(ip_list_file)  # Get the list of IP addresses from the file
    for ip in ip_list:
        for port in ports:
            if port_is_open(ip, port):
                open_ips.append(ip)

    return list(set(open_ips))  # Remove duplicates


def get_ip_list(ip_list_file):
    with open(ip_list_file, 'r') as f:
        ip_list = f.readlines()
    return [ip.strip() for ip in ip_list]

def port_is_open(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            print("[+] Scanning port {0} on {1}.".format(port, ip))
            result = sock.connect_ex((ip, port))
            if result == 0:
                return True
            else:
                return False
    except TimeoutError:
        print("[*] Timeout connecting to {0}:{1}".format(ip, port))
    except ConnectionError:
        print("[*] Connection error connecting to {0}:{1}".format(ip, port))
    except Exception as e:
        print("[*] Error connecting to {0}:{1} - {2}".format(ip, port, e))
        return False

def take_screenshots(ips, screenshots_dir, timeout, ports, threads):
    # Create a queue to store the IP addresses and ports
    ip_queue = queue.Queue()
    for ip in ips:
        for port in ports:
            ip_queue.put((ip, port))

    # Create a list to store the threads
    thread_list = []

    # Create and start the threads
    for i in range(threads):
        t = threading.Thread(target=screenshot_thread, args=(ip_queue, screenshots_dir, timeout, ports))
        t.start()
        thread_list.append(t)

    # Wait for all threads to complete
    for t in thread_list:
        t.join()


def screenshot_thread(ip_queue, screenshots_dir, timeout, ports):
    while not ip_queue.empty():
        ip, port = ip_queue.get()

        if port == 80:
            url = 'http://' + ip
        elif port == 443:
            url = 'https://' + ip
        else:
            # Use http for any other port
            url = 'http://' + ip + ':' + str(port)
        filename = screenshots_dir + '/websight_' + ip + '.' + str(port) + '.png'

        try:
            driver = get_driver(timeout)
            driver.get(url)
            # Wait for the page to load
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            driver.save_screenshot(filename)
            print('[+] Screenshot saved: {0}'.format(filename))
        except TimeoutException:
            # Handle the timeout error
            print('[-] Timed out: {0}'.format(url))
        except Exception as e:
            # Handle any other error
            print('[-] Error: {0} - {1}'.format(url, e.__class__.__name__))
        finally:
            driver.quit()





def get_driver(timeout):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    service = Service(ChromeDriverManager().install())
    service.start()
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(timeout)
    return driver

def print_results(screenshots_dir, ports):
    # Get a list of the screenshots taken
    screenshots = []

    for filename in os.listdir(screenshots_dir):
        # Only include files that start with "websight"
        if filename.startswith('websight'):
            # Extract the IP address and port from the filename using a regular expression
            ip_port_match = re.search(r'websight_(\d+\.\d+\.\d+\.\d+)\.(\d+)', filename)
            ip = ip_port_match.group(1)
            port = ip_port_match.group(2)
            path = screenshots_dir + '/' + filename
            screenshots.append((ip, port, path))

    # Print the results in a table
    print(tabulate(screenshots, headers=['IP Address', 'Open Port', 'Screenshot Path'], tablefmt="grid"))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ips_list_file', required=True, help='List of IP addresses to scan')
    parser.add_argument('-s', '--screenshots_dir', required=True, help='Directory to save screenshots')
    parser.add_argument('-t', '--timeout', type=int, default=10, help='Maximum time (in seconds) to wait for the page to load')
    parser.add_argument('-p', '--ports', type=int, nargs='+', default=[80], help='List of ports to scan (default: 80)')
    parser.add_argument('-n', '--threads', type=int, default=5, help='Number of threads to use (default: 5)')
    return parser.parse_args()

if __name__ == "__main__":
    main()

