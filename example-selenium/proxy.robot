*** Settings ***
Documentation       Robot witch is using proxy server
...                 without autentication

Library             RPA.Browser.Selenium


*** Variables ***
${IP_CHECK_URL}     http://httpbin.org/ip
${IP_CHECK_URL2}    https://whatismyipaddress.com/
${PROXY}            3.110.142.87:80


*** Tasks ***
Open Site With Basic Proxy Http
    Open Available Browser
    ...    ${IP_CHECK_URL}
    ...    proxy=${PROXY}
    ${MY_IP}    Get Text    //body
    Log    Current IP: ${MY_IP}    console=${True}
    Close All Browsers

Open Site With Basic Proxy Https
    Open Available Browser
    ...    ${IP_CHECK_URL2}
    ...    proxy=${PROXY}
    ${MY_IP}    Get Text    id:ipv4
    Screenshot
    Log    Current IP: ${MY_IP}    console=${True}
    Close All Browsers
