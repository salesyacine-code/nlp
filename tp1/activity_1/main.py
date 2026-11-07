"""
main.py
=======
Activity I: Legal Texts Extraction from JORADP & Diagnostic Audit.
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.
Instructor: Dr. M'hamed MATAOUI.

Single entrypoint executing:
  1. Automated download of 50 consecutive French legal gazette PDFs from JORADP.
  2. Page-by-page text extraction into UTF-8 files with layout boundary markers.
  3. Programmatic diagnostics analyzer detecting and logging PDF extraction problems.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict

# Ensure local imports work whether run from repo root or package dir
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from downloader import JORADPDownloader
from extractor import PDFTextExtractor
from diagnostics import CorpusDiagnosticsAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("activityOne")


def activityOne(
    year: int = 2024,
    count: int = 50,
    start_issue: int = 1,
    force_reextract: bool = False,
    base_dir: Path = CURRENT_DIR,
) -> Dict[str, Any]:
    """Execute Activity I pipeline end-to-end.

    Naming conforms to the EMP NLP Lab 1 specification:
    'Developed functions must be named by the question number: activityOne, activityTwo...'

    Args:
        year: Target publication year on JORADP (default 2024).
        count: Target number of consecutive valid gazettes (default 50).
        start_issue: Initial issue number to probe (default 1).
        force_reextract: Re-extract text even if target .txt file already exists.
        base_dir: Root directory for Activity I files.

    Returns:
        Dictionary containing pipeline results, file paths, and diagnostic metrics.
    """
    raw_pdfs_dir = base_dir / "raw_pdfs"
    extracted_texts_dir = base_dir / "extracted_texts"
    reports_dir = base_dir / "reports"
    report_file = reports_dir / "extraction_diagnostics_report.txt"

    print("\n" + "=" * 80)
    print(f" EMP NLP LAB 1 - ACTIVITY I: JORADP COLLECTION & TEXT EXTRACTION PIPELINE")
    print(f" Target Year: {year} | Target Count: {count} gazette issues")
    print("=" * 80 + "\n")

    # ---------------------------------------------------------
    # STEP 1: Automated Download from JORADP
    # ---------------------------------------------------------
    print(">>> [STEP 1/3] Downloading legal gazettes from JORADP portal...")
    downloader = JORADPDownloader(
        output_dir=raw_pdfs_dir,
        min_size_bytes=10 * 1024,
        throttle_range=(0.3, 0.5),
        timeout=25,
    )
    downloaded_files = downloader.download_consecutive_issues(
        year=year, count=count, start_issue=start_issue
    )
    print(f"✔ Step 1 Complete: {len(downloaded_files)} PDF documents stored in {raw_pdfs_dir}\n")

    # ---------------------------------------------------------
    # STEP 2: Text Extraction via pypdf
    # ---------------------------------------------------------
    print(">>> [STEP 2/3] Extracting text page-by-page using pypdf...")
    extractor = PDFTextExtractor(
        input_dir=raw_pdfs_dir,
        output_dir=extracted_texts_dir,
    )
    extraction_summaries = extractor.extract_all(force_reextract=force_reextract)
    total_pages = sum(s.extracted_pages for s in extraction_summaries)
    total_chars = sum(s.total_characters for s in extraction_summaries)
    print(f"✔ Step 2 Complete: {len(extraction_summaries)} text files ({total_pages} pages, {total_chars:,} chars) in {extracted_texts_dir}\n")

    # ---------------------------------------------------------
    # STEP 3: Extraction Diagnostics Audit
    # ---------------------------------------------------------
    print(">>> [STEP 3/3] Running automated extraction anomaly diagnostics...")
    analyzer = CorpusDiagnosticsAnalyzer(text_dir=extracted_texts_dir)
    report = analyzer.run_and_save_report(report_path=report_file)

    # Print terminal summary
    formatted_summary = analyzer.format_text_report(report)
    print(formatted_summary)
    print(f"\n✔ Step 3 Complete: Full diagnostic report written to {report_file}")

    return {
        "downloaded_files": downloaded_files,
        "extraction_summaries": extraction_summaries,
        "report": report,
        "report_file": report_file,
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Activity I: Legal Texts Extraction from JORADP & Extraction Diagnostics"
    )
    parser.add_argument("--year", type=int, default=2024, help="JORADP publication year (default: 2024)")
    parser.add_argument("--count", type=int, default=50, help="Number of gazette issues to collect (default: 50)")
    parser.add_argument("--start", type=int, default=1, help="Starting issue number (default: 1)")
    parser.add_argument(
        "--force", action="store_true", help="Force re-extraction even if extracted text exists"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    activityOne(
        year=args.year,
        count=args.count,
        start_issue=args.start,
        force_reextract=args.force,
    )

