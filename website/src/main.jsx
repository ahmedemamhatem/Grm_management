import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from "react-redux";
import App from './App.jsx';
import { store } from "./app/store.js";

gsap.registerPlugin(ScrollTrigger);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </StrictMode>,
)
