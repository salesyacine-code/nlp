"""
downloader.py
=============
Activity I - Part 1: Automated JORADP Gazette PDF Downloader.
Ecole Militaire Polytechnique (EMP) - Natural Language Processing.

Downloads official Algerian legal gazettes (Journal Officiel de la
République Algérienne Démocratique et Populaire - JORADP) in French.
"""

from __future__ import annotations

import logging
import random
import time
from pathlib import Path
from typing import List, Optional

import requests

logger = logging.getLogger("activity_1.downloader")


class JORADPDownloader:
    """Automated downloader for JORADP legal gazette PDFs in French.

    Attributes:
        base_url_template (str): Formattable URL template for French gazette PDFs.
        headers (dict): Standard HTTP request headers mimicking a legitimate browser.
        min_size_bytes (int): Minimum acceptable file size (to exclude HTTP error redirects/stubs).
        throttle_range (tuple[float, float]): (min_seconds, max_seconds) pause between network requests.
    """

    BASE_URL_TEMPLATE: str = (
        "https://www.joradp.dz/FTP/jo-francais/{year}/F{year}{issue_num:03d}.pdf"
    )

    DEFAULT_HEADERS: dict[str, str] = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/pdf,application/xhtml+xml,text/html;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
    }

    def __init__(
        self,
        output_dir: Path | str = Path("activity_1/raw_pdfs"),
        min_size_bytes: int = 10 * 1024,  # 10 KB
        throttle_range: tuple[float, float] = (0.3, 0.5),
        timeout: int = 20,
    ) -> None:
        """Initialize the downloader with configurable target directory and network parameters."""
        self.output_dir: Path = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.min_size_bytes: int = min_size_bytes
        self.throttle_range: tuple[float, float] = throttle_range
        self.timeout: int = timeout
        self.session: requests.Session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

    def _is_valid_pdf_file(self, file_path: Path) -> bool:
        """Check if a file exists, meets minimum size, and starts with the PDF magic header."""
        if not file_path.is_file() or file_path.stat().st_size < self.min_size_bytes:
            return False
        try:
            with open(file_path, "rb") as f:
                header = f.read(5)
                return header.startswith(b"%PDF-")
        except OSError:
            return False

    def download_issue(
        self, year: int, issue_num: int, max_retries: int = 2
    ) -> Optional[Path]:
        """Download a single gazette PDF by year and issue number.

        Args:
            year: Four-digit publication year (e.g., 2024).
            issue_num: Sequential issue number (e.g., 1 for F2024001.pdf).
            max_retries: Number of retry attempts on connection error.

        Returns:
            Path to downloaded/existing PDF file, or None if download failed.
        """
        filename = f"F{year}{issue_num:03d}.pdf"
        target_path = self.output_dir / filename
        url = self.BASE_URL_TEMPLATE.format(year=year, issue_num=issue_num)

        # Idempotency check: reuse already downloaded valid PDF
        if self._is_valid_pdf_file(target_path):
            logger.info("[Cached] %s already exists and is valid (%d bytes).", filename, target_path.stat().st_size)
            return target_path

        for attempt in range(1, max_retries + 1):
            try:
                # Polite throttle delay
                delay = random.uniform(*self.throttle_range)
                time.sleep(delay)

                logger.info("Fetching issue #%03d from: %s (attempt %d/%d)", issue_num, url, attempt, max_retries)
                response = self.session.get(url, timeout=self.timeout, stream=True)

                if response.status_code != 200:
                    logger.warning("Issue #%03d returned HTTP status %d. Skipping.", issue_num, response.status_code)
                    return None

                content_type = response.headers.get("Content-Type", "").lower()
                # Accept PDF content types or generic binary streams
                if "application/pdf" not in content_type and "octet-stream" not in content_type:
                    logger.warning("Issue #%03d returned unexpected Content-Type '%s'. Skipping.", issue_num, content_type)
                    return None

                # Stream content to temporary file before atomic rename
                temp_path = self.output_dir / f"{filename}.part"
                downloaded_size = 0
                with open(temp_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=16384):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)

                # Validate downloaded payload
                if downloaded_size < self.min_size_bytes or not self._is_valid_pdf_file(temp_path):
                    logger.warning(
                        "Downloaded file %s rejected: size %d bytes (< %d threshold) or invalid PDF header.",
                        filename,
                        downloaded_size,
                        self.min_size_bytes,
                    )
                    if temp_path.exists():
                        temp_path.unlink()
                    return None

                # Atomically replace final file
                if target_path.exists():
                    target_path.unlink()
                temp_path.rename(target_path)
                logger.info("Successfully downloaded %s (%.2f KB).", filename, downloaded_size / 1024)
                return target_path

            except requests.exceptions.RequestException as exc:
                logger.warning("Network error on issue #%03d (attempt %d): %s", issue_num, attempt, exc)
                if attempt == max_retries:
                    logger.error("Failed to download issue #%03d after %d attempts.", issue_num, max_retries)
                    return None

        return None

    def download_consecutive_issues(
        self, year: int = 2024, count: int = 50, start_issue: int = 1, max_consecutive_misses: int = 5
    ) -> List[Path]:
        """Download `count` valid PDF gazettes starting from `start_issue`.

        If an individual issue number is skipped or missing in the archive, it continues
        probing subsequent issue numbers until `count` documents have been collected.

        Args:
            year: Publication year.
            count: Total number of valid PDF documents required (default 50).
            start_issue: Initial issue number to start probe (default 1).
            max_consecutive_misses: Safety threshold to abort if archive has ended.

        Returns:
            List of Paths to successfully acquired PDF files.
        """
        downloaded_paths: List[Path] = []
        current_issue: int = start_issue
        consecutive_misses: int = 0

        logger.info(
            "Starting automated collection of %d legal gazettes for year %d (start_issue=%d).",
            count,
            year,
            start_issue,
        )

        while len(downloaded_paths) < count and consecutive_misses < max_consecutive_misses:
            pdf_path = self.download_issue(year=year, issue_num=current_issue)
            if pdf_path is not None:
                downloaded_paths.append(pdf_path)
                consecutive_misses = 0
            else:
                consecutive_misses += 1
                logger.info(
                    "Missing issue #%03d (consecutive misses: %d/%d).",
                    current_issue,
                    consecutive_misses,
                    max_consecutive_misses,
                )

            current_issue += 1

        logger.info(
            "Collection finished. Total valid documents gathered: %d/%d.",
            len(downloaded_paths),
            count,
        )
        return downloaded_paths


def download_gazettes(
    year: int = 2024,
    count: int = 50,
    output_dir: Path | str = Path("activity_1/raw_pdfs"),
) -> List[Path]:
    """Convenience functional wrapper for downloader component."""
    downloader = JORADPDownloader(output_dir=output_dir)
    return downloader.download_consecutive_issues(year=year, count=count)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    download_gazettes(year=2024, count=5)

