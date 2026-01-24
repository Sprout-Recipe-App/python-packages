from time import time


class FileSystemState:
    def __init__(self) -> None:
        self._last_saved_file = None
        self._save_next_modified_file = False
        self._last_event_time = {}
        self.event_cooldown = 5

    @property
    def last_saved_file(self):
        return self._last_saved_file

    def set_save_next_modified_file(self):
        self._save_next_modified_file = True

    @property
    def should_save_next_modified_file(self):
        return self._save_next_modified_file

    def save_file(self, file_path):
        self._last_saved_file, self._save_next_modified_file = file_path, False

    def clear_last_saved_file(self):
        self._last_saved_file = None

    def has_cooldown_active(self, file_path):
        return time() - self._last_event_time.get(file_path, 0) < self.event_cooldown

    def record_event(self, file_path):
        self._last_event_time[file_path] = time()
