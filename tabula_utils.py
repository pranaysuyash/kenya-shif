"""
Tabula utilities for Streamlit Cloud compatibility.
Provides Java environment setup and subprocess-based tabula extraction.
"""

import os
import glob
import shutil
import subprocess
import shlex


def setup_java_env():
    """
    Set up Java environment for Streamlit Cloud.
    Detects JAVA_HOME and ensures java is on PATH.
    """
    # If JAVA_HOME not set, try to detect it
    if "JAVA_HOME" not in os.environ:
        # Common Debian/Ubuntu OpenJDK install paths on Streamlit Cloud
        candidates = sorted(glob.glob("/usr/lib/jvm/*-openjdk-*"), reverse=True)
        for candidate in candidates:
            if glob.glob(f"{candidate}/lib/server/libjvm.so"):
                os.environ["JAVA_HOME"] = candidate
                break

    # Ensure 'java' is on PATH even if JAVA_HOME not set perfectly
    if shutil.which("java") is None and "JAVA_HOME" in os.environ:
        java_bin_path = os.path.join(os.environ["JAVA_HOME"], "bin")
        os.environ["PATH"] = os.environ["PATH"] + os.pathsep + java_bin_path

    # Keep Java headless and memory-bounded for Streamlit Cloud
    os.environ.setdefault("JAVA_TOOL_OPTIONS", "-Xmx512m -Djava.awt.headless=true")


def cmd_out(cmd):
    """
    Run a command and return its output, or error message.
    Used for Java health checks.
    """
    try:
        return subprocess.check_output(
            shlex.split(cmd),
            stderr=subprocess.STDOUT,
            text=True
        ).strip()
    except Exception as e:
        return f"ERR: {e}"


def tabula_read(pdf_path, pages, lattice=True, pandas_header=None):
    """
    Read PDF tables using tabula-py with subprocess mode for Streamlit Cloud compatibility.

    Args:
        pdf_path: Path to PDF file
        pages: Page specification (e.g., "1-18", "19-54")
        lattice: Whether to use lattice mode (default True)
        pandas_header: Header row specification for pandas

    Returns:
        List of DataFrames, or empty list if extraction fails
    """
    try:
        import tabula
        return tabula.read_pdf(
            pdf_path,
            pages=pages,
            lattice=lattice,
            multiple_tables=True,
            pandas_options={"header": pandas_header},
            java_options=["-Djava.awt.headless=true", "-Xmx512m"],
            force_subprocess=True  # Critical for Streamlit Cloud
        ) or []
    except Exception as e:
        print(f"Tabula extraction failed: {e}")
        return []


def safe_extract_tables(pdf_path, pages_tables="19-54", pages_text="1-18"):
    """
    Extract tables with multiple fallbacks for maximum reliability.

    Returns:
        tuple: (list_of_dataframes, backend_used)
    """
    backend_used = "none"

    # 1) Try tabula first (preferred when Java available)
    try:
        dfs = tabula_read(pdf_path, pages=pages_tables)
        if dfs and any(len(df) for df in dfs):
            return dfs, "tabula"
    except Exception as e:
        print(f"Tabula fallback failed: {e}")

    # 2) Try Camelot lattice mode
    try:
        import camelot
        tables = camelot.read_pdf(pdf_path, pages=pages_tables, flavor="lattice")
        if tables and tables.n > 0:
            return [t.df for t in tables], "camelot_lattice"
    except Exception as e:
        print(f"Camelot lattice fallback failed: {e}")

    # 3) Try Camelot stream mode
    try:
        import camelot
        tables = camelot.read_pdf(pdf_path, pages=pages_tables, flavor="stream")
        if tables and tables.n > 0:
            return [t.df for t in tables], "camelot_stream"
    except Exception as e:
        print(f"Camelot stream fallback failed: {e}")

    # 4) Final fallback to pdfplumber
    try:
        import pdfplumber
        dfs = []
        with pdfplumber.open(pdf_path) as pdf:
            for pnum in parse_page_range(pages_tables, len(pdf.pages)):
                page = pdf.pages[pnum-1]
                for table in page.extract_tables() or []:
                    import pandas as pd
                    dfs.append(pd.DataFrame(table))
        if dfs and any(len(df) for df in dfs):
            return dfs, "pdfplumber"
    except Exception as e:
        print(f"pdfplumber fallback failed: {e}")

    return [], "none"


def parse_page_range(spec, n_pages):
    """
    Parse page range specification like "1-18", "19-54", "all".
    """
    if spec == "all":
        return range(1, n_pages + 1)

    parts = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if "-" in chunk:
            start, end = chunk.split("-", 1)
            parts.extend(range(int(start), int(end) + 1))
        else:
            parts.append(int(chunk))
    return parts


def safe_max(iterable, default=None):
    """Return max of iterable, or default if empty."""
    try:
        return max(iterable)
    except ValueError:
        return default


def safe_min(iterable, default=None):
    """Return min of iterable, or default if empty."""
    try:
        return min(iterable)
    except ValueError:
        return default