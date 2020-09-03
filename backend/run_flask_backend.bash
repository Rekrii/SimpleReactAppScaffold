# pull port for dev or prod here instead of a separate .py script
pyScript="
import constants
if constants.dev_mode:
  print(constants.flask_dev_port)
else:
  print(constants.flask_prod_port)
"

# Run the above temp script to get the port
myVar=$(python3 -c "$pyScript")

# Then export UTF-8 and start flask on the required port
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
FLASK_APP=flask_backend.py python3 -m flask run --host=0.0.0.0 --port=$myVar
