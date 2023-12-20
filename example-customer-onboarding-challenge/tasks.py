from robocorp import browser, log
from pathlib import Path
import polars as pl
from robocorp.tasks import get_output_dir, task

from RPA.Excel.Files import Files as Excel
from RPA.HTTP import HTTP

OUTPUT_DIR = get_output_dir() or Path("output")
CSV_PATH = OUTPUT_DIR / "customers.csv"
URL = "https://developer.automationanywhere.com/challenges/automationanywherelabs-customeronboarding.html"
output = get_output_dir() or Path("output")
# TODO Add documentation


@task
def solve_challenge():
    """Solve the RPA challenge"""
    browser.configure(
        browser_engine="chromium",
        screenshot="only-on-failure",
        headless=False,
    )

    browser.goto(URL)

    df_customers = get_customers_data()

    for customer in df_customers.rows(named=True):
        fill_and_submit_form(customer)

    completion_verification()


def fill_and_submit_form(customer):
    page = browser.page()
    page.fill("#customerName", str(customer["Company Name"]))
    page.fill("#customerID", str(customer["Customer ID"]))
    page.fill("#primaryContact", str(customer["Primary Contact"]))
    page.fill("#street", str(customer["Street Address"]))
    page.fill("#city", str(customer["City"]))
    page.fill("#zip", str(customer["Zip"]))
    page.fill("#email", str(customer["Email Address"]))
    page.query_selector("#state").select_option(str(customer["State"]))
    if str(customer["Offers Discounts"]) == "YES":
        page.locator("#activeDiscountYes").check()
    else:
        page.locator("#activeDiscountNo").check()
    if str(customer["Non-Disclosure On File"]) == "YES":
        page.locator("#NDA").check()
    page.locator("#submit_button").click(force=True, no_wait_after=True)


def get_customers_data():
    page = browser.page()
    download_csv_element = page.query_selector("css=p.lead a")
    csv_url = download_csv_element.get_attribute("href")
    HTTP().download(csv_url, CSV_PATH, overwrite=True)
    df_customers = pl.read_csv(CSV_PATH)
    return df_customers


def completion_verification():
    page = browser.page()
    page.wait_for_selector("css=.modal-body")
    completion_modal = page.locator("css=.modal-body")
    browser.screenshot(completion_modal)
    completion_id = page.locator("id=guidvalue").input_value()
    log.info(f"Completion id: {completion_id}")
