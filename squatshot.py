import os
import re
import sys
import time
from urllib.parse import urlparse

import requests
from rich.console import Console
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Specify the filepath for the list of potentially typosquatted domains (example.com)
file_path = r"dir"
# Specify the filepath for screenshot outputs
screenshot_directory = r"dir"
# Specify the filepath for your chrome driver installation
chromedriver_path = r"dir"

os.makedirs(screenshot_directory, exist_ok=True)

console = Console()

options = Options()
options.add_argument("--headless")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--log-level=3")

with webdriver.Chrome(service=Service(executable_path=chromedriver_path), options=options) as driver:
    with open(file_path, "r") as file:
        websites = [line.strip() for line in file.readlines()]

    console.print("[bold green]Typosquats to visit:[/bold green]")
    for website in websites:
        console.print(f"- {website}")

    success_count = 0

    for index in range(len(websites)):
        website = websites[index]

        if not re.match(r"^https?://", website, re.IGNORECASE):
            website = f"http://{website}"

        console.print(f"\n[bold cyan]Inspecting Typosquat...[/bold cyan] {website}")

        try:
            try:
                response = requests.head(website, allow_redirects=True)
                response_code = response.status_code if response else None
            except requests.exceptions.RequestException:
                response_code = None

            if response_code is not None:
                if 200 <= response_code < 300:
                    console.print(f"[bold green]Response: {response_code}[/bold green]")

                    driver.set_page_load_timeout(10)
                    driver.get(website)

                    time.sleep(3)
                    console.print("[bold yellow]Capturing screenshot...[/bold yellow]")

                    parsed_url = urlparse(website)
                    filename = re.sub(r"[^\w\-_.]", "_", parsed_url.netloc + parsed_url.path)

                    screenshot_path = os.path.join(screenshot_directory, f"{filename}.png")
                    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)

                    driver.save_screenshot(screenshot_path)
                    console.print(f"[bold green]Screenshot captured and saved:[/bold green] {screenshot_path}")
                    success_count += 1
                else:
                    console.print(f"[bold red]Response: {response_code}[/bold red]")
            else:
                console.print(f"[bold red]Response: {response_code}[/bold red]")
        except TimeoutException:
            pass
        except WebDriverException:
            console.print(f"[bold red]Error: Unable to resolve domain name for {website}. Skipping...[/bold red]")

    console.print(f"\n[bold green]Complete![/bold green]")
    console.print(f"[bold green]Typosquats captured: {success_count}[/bold green]")
