import logging
import threading
import time
from pathlib import Path

LOG_DIR = Path("logs")


def _monitor(log_dir: Path, stop: threading.Event) -> None:
    """
    Continuously monitors `.log` files in the specified directory for new lines containing error indicators.
    
    Scans each log file for appended lines with the keywords "ERROR" or "Exception" and logs a message when such lines are detected. The function tracks the last read position for each file to avoid reprocessing old content and runs until the provided stop event is set.
    """
    positions: dict[Path, int] = {}
    log_dir.mkdir(exist_ok=True)
    while not stop.is_set():
        for path in log_dir.glob("*.log"):
            last_pos = positions.get(path, 0)
            if path.exists() and path.stat().st_size > last_pos:
                with path.open() as f:
                    f.seek(last_pos)
                    for line in f:
                        if any(w in line for w in ("ERROR", "Exception")):
                            logging.error("Log monitor detected issue: %s", line.strip())
                    positions[path] = f.tell()
        time.sleep(2)


def start_log_monitor() -> threading.Event:
    """
    Start a background thread to monitor log files in the predefined log directory for error entries.
    
    Returns:
        threading.Event: An event object that can be set to stop the log monitoring thread.
    """
    stop = threading.Event()
    thread = threading.Thread(target=_monitor, args=(LOG_DIR, stop), daemon=True)
    thread.start()
    return stop
