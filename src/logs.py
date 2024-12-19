import os
import json
import time

class Logs:
    events_filename = '../logs/events.json'
    system_filename = '../logs/system.log'

    """
    Full log entries are passed as a dict rather than separated as arguments to keep this function open to all and any type of event logs.
    """
    def new_event_log(self, log) -> None:
        self.__check_incoming_events_log(log)
        self.__create_events_log_file()

        with open(self.events_filename) as events_file:
            try:
                events_file_json = json.load(events_file)
            except json.JSONDecodeError as err:
                raise ValueError(f"Invalid JSON in file {self.events_filename}: {err}")

        if not events_file_json.get('events'):
            events_file_json['events'] = []

        events_file_json['events'].append(log)
        self.__update_json_file(self.events_filename, events_file_json)

    def __check_incoming_events_log(self, log) -> None:
        if not log.get('timestamp'):
            raise KeyError("No timestamp provided in event log")
        if not log.get('event_type'):
            raise KeyError("No event_type provided in event log")

    def __create_events_log_file(self) -> None:
        if not os.path.exists(self.events_filename) or os.stat(self.events_filename).st_size == 0:
            self.__update_json_file(self.events_filename, {"events": []})

    def __update_json_file(self, filename, json_content) -> None:
        try:
            with open(filename, 'w') as file:
                json.dump(json_content, file, indent=4)
        except (IOError, OSError) as err:
            raise RuntimeError(f"An error occurred while trying to write to the file {filename}: {err}")
        except (TypeError, json.JSONDecodeError) as err:
            raise ValueError(f"An error occurred while serializing the content to JSON for {filename}: {err}")

    def new_system_log(self, message, is_error = False) -> None:
        self.__create_systems_log_file()
        with open(self.system_filename, 'a') as file:
            file.write(f"{time.ctime()}: {'[ERR]' if is_error else '[LOG]'} - {message}\n")

    def __create_systems_log_file(self) -> None:
        if not os.path.exists(self.system_filename):
            open(self.system_filename, "x")

    def clear_event_logs(self) -> None:
        open(self.events_filename, 'w').close()
        self.__create_events_log_file()

    def clear_system_logs(self) -> None:
        open(self.system_filename, 'w').close()