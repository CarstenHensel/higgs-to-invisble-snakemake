#!/usr/bin/env python3
"""
slcio2edm4hep_crawler.py

Recursively crawl through a given root directory, find all .slcio files,
convert them into edm4hep .root files using:

    check_missing_cols --minimal input.slcio > patch.txt
    lcio2edm4hep input.slcio output.root patch.txt

Validation:
- The converted .root file is checked with edm4hep-dump (or rootls as fallback).
- Only if validation succeeds, the original .slcio file is deleted.

Features:
- Suppresses normal tool output for speed
- Per-file .log capturing warnings/errors from lcio2edm4hep
- Deletes .slcio files after successful validation
- Dry-run mode (shows what would be done without executing commands)
- Logging to both console and a file (slcio2edm4hep.log)

Usage:
    source /cvmfs/sw.hsf.org/key4hep/setup.sh -r 2025-01-28
    python3 slcio2edm4hep_crawler.py /path/to/rootdir [--dry-run]

    or better, use nohup to keep the job running if connection fails:
    nohup python3 slcio2edm4hep_crawler.py /path/to/rootdir [--dry-run] > convert.out 2>&1 &
"""

import argparse
import logging
import subprocess
import shutil
from pathlib import Path

def setup_logging():
    logger = logging.getLogger("slcio2edm4hep")
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)

    fh = logging.FileHandler("slcio2edm4hep.log", mode="w")
    fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(fh)

    return logger

def validate_root_file(root_file: Path, logger) -> bool:
    """Check if the ROOT file is valid using edm4hep-dump or rootls."""
    if not root_file.exists() or root_file.stat().st_size == 0:
        logger.error(f"Validation failed: {root_file} is missing or empty.")
        return False

    try:
        subprocess.run(
            ["edm4hep-dump", str(root_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        logger.info(f"Validation OK: {root_file}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # fallback: try rootls
        try:
            subprocess.run(
                ["rootls", str(root_file)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            logger.info(f"Validation OK (via rootls): {root_file}")
            return True
        except Exception as e:
            logger.error(f"Validation failed for {root_file}: {e}")
            return False

def convert_file(slcio_file: Path, dry_run: bool, logger):
    root_file = slcio_file.with_suffix(".root")
    patch_file = slcio_file.parent / "patch.txt"
    edm4hep_dir = slcio_file.parent / "edm4hep"
    edm4hep_dir.mkdir(exist_ok=True)

    logger.info(f"Converting: {slcio_file}")
    logger.info(f" → Output: {edm4hep_dir / root_file.name}")

    if dry_run:
        return

    # Per-file error log
    err_log = slcio_file.with_suffix(".log")

    # Step 1: run check_missing_cols
    with patch_file.open("w") as pf:
        subprocess.run(
            ["check_missing_cols", "--minimal", str(slcio_file)],
            stdout=pf,
            stderr=subprocess.DEVNULL,
            check=True,
        )

    # Step 2: run lcio2edm4hep
    with open(err_log, "w") as elog:
        subprocess.run(
            ["lcio2edm4hep", str(slcio_file), str(root_file), str(patch_file)],
            stdout=subprocess.DEVNULL,
            stderr=elog,
            check=True,
        )

    # Step 3: move .root file to edm4hep dir
    final_root = edm4hep_dir / root_file.name
    shutil.move(str(root_file), final_root)

    # Step 4: validate
    if validate_root_file(final_root, logger):
        # Step 5: delete original slcio
        slcio_file.unlink()
        logger.info(f"Deleted original: {slcio_file}")
    else:
        logger.warning(f"Keeping .slcio since validation failed: {slcio_file}")

def crawl_and_convert(root_dir: Path, dry_run: bool, logger):
    for slcio_file in root_dir.rglob("*.slcio"):
        try:
            convert_file(slcio_file, dry_run, logger)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error processing {slcio_file}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error with {slcio_file}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Convert .slcio files to edm4hep .root files.")
    parser.add_argument("rootdir", type=Path, help="Root directory to start crawling from")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without executing them")
    args = parser.parse_args()

    logger = setup_logging()
    logger.info("Starting SLCIO → EDM4hep conversion")
    logger.info(f"Root directory: {args.rootdir}")
    logger.info(f"Dry-run mode: {args.dry_run}")

    crawl_and_convert(args.rootdir, args.dry_run, logger)

    logger.info("Finished.")

if __name__ == "__main__":
    main()
