import React from 'react';
import ReactDOM from 'react-dom';
import { App } from './modules/app'
import 'normalize.css';
import { BrowserRouter as Router } from 'react-router-dom';

ReactDOM.render(<Router>
    <App />
  </Router>,
  document.getElementById('root')
);
