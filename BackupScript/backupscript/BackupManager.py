#!/usr/bin/env python3

"""MyRsyncBackup."""

import os
import sys
import subprocess
from datetime import datetime, timedelta
import logging
import argparse
from typing import Optional


class BackupManager:
    def __init__(self, directory_map: dict, interval: timedelta) -> None:
        self.directory_map = directory_map
        self.interval = interval
        logging.basicConfig(
            filename="backup.log",
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
        )

    def _get_backup_directory(self, base_dir: str) -> Optional[str]:
        backup_dirs = os.listdir(base_dir)
        current_time = datetime.now()
        threshold_time = current_time - self.interval
        backup_dirs.sort(reverse=True)
        for backup_dir in backup_dirs:
            if backup_dir.startswith("backup#"):
                backup_time = datetime.strptime(
                    backup_dir.split("#")[1], "%Y-%m-%d_%H-%M-%S"
                )
                if backup_time > threshold_time:
                    return os.path.join(base_dir, backup_dir)

        return None

    def fullBackup(self) -> None:
        for source_dir, backup_base_dir in self.directory_map.items():
            backup_dir = os.path.join(
                backup_base_dir,
                f"backup#{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}",
            )
            self._run_rsync(source_dir, backup_dir)

    def incrementalBackup(self) -> None:
        for source_dir, backup_base_dir in self.directory_map.items():
            backup_dir = self._get_backup_directory(backup_base_dir)
            if backup_dir is None:
                self.fullBackup()
            else:
                self._run_rsync(source_dir, backup_dir)
                self._log_backup(backup_base_dir, backup_dir)

    def _log_backup(self, backup_base_dir: str, backup_dir: str) -> None:
        log_file_name = os.path.basename(backup_dir) + ".log"
        log_file_path = os.path.join(backup_base_dir, log_file_name)
        with open(log_file_path, "a") as log_file:
            log_file.write(
                f'Backup performed at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
            )

    def _run_rsync(self, source_dir: str, backup_dir: str) -> None:
        rsync_process = subprocess.run(["rsync", "-avz", source_dir, backup_dir])
        if rsync_process.returncode != 0:
            logging.error(f"Backup failed. Return code: {rsync_process.returncode}")


def main():
    parser = argparse.ArgumentParser(
        description="BackupScript: A simple incremental and full backup script."
    )
    parser.add_argument(
        "-d", "--days", type=int, help="Specify the interval in days for the backup."
    )
    parser.add_argument(
        "-m",
        "--months",
        type=int,
        help="Specify the interval in months for the backup.",
    )
    parser.add_argument(
        "-f", "--full", action="store_true", help="Perform a full backup."
    )
    parser.add_argument(
        "-i",
        "--incremental",
        action="store_true",
        default=True,
        help="Perform an incremental backup. This is the default action.",
    )
    parser.add_argument(
        "--src", required=True, help="Specify the source directory for the backup."
    )
    parser.add_argument(
        "--dst", required=True, help="Specify the backup directory for the backup."
    )
    args = parser.parse_args()

    if args.days and args.months:
        print("Error: Please specify either days or months, not both.")
        sys.exit(1)

    if args.days:
        interval = timedelta(days=args.days)
    elif args.months:
        interval = timedelta(days=args.months * 30)
    else:
        interval = timedelta(days=30)

    directory_map = {args.src: args.dst}

    bm = BackupManager(directory_map, interval)
    if args.full:
        bm.fullBackup()
    else:
        bm.incrementalBackup()


if __name__ == "__main__":
    main()
