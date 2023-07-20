from robocorp import browser, log
from robocorp.tasks import task
from RPA.Tables import Tables

CHALLENGE_URL = "https://developer.automationanywhere.com/challenges/financialvalidation-challenge.html"
username = "finance_dept@foodmartgrocerycorp.com"
password = "dR6Si6O&?u1rIp2iSOz-"


@task
def solve_challenge():
    with log.suppress_variables():
        start_challenge()
        transaction_table = get_transactions()
        bank_page_id = login_to_rusty_bank()
        transaction_table = get_supplier_data(transaction_table, bank_page_id)
        fill_suppliers(transaction_table)
        complete_challenge()
        log.console_message("Challenge completed", "regular")


def start_challenge():
    browser.configure(
        browser_engine="chromium",
        screenshot="only-on-failure",
        # headless=False,
        # slowmo=500,
    )
    context = browser.context()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    context.set_extra_http_headers({"User-Agent": user_agent})
    browser.goto(CHALLENGE_URL)


def get_transactions():
    page = browser.page()
    list_of_transactions = page.locator("//form[starts-with(@id, 'transaction')]")
    challenge_table = Tables().create_table(
        columns=["TransactionID", "Account", "Amount", "Supplier"]
    )

    for transaction in range(1, list_of_transactions.count() + 1):
        transaction_amount = page.locator(f"#PaymentAmount{transaction}").input_value()
        transaction_account = page.locator(
            f"#PaymentAccount{transaction}"
        ).input_value()
        Tables().add_table_row(
            challenge_table,
            {
                "TransactionID": transaction,
                "Account": transaction_account,
                "Amount": transaction_amount,
            },
        )
    return challenge_table


def login_to_rusty_bank():
    """Launches bank application and log in"""
    page = browser.page()
    context = browser.context()
    with context.expect_page() as new_bank_page:
        page.click("text=Rusty Bank Login")

    bank_app_page = new_bank_page.value
    bank_app_page.wait_for_load_state()

    try:
        bank_app_page.click("//*[@id='onetrust-accept-btn-handler']")
    except:
        log.info("No cookies for robot")
    bank_login(bank_app_page)
    return bank_app_page


def bank_login(bank_page_id):
    bank_page_id.fill("id=inputEmail", username)
    bank_page_id.fill("id=inputPassword", password)
    bank_page_id.click("text=Login")

    bank_page_id.wait_for_load_state()


def get_supplier_data(transactions_table, bank_page_id):
    """Gets supplier names from banking app.

    Args:
        transactions_table: Tables object containing transactions
        bank_page_id: id for interaction page

    Returns:
        Tables object with added supplier names

    """
    Tables().sort_table_by_column(transactions_table, "Account")
    current_account = ""
    context = browser.context()
    context.set_default_timeout(5000)
    for index, transaction in enumerate(transactions_table):
        while True:
            try:
                if transaction["Account"] == current_account:
                    bank_page_id.fill("css=.dataTable-input", transaction["Amount"])
                else:
                    account_locator = (
                        f"//a[text()[contains(.,'{transaction['Account']}')]]"
                    )
                    bank_page_id.click(account_locator)
                    bank_page_id.wait_for_load_state()
                    current_account = transaction["Account"]
                    bank_page_id.fill("css=.dataTable-input", transaction["Amount"])

                bank_page_id.press("css=.dataTable-input", "Enter")

                supplier = bank_page_id.query_selector("xpath=(//td)[5]").inner_text()

                Tables().set_table_cell(transactions_table, index, "Supplier", supplier)
            except:
                bank_page_id.click("//button[contains(text(),'Take')]")
                bank_login(bank_page_id)
                current_account = ""
                continue
            break
    context.set_default_timeout(30000)
    log.info(transactions_table)
    return transactions_table


def fill_suppliers(transactions_table):
    """Adds supplier names on initial transcation page"""
    page = browser.page()
    page.bring_to_front()

    for transaction in transactions_table:
        page.fill(f"id=Supplier{transaction['TransactionID']}", transaction["Supplier"])

    page.click("#submitChallenge")


def complete_challenge():
    """Completes challenge by taking screenshot
    of final modal and logging challenge id"""
    page = browser.page()

    page.wait_for_selector("css=.modal-body")
    completion_modal = page.locator("css=.modal-body")
    browser.screenshot(completion_modal)
    completion_id = page.locator("id=guidvalue").input_value()
    log.info(f"Completion id: {completion_id}")
