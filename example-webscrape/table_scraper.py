import httpx
from robocorp.tasks import task
from selectolax.parser import HTMLParser


def get_headers_list(header_nodes):
    return [header.text(strip=True) for header in header_nodes[:-1]]


def get_table_data(rows, headers):
    cell_content = []
    for row in rows[1:]:
        cells = row.css("td")
        cell_values = [cell.text(strip=True) for cell in cells[:-1]]
        cell_content.append(dict(zip(headers, cell_values)))
    return cell_content


@task
def get_table():
    r = httpx.get("https://the-internet.herokuapp.com/tables")
    pass
    # get content from response
    tree = HTMLParser(r.content)

    # get table headers content
    table_headers = get_headers_list(tree.css("#table1 th"))

    cell_content = get_table_data(tree.css("#table1 tr"), table_headers)
    print(cell_content)
