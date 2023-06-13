*** Settings ***
Documentation       Template robot main suite.

Library             Collections
Library             MyLibrary
Library             RPA.Calendar
Resource            keywords.robot
Variables           variables.py


*** Tasks ***
Example task
    Example Keyword
    Example Python Keyword
    Log    ${TODAY}
    ${iso_cal}=    Get Iso Calendar    2023-03-09
    ${iso_year}=    Set Variable    ${iso_cal.year}
    ${iso_week}=    Set Variable    ${iso_cal.week}
    ${iso_weekday}=    Set Variable    ${iso_cal.weekday}
    Log    ${iso_week}    console=${True}
