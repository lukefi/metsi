import itertools
import math
import re


# Floats not adjacent to letters (so 'm3/ha' won't be parsed as 3)
_NUM_RE = re.compile(r'(?<![A-Za-z])[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?(?![A-Za-z])')

def _split_text_and_numbers(s: str):
    """Return [("text", str) or ("num", float), ...] segments from a string."""
    parts = []
    last = 0
    for m in _NUM_RE.finditer(s):
        if m.start() > last:
            parts.append(("text", s[last:m.start()]))
        parts.append(("num", float(m.group())))
        last = m.end()
    if last < len(s):
        parts.append(("text", s[last:]))
    return parts

def _compare_mixed_segment(a: str, b: str, line_num: int, abs_tol: float, rel_tol: float):
    """
    Compare a single 'column' that may contain mixed text and numbers.
    Raises AssertionError on mismatch.
    """
    a_parts = _split_text_and_numbers(a)
    b_parts = _split_text_and_numbers(b)

    if len(a_parts) != len(b_parts):
        raise AssertionError(
            f"Line {line_num}: segment count differs in mixed text column "
            f"({len(a_parts)} vs {len(b_parts)}).\nGot:      {a!r}\nExpected: {b!r}"
        )

    num_idx = 0
    for (ak, av), (bk, bv) in zip(a_parts, b_parts):
        if ak != bk:
            raise AssertionError(
                f"Line {line_num}: segment kind differs (got {ak}, expected {bk}).\n"
                f"Got:      {a!r}\nExpected: {b!r}"
            )
        if ak == "text":
            if av != bv:
                raise AssertionError(
                    f"Line {line_num}: text differs.\nGot:      {a!r}\nExpected: {b!r}"
                )
        else:
            num_idx += 1
            if not math.isclose(av, bv, abs_tol=abs_tol, rel_tol=rel_tol):
                diff = abs(av - bv)
                raise AssertionError(
                    f"Line {line_num}, number {num_idx}: got {av}, expected {bv} "
                    f"(abs diff {diff}, abs_tol {abs_tol}, rel_tol {rel_tol})."
                )

def compare_files_with_numeric_in_text(file1_path, file2_path, abs_tol_str, rel_tol_str="0.0"):
    """
    NEW keyword: like compare_numeric_files_with_tolerance, but if a column
    isn't a pure float it will compare the text exactly and any numbers inside
    the text using abs/rel tolerances.

    Args:
        file1_path (str): path to test file
        file2_path (str): path to reference file
        abs_tol_str (str): absolute tolerance, e.g. "1.0"
        rel_tol_str (str): relative tolerance, e.g. "1e-4"
    """
    try:
        abs_tol = float(abs_tol_str)
        rel_tol = float(rel_tol_str)
    except ValueError:
        raise AssertionError(f"Invalid tolerance values: abs={abs_tol_str!r}, rel={rel_tol_str!r}")

    with open(file1_path) as f1, open(file2_path) as f2:
        for line_num, (line1, line2) in enumerate(itertools.zip_longest(f1, f2, fillvalue=None), 1):
            if line1 is None:
                raise AssertionError(f"File '{file1_path}' is shorter than reference '{file2_path}'.")
            if line2 is None:
                raise AssertionError(f"File '{file1_path}' is longer than reference '{file2_path}'.")

            vals1 = line1.rstrip("\n").split('\t')
            vals2 = line2.rstrip("\n").split('\t')

            if len(vals1) != len(vals2):
                raise AssertionError(
                    f"Line {line_num}: different number of columns ({len(vals1)} vs {len(vals2)})."
                )

            for col_num, (v1_str, v2_str) in enumerate(zip(vals1, vals2), 1):
                # First try pure-float comparison for speed/back-compat
                try:
                    n1 = float(v1_str); n2 = float(v2_str)
                except ValueError:
                    # Not pure numbers -> mixed comparison
                    _compare_mixed_segment(v1_str, v2_str, line_num, abs_tol, rel_tol)
                else:
                    if not math.isclose(n1, n2, abs_tol=abs_tol, rel_tol=rel_tol):
                        diff = abs(n1 - n2)
                        raise AssertionError(
                            f"Mismatch at Line {line_num}, Column {col_num}: "
                            f"Got '{v1_str}', expected '{v2_str}' "
                            f"(abs diff {diff}, abs_tol {abs_tol}, rel_tol {rel_tol})."
                        )

    print(f"Files '{file1_path}' and '{file2_path}' match within abs_tol={abs_tol} rel_tol={rel_tol}.")

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