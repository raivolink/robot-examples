import json

from openai import OpenAI
from robocorp import browser, log, storage, vault
from robocorp.browser import Page
from robocorp.tasks import task

CHALLENGE_URL = (
    "https://developer.automationanywhere.com/challenges/healthcare-ai-challenge.html"
)
VAULT_SECRET = "OpenAI"
AA_CREDENTIALS = "AA_community"
gpt_model = "gpt-3.5-turbo"


@task
def solve_ai_challenge():
    """Completes healthcare challenge by AA.
    Automation reads mailbox for doctor emails and
    extracts data from them. Data is sent to gpt to get
    structured content from mail body. Retrieved data is
    inserted to Medikorps portal.
    """
    start_ai_challenge()
    login_to_aa()
    mailbox_page = open_mailbox()
    patient_cases = get_unread_mail_content(mailbox_page)
    patient_cases = get_structured_data_from_gpt(patient_cases)
    fill_patient_data(patient_cases)
    submit_challenge()
    log.console_message("Challenge completed", "regular")


def start_ai_challenge() -> None:
    """Launches browser and opens challenge page"""
    browser.configure(
        browser_engine="chromium",
        screenshot="only-on-failure",
    )
    context = browser.context()
    # user_agent is neede for headless runs
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    context.set_extra_http_headers({"User-Agent": user_agent})
    browser.goto(CHALLENGE_URL)


def open_mailbox() -> Page:
    """Opens mailbox page

    Returns:
        Page: Page for mailbox interactions
    """
    page = browser.page()
    context = browser.context()
    with context.expect_page() as new_mailbox:
        page.click("id=mailboxButton")

    mailbox_page = new_mailbox.value
    mailbox_page.wait_for_load_state()

    return mailbox_page


def get_unread_mail_content(mailbox_page: Page) -> None:
    """Gets unread mails from mailbox and read data from them

    Args:
        mailbox_page (Page): Page for mailbox interactions

    Returns:
        List: Patient data with doctor name and notes
    """
    patient_cases = []
    list_of_unread_mails = mailbox_page.query_selector_all(
        "//*[text()='unread']//parent::div"
    )
    for unread_mail in list_of_unread_mails:
        unread_mail.click()
        doctor_notes = mailbox_page.locator("id=emailContainer").inner_text()
        doctor_name = unread_mail.query_selector("span.mb-0").inner_text()
        current_case = [doctor_name, doctor_notes]
        patient_cases.append(current_case)
        mailbox_page.click("id=backButton")
    return patient_cases


def authorize_openai() -> None:
    """Retrieves api key from vault and authorizes
    gpt usage.
    """
    secrets_container = vault.get_secret(VAULT_SECRET)
    client = OpenAI(
        api_key=secrets_container[
            "api-key"
        ],  # this is also the default, it can be omitted
    )
    return client


def ask_gpt(conversation):
    """Conversation with gpt

    Args:
        conversation (OpenAIObject): current conversation with gpt

    Returns:
        OpenAIObject: Gpt conversation
    """
    client = authorize_openai()
    response = client.completions.create(
        model=gpt_model,
        messages=conversation,
        temperature=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response


def get_structured_data_from_gpt(patient_cases: list[str]) -> list[str]:
    """Sends doctors note to gpt to get structured
    patient diagnosis data

    Args:
        patient_cases (List): Data with patient diagnosis

    Returns:
        List: Data with patient diagnosis with gpt response added
    """
    authorize_openai()
    conversation = []

    initial_prompt = storage.get_text("healthcare-challenge-prompt")
    conversation.append({"role": "user", "content": initial_prompt})

    for patient, case in enumerate(patient_cases):
        conversation.append({"role": "user", "content": case[1]})
        response = ask_gpt(conversation)
        patient_data = json.loads(response["choices"][0]["message"]["content"])
        patient_cases[patient].append(patient_data)

    return patient_cases


def fill_patient_data(patient_cases) -> None:
    """Fills patient data with data from doctors note.

    Args:
        patient_cases (List): Data with patient diagnosis
    """
    page = browser.page()
    page.bring_to_front()
    for case in patient_cases:
        patient_detail = case[2]
        doctors_name = case[0]

        page.fill("id=doctorName", doctors_name)
        page.fill("id=patientName", patient_detail["PatientName"])
        page.fill("id=patientWeight", str(patient_detail["Weight"]))
        page.fill("id=patientBP", str(patient_detail["BloodPressure"]))
        page.fill("id=patientBloodOxygen", str(patient_detail["BloodOxygenLevel"]))
        page.fill("id=patientHeartRate", str(patient_detail["RestingHeartRate"]))
        page.fill("id=patientDiagnosis", patient_detail["Diagnosis"])
        page.fill("id=patientHeight", str(patient_detail["Height"]))
        medicines = patient_detail["MedicinesPrescribed"]
        if len(medicines) > 0:
            page.click("id=patientMedication")
            medicine_list = medicines.split(",")
            for count, medicine in enumerate(medicine_list, start=1):
                page.fill(f"id=prescribedMedicine{count}", medicine)
        page.click("id=add_button")


def submit_challenge() -> None:
    """Submits challenge, takes result screenshot and
    logs completion id to the log
    """
    page = browser.page()

    page.click("id=submit_button")
    page.wait_for_selector("css=.modal-body")
    completion_modal = page.locator("css=.modal-body")
    browser.screenshot(completion_modal)
    completion_id = page.locator("id=guidvalue").input_value()
    log.info(f"Completion id: {completion_id}")
    log.info(f"Completion id: {completion_id}")


def login_to_aa() -> None:
    """
    Handles initial login to AA challanges site
    """
    credentials_container = vault.get_secret(AA_CREDENTIALS)
    page = browser.page()
    page.locator("#onetrust-accept-btn-handler").click()
    page.locator("xpath=//button[contains(.,'Community login')]").click()
    page.locator("xpath=//label[contains(.,'Email')]/../input").fill(
        credentials_container["user"]
    )
    page.locator("xpath=//button[contains(.,'Next')]").click()
    page.locator("xpath=//label[contains(.,'Password')]/../input").fill(
        credentials_container["password"]
    )
    page.locator("xpath=//button[contains(.,'Log in')]").click()
