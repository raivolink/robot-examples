*** Settings ***
Documentation       Updates Zendesk ticket after previous processing

Library             RPA.Robocorp.WorkItems
Library             RPA.Robocorp.Vault
Library             RPA.Robocorp.Storage
Library             RPA.HTTP
Library             Collections
Library             RPA.JSON

Suite Setup         Create Zendesk Session
Suite Teardown      Delete All Sessions


*** Tasks ***
Update Zendesk
    [Documentation]    Update Zendesk ticket internal comment
    ...    with message from work item.

    TRY
        For Each Input Work Item    Update Zendesk Ticket From Asset
    EXCEPT    AS    ${err}
        Log    ${err}    level=ERROR
        Release Input Work Item
        ...    state=FAILED
        ...    exception_type=INTEGRATION
        ...    code=API_FAILURE
        ...    message=${err}
    END


*** Keywords ***
Update Zendesk Ticket From Data
    [Documentation]    Updates Zendesk ticket based on create dictonary
    ...    Example with building request body with dictonaries
    ${ticket_id} =    Get Work Item Variable    ticket_id
    ${message} =    Get Work Item Variable    message

    &{comment} =    Create Dictionary    body=${message}    public=false
    &{ticket} =    Create Dictionary    comment=&{comment}
    &{ticket_body} =    Create Dictionary    ticket=&{ticket}
    ${body_json} =    Convert JSON to string    ${ticket_body}

    # Need to remove tigger tag first ot avoid subsequent runs
    Remove Bot Tag    ${ticket_id}
    # Update ticket with comment
    Send Zendesk Ticket Update    ${ticket_id}    ${body_json}

Update Zendesk Ticket From Asset
    [Documentation]    Updates Zendesk ticket based on asset template
    ...    Example using storage for request body

    ${ticket_id} =    Get Work Item Variable    ticket_id
    ${message} =    Get Work Item Variable    message

    ${body_json} =    Get Text Asset    Zendesk-comment
    ${body_json} =    Replace Variables    ${body_json}

    # Need to remove tigger tag first ot avoid subsequent runs
    Remove Bot Tag    ${ticket_id}
    # Update ticket with comment
    Send Zendesk Ticket Update    ${ticket_id}    ${body_json}

Send Zendesk Ticket Update
    [Documentation]    Sends update request to zendesk
    ...    using tickets api endpoint
    [Arguments]    ${ticket_id}    ${body_json}

    ${resp} =    PUT On Session
    ...    Zendesk
    ...    url=/api/v2/tickets/${ticket_id}
    ...    data=${body_json}
    ...    expected_status=200

Remove Bot Tag
    [Documentation]    Removes triggering tag from ticket to revent
    ...    unexpected robot runs
    [Arguments]    ${ticket_id}

    ${body_json} =    Set Variable    {"tags": ["bot_trigger_1"]}
    ${resp} =    DELETE On Session
    ...    Zendesk
    ...    url=/api/v2/tickets/${ticket_id}/tags
    ...    data=${body_json}
    ...    expected_status=200

Create Zendesk Session
    [Documentation]    Creates session for zendesk to use on api calls
    ${zendesk_secret} =    Get Secret    ZendeskService

    &{headers} =    Create Dictionary
    ...    Content-Type=application/json
    ...    Authorization=${zendesk_secret}[Authorization]
    Create Session    Zendesk
    ...    ${zendesk_secret}[BaseUrl]
    ...    headers=&{headers}
