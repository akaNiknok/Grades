import os
import openpyxl
from openpyxl.utils import range_boundaries


def read_excels(grade, section, cn):
    """Read excels of every subject of a student and returns a table list
    Return format:
        subjects = {
            "Subject":
                "Trimester": [[col]]
        }"""

    # Get file directory using users grade and section
    filedir = "excels/{}/{}/".format(grade, section)

    # Get all files (subjects) in file directory
    try:
        files = os.listdir(filedir)
    except OSError:
        return "Empty"

    subjects = {}

    # Loop per subject
    for file in files:

        # Only read .xslx
        if file.endswith(".xlsx"):

            # Open the excel file
            wb = openpyxl.load_workbook(os.path.join(filedir, file),
                                        data_only=True)

            trimesters = {}

            # Loop through sheets
            for ws in wb.worksheets:

                if "Raw.Score" in ws.title:

                    # Get boundary (min_col, min_row, max_col, max_row)
                    # of merged_cells
                    merged_cells = [range_boundaries(r)
                                    for r in ws.merged_cell_ranges]

                    table = []

                    # Loop through rows
                    for row in range(5, ws.max_row):

                        # Store the labels
                        if row in (5, 6, 7, 8):

                            # Contains columns (value, colspan) here
                            new_row = []

                            # Create an iterator object to skip merged cells
                            columns = iter(range(1, ws.max_column))

                            # Loop through columns
                            for column in columns:

                                value = ws.cell(row=row, column=column).value

                                # Check if the cell is not empty
                                if value is not None:
                                    colspan = 1

                                    # Check if cell is merged
                                    for r in merged_cells:
                                        if (r[0] == column) and (r[1] == row):
                                            # Add to colspan
                                            colspan += (r[2] - r[0])
                                            break

                                    new_row.append((value, colspan))

                                    # If cell is merged,
                                    # skip (colspan - 1) iterations
                                    if colspan != 1:
                                        for x in range(colspan - 1):
                                            next(columns)
                                else:
                                    new_row.append(("", 1))

                            table.append(new_row)

                        # Store users score
                        elif ws.cell(row=row, column=1).value == cn:

                            # Contains columns (value, colspan) here
                            new_row = []

                            # Loop through columns
                            for column in range(1, ws.max_column):

                                value = ws.cell(row=row, column=column).value

                                # Check if the cell is not empty
                                if value is not None:
                                    new_row.append((value, 1))
                                else:
                                    new_row.append(("", 1))

                            table.append(new_row)

                    trimesters[ws.title.split("-")[1]] = table

            subjects[os.path.splitext(file)[0]] = trimesters

    return subjects


def read_excel(grade, section, subject):
    """Reads an excel file and returns a table list"""

    # Open excel file
    wb = openpyxl.load_workbook("excels/{}/{}/{}".format(grade,
                                                         section,
                                                         subject + ".xlsx"),
                                data_only=True)

    trimesters = {}

    # Loop through sheets
    for ws in wb.worksheets:

        if "Raw.Score" in ws.title:

            # Get boundary (min_col, min_row, max_col, max_row) of merged_cells
            merged_cells = [range_boundaries(r) for r in ws.merged_cell_ranges]

            table = []

            # Loop through rows
            for row in range(5, ws.max_row):

                # Contains columns (value, colspan) here
                new_row = []

                # Create an iterator object to be able to skip merged cells
                columns = iter(range(1, ws.max_column))

                # Loop through columns
                for column in columns:

                    # Get value of cell
                    value = ws.cell(row=row, column=column).value

                    # Check if the cell is not empty
                    if value is not None:
                        colspan = 1

                        # Check if cell is merged
                        for r in merged_cells:
                            if (r[0] == column) and (r[1] == row):
                                colspan += (r[2] - r[0])  # Add to colspan
                                break

                        # Append column's row and colspan to row
                        new_row.append((value, colspan))

                        # If cell is merged, skip (colspan - 1) iterations
                        if colspan != 1:
                            for x in range(colspan - 1):
                                next(columns)
                    else:
                        new_row.append(("", 1))

                # Appen row to table
                table.append(new_row)

            # Store the table in the trimesters dictionary
            trimesters[ws.title.split("-")[1]] = table

    return trimesters
