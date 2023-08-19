import React from "react";
import Box from '@mui/material/Box';
import Chat from './chat';
import Navigator from './navigator';
import Typography from '@mui/material/Typography';
import { ThemeProvider } from "@emotion/react";
import { createTheme } from "@mui/material";
import './style/App.scss';

const theme = createTheme({
  typography: {
    fontFamily: '"Nunito", sans-serif',
  },
  palette: {
    default: {
      main: '#ff0000', // Unselected radio color
    },
  },
});

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: '100vh'
        }}
      >
        <Box className="header">
          <Typography variant="h4" component="h1" gutterBottom className="title">
            Micro-economics chatterbox
          </Typography>
        </Box>
        <Box sx={{ flexGrow: 0 }} className="navigator-container">
          <Navigator />
        </Box>
        <Box sx={{ flexGrow: 1 }} className="chat-container">
          <Chat />
        </Box>
      </Box>
    </ThemeProvider>
  );
}
