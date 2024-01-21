from pathlib import Path

import polars as pl
import requests
from polars import DataFrame
from robocorp import browser, log
from robocorp.tasks import get_output_dir, task

OUTPUT_DIR = get_output_dir() or Path("output")
TARGET_FILENAME = "customers.csv"
CSV_PATH = OUTPUT_DIR
URL = "https://developer.automationanywhere.com/challenges/automationanywherelabs-customeronboarding.html"


@task
def solve_challenge():
    """Complete Customer onboarding challenge"""
    launch_browser_and_open_challenge()
    # get customer data as dataframe
    df_customers = get_customers_data()
    # insert data to form
    complete_challenge(df_customers)
    # log screenshot and challlenge id
    challenge_verification()


def launch_browser_and_open_challenge():
    browser.configure(
        browser_engine="chromium",
        screenshot="only-on-failure",
        headless=False,
    )
    # user_agent is needed for headless runs
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    context = browser.context()
    context.set_extra_http_headers({"User-Agent": user_agent})
    # navigate to challenge page
    browser.goto(URL)


def complete_challenge(df_customers):
    # fill data to crm
    for customer in df_customers.rows(named=True):
        fill_and_submit_form(customer)


def fill_and_submit_form(customer):
    page = browser.page()
    page.fill("#customerName", str(customer["Company Name"]))
    page.fill("#customerID", str(customer["Customer ID"]))
    page.fill("#primaryContact", str(customer["Primary Contact"]))
    page.fill("#street", str(customer["Street Address"]))
    page.fill("#city", str(customer["City"]))
    page.fill("#zip", str(customer["Zip"]))
    page.fill("#email", str(customer["Email Address"]))
    page.locator("#state").select_option(str(customer["State"]))
    if str(customer["Offers Discounts"]) == "YES":
        page.locator("#activeDiscountYes").check()
    else:
        page.locator("#activeDiscountNo").check()
    if str(customer["Non-Disclosure On File"]) == "YES":
        page.locator("#NDA").check()
    page.locator("#submit_button").click(force=True, no_wait_after=True)


def get_customers_data() -> DataFrame:
    page = browser.page()
    download_csv_element = page.locator("css=p.lead a")
    csv_url = download_csv_element.get_attribute("href")
    local_filename = download_file(csv_url, CSV_PATH, TARGET_FILENAME)
    df_customers = pl.read_csv(local_filename)
    return df_customers


def challenge_verification():
    """
    Verifies challenge results by taking result screenshot
    Logs challenge id info
    """
    page = browser.page()
    page.wait_for_selector("css=.modal-body")
    completion_modal = page.locator("css=.modal-body")
    browser.screenshot(completion_modal)
    completion_id = page.locator("id=guidvalue").input_value()
    log.info(f"Challenge completion id: {completion_id}")


def download_file(url: str, target_dir: Path, target_filename: str) -> str:
    """
    Downloads a file from the given url into the given folder with given filename.
    """
    target_dir.mkdir(exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()  # This will raise an exception if the request fails
    local_filename = Path(target_dir, target_filename)
    with open(local_filename, "wb") as f:
        f.write(response.content)  # Write the content of the response to a file
    return local_filename
