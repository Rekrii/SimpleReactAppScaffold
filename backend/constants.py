'''
  General app-wide constants
'''
app_name_full: str = "appName"
app_name_short: str = "app"

'''
  Flask constants, generally used in flask_backend.py
'''
# dev_mode generally used to select between dev/prod constants
dev_mode: bool = True

flask_dev_port: str = "3012"
flask_dev_subdir = "/" + flask_dev_port

flask_prod_port: str = "3112"
flask_prod_subdir = ""

'''
  database constants
'''
# delay in seconds between login attempts
db_attempt_delay = 5
# 1min timeout if we get no new commands to execute
db_idle_timeout = 60
# If we want to log *ever* command that gets executed
# this gets big if left on for a long time
db_use_call_log = True
# Database will create these columns when the backend/db starts
# These cols are added to a 'data' table, 
# this is the table get_data/set_data uses. 
# NOTE: Generally use lower case names.
db_col_names = ['colname']