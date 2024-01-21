from playwright.sync_api import Page
from robocorp import browser
from robocorp.tasks import task

CHALLENGE_URL = "https://developer.automationanywhere.com/challenges/automationanywherelabs-quarterclose.html"


@task
def solve_challenge():
    """Completes Close quarter challenge"""
    launch_browser()
    open_transaction_website()
    transaction_data = get_transactions()
    transaction_data = match_transactions(transaction_data)
    update_transaction_statuses(transaction_data)
    submit_challenge()


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


def open_transaction_website():
    browser.goto(CHALLENGE_URL)
    transaction_page = browser.page()
    transaction_page.click("#onetrust-accept-btn-handler", no_wait_after=True)


def get_transactions() -> list:
    """
    Collects initial transaction data

    Returns:
        list: Collected accounts and amounts
    """
    page = browser.page()
    transaction_data = []
    transaction_list = page.locator('css=div[id^="transaction"]').all()
    for index, transaction in enumerate(transaction_list, start=1):
        account = page.locator(f"#PaymentAccount{index}").input_value()
        amount = page.locator(f"#PaymentAmount{index}").input_value()
        current_transaction = {"id": index, "Account": account, "Amount": amount}
        transaction_data.append(current_transaction)
    # sort accounts
    transaction_data = sorted(transaction_data, key=lambda d: d["Account"])
    return transaction_data


def open_bank_page_and_log_in() -> Page:
    """
    Opens banks page and inserts account credentials

    Returns:
        Page: Bank page id
    """
    page = browser.page()
    context = browser.context()
    with context.expect_page() as new_page:
        page.click("text=Arcadia Bank Login")
    bank_page = new_page.value
    bank_page.fill("id=inputEmail", "tammy.peters@petersmfg.com")
    bank_page.fill("id=inputPassword", "arcadiabank!")
    bank_page.click("css=a >> text=Login")
    return bank_page


def open_account_page(bank_page: Page, account: str):
    bank_page.click(f"css=a >> text={account}")


def search_transaction(bank_page: Page, amount: str):
    search_input = bank_page.locator(".datatable-search > .datatable-input")
    search_input.fill("")
    search_input.press_sequentially(amount)
    search_input.press("Enter")


def match_transactions(transaction_data: list) -> list:
    """
    Matches transactions on bank pages, when found marks as
    Verified. If transaction is not found marks as Unverified

    Args:
        transaction_data (list): Data collected from transaction page

    Returns:
        lisy: Transaction date with updated statuses.
    """
    bank_page = open_bank_page_and_log_in()
    current_account = ""
    for index, transaction in enumerate(transaction_data):
        if current_account != transaction["Account"]:
            open_account_page(bank_page, transaction["Account"])
            current_account = transaction["Account"]
        search_transaction(bank_page, transaction["Amount"])
        if bank_page.locator("text=Showing 1 to 1 of 1 entries").is_visible():
            transaction_data[index]["Status"] = "Verified"
        else:
            transaction_data[index]["Status"] = "Unverified"
    return transaction_data


def update_transaction_statuses(transaction_data: list):
    page = browser.page()
    page.bring_to_front()
    for transaction in transaction_data:
        page.select_option(
            f'css=#transaction{transaction["id"]} select[id^="Status"]',
            transaction["Status"],
        )


def submit_challenge():
    """Submits challenge, takes result screenshot and
    logs completion id to the log
    """
    page = browser.page()

    page.click("id=submitbutton")
    page.wait_for_selector("css=.modal-body")
    completion_modal = page.locator("css=.modal-body")
    browser.screenshot(completion_modal)
