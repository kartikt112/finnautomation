from openpyxl import load_workbook


def parse_excel(file_path: str) -> list[dict]:
    """Parse an Excel file and return a list of row dicts.
    Validates that required columns (email/username + password) exist.
    """
    wb = load_workbook(file_path, read_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 2:
        raise ValueError("Excel file must have a header row and at least one data row")

    headers = [str(h).strip().lower() if h else "" for h in rows[0]]

    # Check for required columns
    has_email = any(h in ("email", "username", "user", "login") for h in headers)
    has_password = "password" in headers

    if not has_email:
        raise ValueError("Excel must have an 'Email' or 'Username' column")
    if not has_password:
        raise ValueError("Excel must have a 'Password' column")

    # Build clean header names
    clean_headers = []
    for h in headers:
        if h in ("email", "username", "user", "login"):
            clean_headers.append("username")
        else:
            clean_headers.append(h)

    data = []
    for row in rows[1:]:
        if all(cell is None for cell in row):
            continue
        entry = {}
        for i, cell in enumerate(row):
            if i < len(clean_headers):
                entry[clean_headers[i]] = str(cell) if cell is not None else ""
        if entry.get("username") and entry.get("password"):
            data.append(entry)

    wb.close()
    return data
