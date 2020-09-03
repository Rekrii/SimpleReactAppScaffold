import React from 'react';
import './custom.css';
import { LoginArea } from './login';

function App() {
  return (
    <div className="App">
      <div>
        <div className="container-fluid border-bottom margin-bottom-20">
          <div className="row justify-content-end">
            <LoginArea />
          </div>

          <div className="row">
            <h1 className="title">Base App With Login</h1>
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

export default App;
