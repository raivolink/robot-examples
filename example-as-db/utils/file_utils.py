def read_query_file(file_path: str) -> str:
    with open(file_path) as f:
        sql_query = f.read()

    return sql_query
