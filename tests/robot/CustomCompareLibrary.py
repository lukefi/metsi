import itertools

def compare_numeric_files_with_tolerance(file1_path, file2_path, tolerance_str):
    """
    Compares two text files line-by-line and value-by-value with a numeric tolerance.

    This is much faster than doing the loops inside Robot Framework.

    Args:
        file1_path (str): Path to the first file.
        file2_path (str): Path to the second (reference) file.
        tolerance_str (str): The tolerance for float comparison, as a string (e.g., "0.01").

    Raises:
        AssertionError: If files do not match within the tolerance.
    """
    try:
        tolerance = float(tolerance_str)
    except ValueError:
        raise AssertionError(f"Invalid tolerance value: '{tolerance_str}'")

    with open(file1_path) as f1, open(file2_path) as f2:
        # Use zip_longest to handle files with different line counts
        for line_num, (line1, line2) in enumerate(itertools.zip_longest(f1, f2, fillvalue=None), 1):

            if line1 is None:
                raise AssertionError(f"File '{file1_path}' is shorter than reference file '{file2_path}'.")
            if line2 is None:
                raise AssertionError(f"File '{file1_path}' is longer than reference file '{file2_path}'.")

            vals1 = line1.strip().split('\t')
            vals2 = line2.strip().split('\t')

            if len(vals1) != len(vals2):
                raise AssertionError(
                    f"Line {line_num}: Different number of columns. "
                    f"Got {len(vals1)}, expected {len(vals2)}."
                )

            for col_num, (v1_str, v2_str) in enumerate(zip(vals1, vals2), 1):
                try:
                    # Try to compare as numbers first
                    num1 = float(v1_str)
                    num2 = float(v2_str)
                    if not abs(num1 - num2) <= tolerance:
                        raise AssertionError(
                            f"Mismatch at Line {line_num}, Column {col_num}: "
                            f"Got '{v1_str}', expected '{v2_str}' (tolerance: {tolerance})."
                        )
                except ValueError:
                    # If they are not numbers (e.g., headers), compare as strings
                    if v1_str != v2_str:
                        raise AssertionError(
                            f"Mismatch at Line {line_num}, Column {col_num}: "
                            f"Got text '{v1_str}', expected text '{v2_str}'."
                        )

    # If we get here, the files match
    print(f"Files '{file1_path}' and '{file2_path}' match within tolerance {tolerance}.")