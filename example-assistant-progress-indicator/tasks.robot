*** Settings ***
Documentation       An Assistant Robot.

Library             OperatingSystem
Library             RPA.Assistant
Library             String
Resource            challenge.resource

Suite Teardown      Close All Browsers


*** Variables ***
${STEP_DELAY}       0.4


*** Tasks ***
Complete rpa challenge
    [Documentation]
    ...    The completes rpa challenge and
    ...    displays process progress

    Display Process Run
    ${result}    RPA.Assistant.Run Dialog
    ...    title=Assistant Template
    ...    on_top=True
    ...    height=450
    IF    "${result.submit}" == "Cancel"
        Log    \nProcess Canceled    console=True
    ELSE
        Log    \nProcess Completed    console=True
    END
    Collect the results


*** Keywords ***
Display Process Run
    [Documentation]    Main keyword to build dialog used for
    ...    for the process run
    Clear Dialog
    Add Heading    Spinner Example
    Open Row
    Add Button    Start Process With Spinner    Show Process Progress With Indicator    spinner
    Add Button    Start Process With Bar    Show Process Progress With Indicator    bar
    Close Row
    Add Submit Buttons    buttons=Cancel    default=Cancel

Show Process Progress With Indicator
    [Documentation]    Adds process progess indicator and processes records
    [Arguments]    ${process_indicator}=bar

    ${process_indicator}    Convert To Lower Case    ${process_indicator}
    Set Title    Process Running
    Start the challenge
    ${people}    Get the list of people from the Excel file
    # calculate ticks for indicator
    ${records}    Get Length    ${people}
    ${tick}    Evaluate    ${records} / 100

    Click Button    Start

    FOR    ${index}    ${person}    IN ENUMERATE    @{people}    start=1
        Clear Dialog
        Add Heading    Process Running
        ${progress}    Evaluate    ${index} * ${tick}
        Open Row
        IF    "${process_indicator}" == "bar"
            ${loading_bar}    Add Loading Bar    Test Bar    width=100    value=${progress}
        ELSE IF    "${process_indicator}" == "spinner"
            ${loading_bar}    Add Loading Spinner    Test Bar    value=${progress}
        END
        Add Text    Item: ${index}
        Close Row
        Open Row
        Add Text    Processing: ${person}[First Name] ${person}[Last Name]
        Close Row
        Refresh Dialog
        Fill and submit the form    ${person}
        Sleep    ${STEP_DELAY}
    END

    Clear Dialog
    Open Row
    Set Title    Process Completed
    Add Heading    Process Completed
    Add Submit Buttons    buttons=Close    default=Close
    Close Row
    Refresh Dialog
