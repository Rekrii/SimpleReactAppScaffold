from db_base import db_base
from accounts import accounts

# db = db_base("test")

act = accounts(is_test=True)

act.add_account("test", "test")
print("Getting valid account: ", act.get_account("test", "test"))
print("Getting invalid account: ", act.get_account("invalid", "na"))

sessUuid = act.start_session("test", "test")
print("Started valid session: ", sessUuid)
print("Started invalid session: ", act.start_session("na", "na"))

print("Checking valid session: ", act.active_sessions.check_session("test", sessUuid))
print("Checking invalid session: ", act.active_sessions.check_session("na", "na"))

print("Adding valid data ('testValue'): ", act.set_data("test", sessUuid, "testCol", "testValue"))
print("Getting valid data: ", act.get_data("test", sessUuid, "testCol"))

print("Adding valid data ('testValueAgain'): ", act.set_data("test", sessUuid, "testCol", "testValueAgain"))
print("Getting valid data: ", act.get_data("test", sessUuid, "testCol"))

print("Ending valid session: ", act.end_session("test", sessUuid))
print("Checking ended session: ", act.active_sessions.check_session("test", sessUuid))
print("Getting ended session data: ", act.get_data("test", sessUuid, "testCol"))
print("Ending invalid session: ", act.end_session("na", "na"))