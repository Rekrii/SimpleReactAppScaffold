
export class EventManagerClass {

  EVENT_LOGIN = "eventLogin";
  EVENT_LOGOUT = "eventLogout";

  eventRegister: Record<string, Array<Function>>;

  constructor() {
    this.eventRegister = {};
  }


  registerEventListener(eventName: string, callback: Function) {
    // Need to check if we have a new eventName, e.g. the list 
    // of callbacks will be undefined. so set it as a new list
    if (this.eventRegister[eventName] === undefined) {
      this.eventRegister[eventName] = [];
    }
    this.eventRegister[eventName].push(callback);
  }

  raiseEvent(eventName: string) {
    // Need to make sure we dont have an empty list for this event
    // e.g. if no one has registered for this event
    if (this.eventRegister[eventName] !== undefined) {
      this.eventRegister[eventName].forEach(callback => {
        callback();
      });
    }
  }
}

var EventManager = new EventManagerClass()

export default EventManager;