*** Settings ***
Documentation       Database examples using RPA.Database

Library             RPA.Database
Library             TablePrint.py

Task Setup          Connect to Northwind
Task Teardown       Disconnect From Database


*** Tasks ***
Minimal task
    Query using WITH
    Simple Query


*** Keywords ***
Query using WITH
    ${with_query}    Catenate
    ...    SEPARATOR=
    ...    WITH cte_quantity AS
    ...    (SELECT SUM(Quantity) as Total${SPACE}
    ...    FROM 'Order Details' GROUP BY ProductID)
    ...    SELECT AVG(Total) average_product_quantity${SPACE}
    ...    FROM cte_quantity
    @{rows}    Query    ${with_query}
    Log    ${rows}    console=${True}

Simple Query
    ${simple_query}    Catenate
    ...    SEPARATOR=
    ...    SELECT * FROM Products
    ${rows}    Query    ${simple_query}
    Log Table    ${rows}

Connect to Northwind
    Connect To Database    sqlite3    northwind.db
