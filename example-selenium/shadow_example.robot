*** Settings ***
Documentation       Robot clicking button inside shadow dom

Library             RPA.Browser.Selenium


*** Variables ***
${URL}      https://yhteishyva.fi/


*** Tasks ***
Open Site And Accept Cookies
    Open Available Browser    ${URL}
    Sleep    2s
    ${shadow_root}    Get WebElement    id:usercentrics-root    shadow=${True}
    ${accept_button}    Get WebElement    css:button[data-testid="uc-accept-all-button"]    ${shadow_root}
    Click Button When Visible    ${accept_button}
    Wait Until Element Is Visible    (//div[@class='interstitial-ad-content']//*[text()='Sulje mainos'])[1]
    Click Element    (//div[@class='interstitial-ad-content']//*[text()='Sulje mainos'])[1]
    Sleep    5s
