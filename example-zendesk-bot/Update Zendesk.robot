*** Settings ***
Documentation       Updates Zendesk ticket after previous processing

Library             RPA.Robocorp.WorkItems
Library             RPA.Robocorp.Vault
Library             RPA.Robocorp.Storage
Library             RPA.HTTP
Library             Collections
Library             RPA.JSON


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

    ${ticket_id} =    Get Work Item Variable    ticket_id
    ${message} =    Get Work Item Variable    message

    &{comment} =    Create Dictionary    body=${message}    public=false
    &{ticket} =    Create Dictionary    comment=&{comment}
    &{ticket_body} =    Create Dictionary    ticket=&{ticket}
    ${body_json} =    Convert JSON to string    ${ticket_body}

    Send Zendesk Ticket Update    ${ticket_id}    ${body_json}

Update Zendesk Ticket From Asset
    [Documentation]    Updates Zendesk ticket based on asset template

    ${ticket_id} =    Get Work Item Variable    ticket_id
    ${message} =    Get Work Item Variable    message

    ${body_json} =    Get Text Asset    Zendesk-comment
    ${body_json} =    Replace Variables    ${body_json}

    Send Zendesk Ticket Update    ${ticket_id}    ${body_json}

Send Zendesk Ticket Update
    [Documentation]    Sends update request to zendesk
    ...    using tickets api endpoint
    [Arguments]    ${ticket_id}    ${body_json}

    ${zendesk_secret} =    Get Secret    ZendeskService

    &{headers} =    Create Dictionary
    ...    Content-Type=application/json
    ...    Authorization=${zendesk_secret}[Authorization]

    ${resp} =    PUT
    ...    url=${zendesk_secret}[BaseUrl]/api/v2/tickets/${ticket_id}
    ...    data=${body_json}
    ...    headers=&{headers}
    ...    expected_status=200
