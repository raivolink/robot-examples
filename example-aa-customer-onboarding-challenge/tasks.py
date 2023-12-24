from robocorp import browser, log
from pathlib import Path
import polars as pl
from robocorp.tasks import get_output_dir, task

from RPA.HTTP import HTTP

OUTPUT_DIR = get_output_dir() or Path("output")
CSV_PATH = OUTPUT_DIR / "customers.csv"
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


def get_customers_data():
    page = browser.page()
    download_csv_element = page.locator("css=p.lead a")
    csv_url = download_csv_element.get_attribute("href")
    HTTP().download(csv_url, CSV_PATH, overwrite=True)
    df_customers = pl.read_csv(CSV_PATH)
    return df_customers


def challenge_verification():
    page = browser.page()
    page.wait_for_selector("css=.modal-body")
    completion_modal = page.locator("css=.modal-body")
    browser.screenshot(completion_modal)
    completion_id = page.locator("id=guidvalue").input_value()
    log.info(f"Challenge completion id: {completion_id}")
