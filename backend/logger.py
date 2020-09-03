import os
import atexit


class logger:

    def __init__(self, log_name, prepend_string=''):
        if not os.path.exists("logs/"):
            os.makedirs("logs/")
        self.log_file = open(
            'logs/log_{}.txt'.format(log_name),
            'a',
            buffering=1  # use line buffering
        )
        self.prepend_str = prepend_string
        # Using atexit to close the log file
        atexit.register(self.cleanup)

    def cleanup(self):
        self.log_file.close()

    def log_string(self, text, newline_char="\n", and_print=False):
        if self.log_file is None:
            self.__init__(self)
        self.log_file.write(self.prepend_str + str(text) + newline_char)
        if and_print:
            print(text)
