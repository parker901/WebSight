# WebSight
An updated version of the webpage-screenshot script. This version has been updated to use selenium v4 and supports more port numbers. The purpose of this tool is to determine if any of the provided public IP addresses have sensitive information that is publicly available.

To use WebSight, you need to provide a list of IP addresses and specify the port to use. WebSight will then take a screenshot of the website at each IP address and output a table with the IP address, port, and screenshot path.

## Usage

To use WebSight, run the script with the following arguments:

	python websight.py -i <ips_list_file> -s <screenshots_dir> -t <timeout> -p <port> -n <threads> --verbose

* ips_list_file: A file containing a list of IP addresses to scan, one per line.
* screenshots_dir: The directory to save the screenshots.
* timeout: The maximum time (in seconds) to wait for the page to load.
* port: The port to scan (either 80 for HTTP or 443 for HTTPS).
* threads: The number of threads to use.