"""
A simple AI Action template for database actions

Please checkout the base guidance on AI Actions in our main repository readme:
https://github.com/robocorp/robocorp/blob/master/README.md

"""

import sqlite3

from robocorp.actions import action

from utils import files


@action
def get_customer(first_name: str) -> str:
    """
    List customers by first name.

    Args:
        first_name (str): Customer's first name in string format. Example: "Jill"

    Returns:
        str: List of customers based on the first name (customer name, position).
    """
    output_str: list[str] = []

    # Connect to the SQLite database
    conn = sqlite3.connect("northwind.db")
    cursor = conn.cursor()

    # Create query to retrieve customer information
    sql_query = files.read_query_file("queries/get_customer.sql")
    # Execute a SELECT query to retrieve customer information
    cursor.execute(sql_query, (first_name + "%",))

    # Fetch all the results
    customers = cursor.fetchall()
    # build the response list
    response = [
        f"Customer name: {customer[2]}, Position: {customer[3]}, Company Name: {customer[1]}"
        for customer in customers
    ]

    # Close the connection
    cursor.close()
    conn.close()
    # build the output string
    if not response:
        output_str = "No matches found"
    else:
        output_str = "\n".join(response)
    # print(output_str)
    return output_str


@action
def get_order_details(company_name: str) -> str:
    """
    List order details by company name.

    Args:
        company_name (str): Company name in string format needs to be exact match. Example: "Microsoft"

    Returns:
        str: List of orders by company.
    """
    output_str: list[str] = []
    # Connect to the SQLite database
    conn = sqlite3.connect("northwind.db")
    cursor = conn.cursor()

    # Create query to retrieve customer information
    sql_query = files.read_query_file("queries/get_order_details.sql")
    # Execute a query
    cursor.execute(sql_query, (company_name,))

    # Fetch all the results
    orders = cursor.fetchall()

    response = [
        f"Order id: {order[0]}, Company: {order[2]}, Product: {order[4]}"
        for order in orders
    ]

    # Close the connection
    cursor.close()
    conn.close()
    # build the output string
    if not response:
        output_str = "No matches found"
    else:
        output_str = "\n".join(response)
    # print(output_str)
    return output_str
