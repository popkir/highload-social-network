import time

from app.utils.logger import logger


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class Timer:
    def __init__(self, corr_id: str = ""):
        self._start_time = time.perf_counter()
        self.corr_id = corr_id

    def restart(self):
        """Start/Restart a new timer"""
        self._start_time = time.perf_counter()

    def get_elapsed_time_sec(self):
        return time.perf_counter() - self._start_time

    def print_elapsed_time(self, command: str):
        """report the elapsed time"""
        elapsed_time = time.perf_counter() - self._start_time
        log_str = f"Elapsed time for {command}: {elapsed_time:0.4f} seconds"
        if len(self.corr_id) > 0:
            log_str += f", corr_id: {self.corr_id}"
        logger.info(log_str)

    def restart_and_print_elapsed_time(self, command: str):
        """stop and report the elapsed time"""
        self.print_elapsed_time(command=command)
        self.restart()

    def print_elapsed_time_ops(self, command: str, count: int):
        """report the elapsed time"""
        elapsed_time = time.perf_counter() - self._start_time
        if elapsed_time != 0 and count != 0:
            log_str = f"Elapsed time for ({command}, count: {count}): {elapsed_time:0.4f} seconds, op/sec = {(count/elapsed_time):0.4f}"
        else:
            log_str = f"Elapsed time for ({command}, count: {count}): {elapsed_time:0.4f} seconds, op/sec = undefined"
        if len(self.corr_id) > 0:
            log_str += f", corr_id: {self.corr_id}"
        logger.info(log_str)

    def restart_and_print_elapsed_time_ops(self, command: str, count: int):
        """Stop the timer, and report the elapsed time"""
        self.print_elapsed_time_ops(command=command, count=count)
        self.restart()
