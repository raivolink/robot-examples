from robocorp import browser, log
from pathlib import Path
import polars as pl
from robocorp.tasks import get_output_dir, task

from RPA.HTTP import HTTP

OUTPUT_DIR = get_output_dir() or Path("output")
EXCEL_PATH = OUTPUT_DIR / "agents.xlsx"
PROCUREMENT_URL = "https://developer.automationanywhere.com/challenges/AutomationAnywhereLabs-POTrackingLogin.html"
PURCHASE_ORDERS_URL = "https://developer.automationanywhere.com/challenges/automationanywherelabs-supplychainmanagement.html"


@task
def solve_challenge():
    """Complete the supply chain challenge"""
    launch_browser()
    open_procurement_website_and_log_in()
    purchase_order_page = open_po_page()
    agents_df = get_agents(purchase_order_page)
    po_numbers = get_po_numbers(purchase_order_page)
    get_po_data_and_insert_to_form(agents_df, po_numbers, purchase_order_page)
    challenge_verification(purchase_order_page)


def launch_browser():
    browser.configure(
        browser_engine="chromium",
        screenshot="only-on-failure",
        headless=False,
    )
    # user_agent is needed for headless runs
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    context = browser.context()
    context.set_extra_http_headers({"User-Agent": user_agent})


def open_po_page():
    purchase_order_page = browser.context().new_page()
    purchase_order_page.goto(PURCHASE_ORDERS_URL)
    return purchase_order_page


def get_agents(purchase_order_page):
    download_xlsx_element = purchase_order_page.locator(".challenge-intro a.btn")
    csv_url = download_xlsx_element.get_attribute("href")
    HTTP().download(csv_url, EXCEL_PATH, overwrite=True)
    df_agents = pl.read_excel(EXCEL_PATH)
    return df_agents


def get_po_numbers(purchase_order_page):
    po_numbers = {}
    po_list = [f"PONumber{number}" for number in range(1, 8)]
    for po in po_list:
        po_number = purchase_order_page.locator(f"#{po}").input_value()
        po_numbers[po] = po_number
    return po_numbers


def search_for_po(po_number, page):
    page.fill("#dtBasicExample_filter input", po_number)


def get_po_data_and_insert_to_form(df_agents, po_numbers, purchase_order_page):
    page = browser.page()
    # page.bring_to_front()
    for po in po_numbers:
        # TODO Clearer logic(using enumerate?)
        search_for_po(po_numbers[po], page)
        state = page.locator("#dtBasicExample td:nth-child(5)").inner_text()
        ship_date = page.locator("#dtBasicExample td:nth-child(7)").inner_text()
        order_total = page.locator("#dtBasicExample td:nth-child(8)").inner_text()[1:]
        agent_in_state = df_agents.filter(df_agents["State"] == state)
        agent_name = agent_in_state["Full Name"][0]
        # TODO Change logic for not switch pages
        current_po_index = po[-1]  # slice last value from string
        fill_po_form(
            current_po_index,
            ship_date,
            order_total,
            agent_name,
            purchase_order_page,
        )

    purchase_order_page.locator("#submit_button").click()


def open_procurement_website_and_log_in():
    browser.goto(PROCUREMENT_URL)
    page = browser.page()
    page.click("#onetrust-accept-btn-handler", no_wait_after=True)
    page.fill("#inputEmail", "admin@procurementanywhere.com")
    page.fill("#inputPassword", "paypacksh!p")
    page.click(".btn-primary")


def fill_po_form(index, ship_date, total, agent, purchase_order_page):
    # purchase_order_page.bring_to_front()
    purchase_order_page.fill(f"#shipDate{index}", str(ship_date))
    purchase_order_page.fill(f"#orderTotal{index}", str(total))
    purchase_order_page.locator(f"#agent{index}").select_option(str(agent))


def challenge_verification(purchase_order_page):
    """
    Function to add challenge result screenshot
    and id to generated log
    """
    purchase_order_page.wait_for_selector("css=.modal-body")
    completion_modal = purchase_order_page.locator("css=.modal-body")
    browser.screenshot(completion_modal)
    completion_id = purchase_order_page.locator("id=guidvalue").input_value()
    log.info(f"Challenge completion id: {completion_id}")
