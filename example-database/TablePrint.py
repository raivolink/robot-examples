from prettytable import PrettyTable
from robot.libraries.BuiltIn import BuiltIn


def log_table(
    table_to_print, columns: int = None, rows: int = 5, log_to_console: bool = True
):
    """Print table content to console
    :param columns: maximum columns to print
    :param rows: maximum rows to print
    :param log_to_console: logs table to console
    Example.
    .. code-block:: robotframework
        Log Table
        ...  columns=3
        ...  rows=10
    """
    rpa_table = table_to_print
    pretty_table = PrettyTable()
    pretty_table.field_names = (
        rpa_table.columns[:columns] if columns else rpa_table.columns
    )
    for index, row in enumerate(rpa_table):
        if rows and (index + 1) > rows:
            break
        values = list(row.values())
        values = values[:columns] if columns else values
        pretty_table.add_row(values)
    BuiltIn().log(message=f"\n{pretty_table}", console=log_to_console)
