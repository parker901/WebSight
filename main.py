import os
from time import sleep
import sys
import socket
import hashlib
from datetime import date
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException

PATH = "/Applications/chromedriver" #replace with your chromedriver path
ips_list = "ips_list"

def main():
    hash_file = open(('hash-' + str(date.today()) + '.txt'), "a")
    
    ips_80 = get_port_ips(80)
    ips_443 = get_port_ips(443)

    hash_file.write("------------------- Port 80------------------- \n" )
    for ip_80 in ips_80:
        url = "http://" + ip_80
        hash = gen_hash(ip_80)
        screenshot_path = 'screenshots/port_80/' + str(hash) + ".png"
        take_screenshot(url, screenshot_path)
        if os.path.isfile(screenshot_path):
            hash_file.write(ip_80 + " " + hash + "\n" )

    hash_file.write("------------------- Port 443------------------- \n" )
    for ip_443 in ips_443:
        url = "https://" + ip_443
        hash = gen_hash(ip_443)
        screenshot_path = 'screenshots/port_443/' + str(hash) + ".png"
        take_screenshot(url, screenshot_path)
        if os.path.isfile(screenshot_path):
            hash_file.write(ip_443 + " " + hash + "\n" )

    hash_file.close()

def gen_hash(ip):
    hash = hashlib.md5(ip.encode('utf-8')).hexdigest()
    return hash

def get_port_ips(port):
    new_ips = []
    ips = get_ips()
    for ip in ips:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2) 
            print("Scanning port {0} on {1}.".format(port,ip))
            result = sock.connect_ex((ip, port))
            if result == 0:
                new_ips.append(ip)
            sock.close()
        except Exception as e:
            print("[*] Error - {0}.".format(e))

    return new_ips

def get_ips():
    if not os.path.isfile(ips_list):
        print("[*] Exiting - {0} file doesn't exist.".format(ips_list))
        sys.exit(1)
    file = open(ips_list, 'r')
    ips = file.read().splitlines()
    return ips
    

def take_screenshot(url, screenshot_path):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(PATH, options=options)
    driver.set_page_load_timeout(5)

    try:
        driver.get(url)
        driver.save_screenshot(screenshot_path)
        sleep(2)
        driver.quit()
    except TimeoutException as e:
        print("[*] Timeout - {0}.".format(url))
        driver.quit()
    except WebDriverException as e:
        print("[*] Page not loading {0} - {1}.".format(url, e))
        driver.quit()



if __name__ == "__main__":
    main()