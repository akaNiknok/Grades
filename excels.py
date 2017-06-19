import os
import openpyxl
from openpyxl.utils import range_boundaries


def read_excels(grade, section, cn):
    """Return format:
        subjects = {
            "Subject": {
                "Trimester": {
                    "Test": (int(Student Score), int(Total Score))
                }
            }
        }
    """

    # Rows for label and total score
    TEST_LABEL_ROW = 7
    TEST_TOTAL_ROW = 8

    # Get file directory using users grade and section
    filedir = "excels/{}/{}/".format(grade, section)

    # Get all files (subjects) in file directory
    try:
        files = os.listdir(filedir)
    except OSError:
        return None

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

                    # Get CN rows
                    user_row = cn + 8

                    Tests = {}

                    # Store tests in dictionary
                    for col in range(3, ws.max_column):

                        test_label = ws.cell(row=TEST_LABEL_ROW,
                                             column=col).value
                        student_score = ws.cell(row=user_row,
                                                column=col).value
                        total_score = ws.cell(row=TEST_TOTAL_ROW,
                                              column=col).value

                        # Only include scores with label
                        if ((test_label not in (None, "TS", "PS", "EP"))
                                and (student_score is not None)):

                            if test_label in Tests:
                                Tests[test_label][0] += student_score
                                Tests[test_label][1] += total_score
                            else:
                                Tests[test_label] = [student_score,
                                                     total_score]

                    # Store the test in trimester
                    # Also remove "Raw.Score-" from the sheet title
                    trimesters[ws.title.split("-")[1]] = Tests

            # Store the trimester in subject
            # Also removes the file extension
            subjects[os.path.splitext(file)[0]] = trimesters

    return subjects


def read_excel(grade, section, subject):
    """Reads an excel file and returns a table list"""

    # Open excel file
    wb = openpyxl.load_workbook("excels/{}/{}/{}".format(grade,
                                                         section,
                                                         subject + ".xlsx"),
                                data_only=True)

    # Open the sheet (subject to change)
    ws = wb.worksheets[0]

    # Get boundaries (min_col, min_row, max_col, max_row) of merged_cells
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

                new_row.append((value, colspan))

                # If cell is merged, skip (colspan - 1) iterations
                if colspan != 1:
                    for x in range(colspan - 1):
                        next(columns)
            else:
                new_row.append(("", 1))

        table.append(new_row)

    return table
