# Take screenshots 
The script takes screenshots of IP addresses that either have port 80 or port 443 opened. The screenshots are saved to folder port_80 or port_443. The name of each screenshot is the md5 hash of its IP address. 

## Usage:
* For selenium to be able to run, both Chrome browser and Chrome driver are required installed on your computer
Download Chrome WebDriver
https://chromedriver.chromium.org/downloads

* Replace the path on line 10 with your Chrome WebDriver's path.

* Replace the IP addresses in the file ips_list with the file IP addresses you wish to scan. Note: Each IP address should be on a new line. 




