*** Settings ***
Documentation       Robot that reads bowser console logs

Library             RPA.Browser.Selenium


*** Variables ***
&{browser logging capability}       browser=ALL
&{capabilities}
...                                 version=${EMPTY}
...                                 platform=ANY
...                                 goog:loggingPrefs=${browser logging capability}


*** Tasks ***
Browser Log Cases
    Open Available Browser
    ...    https://rpachallenge.com/
    ...    preferences=${capabilities}
    Set Log Level    TRACE
    ${log entries}=    Get Browser Console Log Entries
    Log    ${log entries}
    [Teardown]    Close All Browsers


*** Keywords ***
Get Browser Console Log Entries
    ${selenium}=    Get Library Instance    RPA.Browser.Selenium
    ${webdriver}=    Set Variable    ${selenium._drivers.active_drivers}[0]
    ${log entries}=    Evaluate    $webdriver.get_log('browser')
    RETURN    ${log entries}
