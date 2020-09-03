import { Constants } from './constants';
import { getCookieOrDefault, setCookie } from './utilities';
import React from 'react';
import EventManager from './EventManager';

async function getLoggedInStatus() {
  // Check if the user cookie is still valid/logged in
  var name = getCookieOrDefault(Constants.cookieNameSessionName, "")
  var uuid = getCookieOrDefault(Constants.cookieNameStringSessionUuid, "")

  var myInit: RequestInit = {
    method: 'POST',
    body: JSON.stringify(
      {
        name: name,
        uuid: uuid,
      }
    ),
    headers: new Headers(),
    mode: 'cors',
    credentials: 'include',
    cache: 'default'
  };

  var myRequest = new Request(Constants.baseUrl + "/api/is-logged-in", myInit);
  var result = await (await fetch(myRequest)).text();
  return (result.trim() === "true");
}

export class LoginArea extends React.Component<any, any> {
  constructor(props: any) {
    super(props);
    // Extra state variables are defined from the input boxes
    // where the generic change handler updates state based on
    // the id of the element, normally input<Name>
    this.state = {
      loginInputName: getCookieOrDefault(Constants.cookieNameSessionName, ""),
      loginInputPassword: "",
      status: "",
      isLoggedIn: false,
      isLoading: false,
      showReg: false
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleLogout = this.handleLogout.bind(this);
    this.handleLogin = this.handleLogin.bind(this);
    this.setAsLoggedIn = this.setAsLoggedIn.bind(this);
    this.showRegistration = this.showRegistration.bind(this);

    // Can't call setState in the constructor, so call it on a
    // 500ms timeout, hopefully once the object has loaded
    // no big issue I don't think if it calls it too early...
    window.setTimeout(async () => {
      EventManager.registerEventListener(EventManager.EVENT_LOGIN, this.setAsLoggedIn);
    }, 500)
  }

  async componentDidMount() {

    var result = await getLoggedInStatus(); // returns a bool type
    // this.setState({isLoggedIn: result})
    if (result) {
      EventManager.raiseEvent(EventManager.EVENT_LOGIN)
    }
    console.log("checking logged in status: " + result);
  }

  setAsLoggedIn() {
    // This is just used as the event callback when registering
    // so we also need to hide the showReg area too
    this.setState({ isLoggedIn: true });
    this.setState({ showReg: false });
    document.title = this.state.loginInputName + " - TaskTracker";
  }

  handleChange(event: any) {
    this.setState({ [event.target.id]: event.target.value });
    // Use a swich/case to go through each id name if required
  }

  showRegistration() {
    this.setState({ showReg: true })
  }

  async handleLogout(event: any) {

    event.preventDefault();

    this.setState({ isLoading: true });

    var name = getCookieOrDefault(Constants.cookieNameSessionName, "");
    var uuid = getCookieOrDefault(Constants.cookieNameStringSessionUuid, "");

    var myInit: RequestInit = {
      method: 'POST',
      body: JSON.stringify(
        {
          name: name,
          uuid: uuid,
        }
      ),
      headers: new Headers(),
      mode: 'cors',
      credentials: 'include',
      cache: 'default'
    };

    var myRequest = new Request(Constants.baseUrl + "/api/logout", myInit);
    // var result = await (await fetch(myRequest)).text();
    await (await fetch(myRequest)).text();

    setCookie(Constants.cookieNameSessionName, "", 15);
    setCookie(Constants.cookieNameStringSessionUuid, "", 15);

    EventManager.raiseEvent(EventManager.EVENT_LOGOUT);

    this.setState({ isLoading: false });
    this.setState({ isLoggedIn: false });
  }

  async handleLogin(event: any) {
    event.preventDefault();

    this.setState({ isLoading: true });

    var myInit: RequestInit = {
      method: 'POST',
      body: JSON.stringify(
        {
          name: this.state.loginInputName,
          password: this.state.loginInputPassword,
        }
      ),
      headers: new Headers(),
      mode: 'cors',
      credentials: 'include',
      cache: 'default'
    };

    var myRequest = new Request(Constants.baseUrl + "/api/login", myInit);

    var response = await fetch(myRequest);
    var result = await (response).text();
    setCookie(Constants.cookieNameStringSessionUuid, result, 15);
    setCookie(Constants.cookieNameSessionName, this.state.loginInputName, 15);

    // Length of uuid e.g. "c117be33-e3d2-4b15-8ce8-c0484e6da7fe".length
    console.log("Login attempt result: " + result.substring(0, 200));
    if (result.length === 36) {
      this.setState({ status: "Success" });
      this.setState({ isLoggedIn: true });
      EventManager.raiseEvent(EventManager.EVENT_LOGIN)
    }
    else if (result.toLowerCase().indexOf("password not valid") > -1) {
      this.setState({ status: result });
    }
    else if (response.status === 502) {
      this.setState({ status: "Login server down" });
    }
    else if (response.status === 500) {
      this.setState({ status: "Login server error" });
    }
    else {
      this.setState({ status: "Unknown server response" });
    }
    // Regardless if login works or fails, need to clear the password from state
    this.setState({ loginInputPassword: "" })
    this.setState({ isLoading: false });
  }

  render() {
    return (
      <div className="mt-1 mx-1">
        {this.state.isLoggedIn ?
          <div>
            Logged in as: {this.state.loginInputName}
            <button onClick={this.handleLogout}>Logout</button>
          </div>
          :
          <div>
            {this.state.showReg ?
              <RegisterArea />
              :
              <div>
                <div className="d-flex flex-row">
                  <form onSubmit={this.handleLogin}>
                    <label>
                      User Name:
                      <input type="text" id="loginInputName" onChange={this.handleChange} />
                    </label>
                    <label>
                      Password:
                      <input type="password" id="loginInputPassword" autoComplete="cur-pw" onChange={this.handleChange} />
                    </label>
                    <input type="submit" value="Login" />
                    <button onClick={this.showRegistration}>Create Account</button>
                  </form>
                </div>
                <div className="d-flex justify-content-center">
                  {this.state.status}
                </div>
                <div className="d-flex justify-content-center">
                  {this.state.isLoading ? <div className="load-spinner small"></div> : null}
                </div>
              </div>
            }
          </div>
        }
      </div>
    );
  }
}

class RegisterArea extends React.Component<any, any> {
  constructor(props: any) {
    super(props);
    // Extra state variables are defined from the input boxes
    // where the generic change handler updates state based on
    // the id of the element, normally input<Name>
    this.state = {
      registerInputName: "",
      registerInputPassword: "",
      registerInputPasswordConf: "",
      isLoading: false
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);

  }

  handleChange(event: any) {
    this.setState({ [event.target.id]: event.target.value });
    // Use a swich/case to go through each id name if required
  }

  async handleSubmit(event: any) {
    event.preventDefault();

    if (this.state.registerInputPassword !== this.state.registerInputPasswordConf) {
      alert("Passwords do not match")
      return
    }

    this.setState({ isLoading: true });

    var myInit: RequestInit = {
      method: 'POST',
      body: JSON.stringify(
        {
          name: this.state.registerInputName,
          password: this.state.registerInputPassword,
          password_conf: this.state.registerInputPasswordConf
        }
      ),
      headers: new Headers(),
      mode: 'cors',
      credentials: 'include',
      cache: 'default'
    };

    var myRequest = new Request(Constants.baseUrl + "/api/register", myInit);
    var response = await fetch(myRequest);
    var result = await (response).text();
    // result = JSON.parse(result)

    // Length of uuid e.g. "c117be33-e3d2-4b15-8ce8-c0484e6da7fe".length
    // alert(result)
    if (result.length === 36) {
      setCookie(Constants.cookieNameStringSessionUuid, result, 15)
      setCookie(Constants.cookieNameSessionName, this.state.registerInputName, 15)
      EventManager.raiseEvent(EventManager.EVENT_LOGIN)
    }
    else if (response.status === 502) {
      this.setState({ status: "Registration server down" });
    }
    else if (response.status === 500) {
      this.setState({ status: "Registration server error" });
    }
    else {
      this.setState({ status: "Unknown server response" });
    }

    this.setState({ isLoading: false });
  }

  render() {
    return (
      <div>
        <form onSubmit={this.handleSubmit}>
          <label>
            User Name:
            <input type="text" id="registerInputName" onChange={this.handleChange} />
          </label>
          <label>
            Password
            <input type="password" id="registerInputPassword" onChange={this.handleChange} />
          </label>
          <label>
            Confirm Password
            <input type="password" id="registerInputPasswordConf" onChange={this.handleChange} />
          </label>
          <label>
            <input type="submit" value="Register" />
          </label>
        </form>
        <div className="d-flex justify-content-center">
          {this.state.isLoading ? <div className="m-2 load-spinner"></div> : null}
        </div>
      </div>
    );
  }
}
