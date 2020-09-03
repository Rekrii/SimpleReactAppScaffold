import time
import threading
import sqlite3
from datetime import datetime

import logger
import constants


class db_base:

    def __init__(self, name):
        self.name = name
        # Log for general activity
        self.log = logger.logger("db_" + name)
        # Log for each command that gets executed, this gets big
        self.call_log = logger.logger("db_" + name + "_calls")

        self.use_call_log = constants.db_use_call_log

        self.date_today = ""

        self.queue = []
        self.queue_running = False
        self.is_reading = False

        # Large last_command, so the timeout doesn't immediately expire
        self.last_command = 2545273778
        self.idle_timeout = constants.db_idle_timeout

    def add_col(self, table, col_name, col_type):
        if not self.has_col(table, col_name):
            cmd = "ALTER TABLE {} ADD COLUMN {} {}".format(
                simple_sqlsafe_str(table),
                simple_sqlsafe_str(col_name),
                simple_sqlsafe_str(col_type)
            )
            try:
                # Create the queue_cmd, stick in a queue_item, then queue it
                self.queue_command(queue_item(queue_cmd(cmd)))
            except Exception:
                pass

    def has_col(self, table, col_name):
        cmd = 'PRAGMA TABLE_INFO({})'.format(
            simple_sqlsafe_str(table))

        # Create the queue item with a cmd and return type
        qi = queue_item(queue_cmd(cmd), queue_item.return_type_raw)
        result = self.queue_command(qi)

        # With the col name, check if it matches the target name
        for col in result:
            if col['name'] == col_name:
                return True
        return False

    def queue_command(self, cmd):
        # Just make sure there queue is running, if it's not already
        if not self.queue_running:
            self.start_queue()

        if cmd.return_type is queue_item.return_type_none:
            # if we don't want a return value, still provide a list,
            # just a None instead of the dict
            self.queue.append(cmd)
        else:
            self.queue.append(cmd)
            return self.await_queue_return(cmd)

    # Returns the requested type raw/single/length if the data was found
    # or returns None if the queue returned nothing
    # or finally raises an exception if the queue didn't even execute
    # and failed to modify the default data value
    def await_queue_return(self, cmd, fail_msg=""):

        counter = 0
        # Retry waiting for the dict update with a microsleep
        while cmd.return_dict[queue_item.data_key] == queue_item.data_default and counter < 150:
            counter += 1
            time.sleep(0.02)

        # Grab the return val here, for clarity sake
        return_data = cmd.return_dict[queue_item.data_key]

        # When we exit the while, if we default data has been updated
        if cmd.return_dict[queue_item.data_key] != queue_item.data_default:
            # If it's raw, return whatever is in the value spot, even if its empty
            if cmd.return_type == queue_item.return_type_raw:
                return return_data
            # If we want a single, remove all the random formatting around it
            elif cmd.return_type == queue_item.return_type_single:
                # Need to do [0] to remove the tuple. Just want the first string.
                # returns a list of tuples; e.g. [('some_data',)]
                if len(return_data) == 0:
                    return None
                else:
                    return tuple(return_data[0].items())[0][1]
            elif cmd.return_type == queue_item.return_type_len:
                return len(return_data)
        else:
            raise Exception("Failed to return queue data:" + str(fail_msg))

    def start_queue(self):
        if not self.queue_running:
            threading.Thread(target=self.run_queue).start()

    def run_queue(self):
        conn = sqlite3.connect(constants.app_name_short + '_' + self.name + '.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        self.queue_running = True
        queue_empty_count = 0
        while(self.queue_running):
            if(self.is_reading):
                # Something is reading, just do a microsleep
                time.sleep(0.05)
            elif(len(self.queue) > 0):
                # Reset the queue empty count, so reset wait timer
                queue_empty_count = 0
                try:
                    # Item of type queue_item includes the command, return type
                    # and a return byref data dict to store the data
                    item: queue_item = self.queue[0]
                    # Remove the item immediately, if there is an exception
                    # it won't get stuck doing the same item
                    self.queue.remove(self.queue[0])

                    self.last_command = time.mktime(datetime.now().timetuple())
                    if self.use_call_log:
                        log_str = "Executing item: " + str(item.cmd.cmd_str)
                        if item.cmd.params:
                            log_str += " >With Params: " + str(item.cmd.params)
                        self.call_log.log_string(log_str)
                    # If params is not None, then use parameterisation
                    # otherwise just call execute on the cmd_string
                    if item.cmd.params:
                        cur.execute(item.cmd.cmd_str, item.cmd.params)
                    else:
                        cur.execute(item.cmd.cmd_str)

                    # If the command is a non-none return type, then update
                    # the return_dict with data
                    if item.return_type != queue_item.return_type_none:
                        '''
                        If we need to return something, fetchall on the cursor
                        
                        Using the built in row_factory to return structured
                        rows, which we then convert to dicts
                        '''
                        data = cur.fetchall()
                        rows = []
                        for row in data:
                            rows.append(dict(zip(row.keys(), row)))
                        # Stuff the raw data in the dict as a return
                        # and the item while loop will pick up the new data
                        item.return_dict[queue_item.data_key] = rows
                # Should catch the correct exceptions, but this works
                except Exception as e:
                    if(str(e).find("UNIQUE constraint failed") > -1):
                        # Do nothing
                        pass
                    else:
                        self.log.log_string(
                            "Failed to proces queue item: {}. Exception: {}"
                            .format(item.cmd.cmd_str, str(e)),
                            and_print=True
                        )
            elif(time.mktime(datetime.now().timetuple())
                    - self.last_command > self.idle_timeout):
                self.log.log_string(">>Idle time reached. Exiting queue loop.")
                self.queue_running = False
            else:
                # If the queue is empty, sleep for 1s
                # and commit and changes pending
                conn.commit()
                time.sleep(min(0.05*queue_empty_count, 2))
                queue_empty_count += 1
        self.log.log_string("Queue stopped running")
        conn.close()

# Simple queue object to store command string
# and any data if parameterisation is needed/used
class queue_cmd():

    def __init__(self, cmd_str, params=None):
        self.cmd_str = cmd_str
        self.params = params

class queue_item():

    return_type_none = -1
    return_type_raw = 0
    return_type_single = 1
    return_type_len = 2

    data_key = "data"
    data_default = "__nodata__"

    status_incomplete = 10
    status_complete = 11

    def __init__(self, cmd, return_type=return_type_none):
        self.cmd: queue_cmd = cmd
        self.return_dict: dict = {}
        self.return_dict[queue_item.data_key] = queue_item.data_default
        self.return_type: int = return_type
        self.status: int = queue_item.status_incomplete



# Not the best, but simple sanitising to prevent accidental misuse
# for the most part. primarily used for col names where
# parameterisation cant be used
def simple_sqlsafe_str(in_str):
    if in_str is None:
        return None
    return in_str.lower().replace("drop", "") \
        .replace("select", "") \
        .replace("where", "") \
        .replace("table", "") \
        .replace(";", "") \
        .replace("=", "") \
        .replace("'",  "") \
        .replace('"', "") \
        .replace("*", "") \
        .strip()
