from robocorp import browser
from robocorp.tasks import task


CHALLENGE_URL = "https://developer.automationanywhere.com/challenges/automationanywherelabs-quarterclose.html"


# TODO group by account for better performance?
@task
def solve_challenge():
    """Complete Close quarter challenge"""
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


def get_transactions():
    page = browser.page()
    transaction_data = []
    transaction_list = page.locator('css=div[id^="transaction"]').all()
    for index, transaction in enumerate(transaction_list, start=1):
        account = page.locator(f"#PaymentAccount{index}").input_value()
        amount = page.locator(f"#PaymentAmount{index}").input_value()
        transaction = {"id": index, "Account": account, "Amount": amount}
        transaction_data.append(transaction)
    return transaction_data


def open_bank_page_and_log_in():
    page = browser.page()
    context = browser.context()
    with context.expect_page() as new_page:
        page.click("text=Arcadia Bank Login")
    bank_page = new_page.value
    bank_page.fill("id=inputEmail", "tammy.peters@petersmfg.com")
    bank_page.fill("id=inputPassword", "arcadiabank!")
    bank_page.click("css=a >> text=Login")
    return bank_page


def open_account_page(bank_page, account):
    bank_page.click(f"css=a >> text={account}")


def search_transaction(bank_page, amount):
    search_input = bank_page.locator(".datatable-search > .datatable-input")
    search_input.press_sequentially(amount)
    search_input.press("Enter")


def match_transactions(transaction_data):
    bank_page = open_bank_page_and_log_in()
    for index, transaction in enumerate(transaction_data):
        open_account_page(bank_page, transaction["Account"])
        search_transaction(bank_page, transaction["Amount"])
        if bank_page.locator("text=Showing 1 to 1 of 1 entries").is_visible():
            transaction_data[index]["Status"] = "Verified"
        else:
            transaction_data[index]["Status"] = "Unverified"
    return transaction_data


def update_transaction_statuses(transaction_data):
    page = browser.page()
    page.bring_to_front()
    for transaction in transaction_data:
        # print(f'css=#transaction{transaction["id"]} select[id^="Status"]')
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
