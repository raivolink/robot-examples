*** Settings ***
Library     Collections
Library     RPA.Robocorp.WorkItems
Library     RPA.Tables


*** Tasks ***
Consume Zendesk Request
    [Documentation]    Login and then cycle through work items.
    TRY
        For Each Input Work Item    Handle item
    EXCEPT    AS    ${err}
        Log    ${err}    level=ERROR
        Release Input Work Item
        ...    state=FAILED
        ...    exception_type=APPLICATION
        ...    code=UNCAUGHT_ERROR
        ...    message=${err}
    END


*** Keywords ***
Login
    [Documentation]
    ...    Simulates a login that fails 1/5 times to highlight APPLICATION exception handling.
    ...    In this example login is performed only once for all work items.
    ...
    ${Login as James Bond}=    Evaluate    random.randint(1, 5)

    IF    ${Login as James Bond} != 1
        Log    Logged in as Bond. James Bond.
    ELSE
        Fail    Login failed
    END

Action for item
    [Documentation]
    ...    Gets Zendesk request and processes payload
    [Arguments]    ${payload}

    ${requester_email}=    Get Work Item Variable    requester_mail
    ${ticket_id}=    Get Work Item Variable    ticket_id

    &{variables}=    Create Dictionary
    ...    requester_mail    ${requester_email}
    ...    ticket_id    ${ticket_id}
    ...    message    Requester with mail:${requester_email} and request id:${ticket_id}

    Create Output Work Item    variables=${variables}    save=${True}

Handle item
    [Documentation]    Error handling around one work item.

    ${payload}=    Get Work Item Variables

    TRY
        Action for item    ${payload}
        Release Input Work Item    DONE
    EXCEPT    Invalid data    type=START    AS    ${err}
        # Giving a good error message here means that data related errors can
        # be fixed faster in Control Room.
        # You can extract the text from the underlying error message.
        ${error_message}=    Set Variable
        ...    Data may be invalid, encountered error: ${err}
        Log    ${error_message}    level=ERROR
        Release Input Work Item
        ...    state=FAILED
        ...    exception_type=BUSINESS
        ...    code=INVALID_DATA
        ...    message=${error_message}
    EXCEPT    *timed out*    type=GLOB    AS    ${err}
        ${error_message}=    Set Variable
        ...    Application error encountered: ${err}
        Log    ${error_message}    level=ERROR
        Release Input Work Item
        ...    state=FAILED
        ...    exception_type=APPLICATION
        ...    code=TIMEOUT
        ...    message=${error_message}
    END
