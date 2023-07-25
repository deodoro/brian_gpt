import React from "react";
import ReactDOM from "react-dom";
import App from "./App";
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import theme from './theme';

import { createRoot } from 'react-dom/client';
const container = document.getElementById("root");
const root = createRoot(container);

root.render(
    <ThemeProvider theme={theme}>
    <CssBaseline />
    <App tab="home" />
    </ThemeProvider>);
