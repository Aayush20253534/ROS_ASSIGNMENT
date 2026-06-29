// Entry point for the React app. Vite loads this file via index.html.
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

// Mount the <App /> component into the #root div from index.html.
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
