import React from 'react';
import './custom.css';
import { LoginArea } from './login';
import { pushDataToServer, pullServerData } from './utilities'

export class App extends React.Component<any, any> {

  async clearTestDataOnServer() {
    await pushDataToServer("colname", "")
  }

  async pushTestDataToServer() {
    await pushDataToServer("colname", "pushed test data");
  }

  async pullTestDataFromServer() {
    alert(await pullServerData("colname"))
  }

  render() {
    return (
      <div className="App">
        <div>
          <div className="container-fluid border-bottom margin-bottom-20">
            <div className="row justify-content-end">
              <LoginArea />
            </div>
  
            <div className="row">
              <h1 className="title">Base App With Login</h1>
              <button onClick={this.clearTestDataOnServer}>Clear Test Data</button>
              <button onClick={this.pushTestDataToServer}>Push Test Data</button>
              <button onClick={this.pullTestDataFromServer}>Pull Test Data</button>
            </div>
          </div>
  
          <div className="container-fluid">
            <div className="row justify-content-center">
              <h1>Content Area</h1>
              {/* Add content modules here */}
            </div>
          </div>
  
        </div>
      </div>
    );
  }
}

export default App;
