import React from "react";
import Box from '@mui/material/Box';
import Chat from './chat';
import Typography from '@mui/material/Typography';
import { ThemeProvider } from "@emotion/react";
import { createTheme } from "@mui/material";
import './style/App.scss';

const theme = createTheme({
  typography: {
    fontFamily: '"Numoto", sans-serif',
  },
  palette: {
    default: {
      main: '#ff0000', // Unselected radio color
    },
    primary: {
      main: '#407ec9', // Unselected radio color
    },
    secondary: {
      main: '#407ec9', // Selected radio color
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
          <Box
            className="header"
          >
            {/* <img src="" alt="Logo" className="logo" /> */}
            <Typography variant="h4" component="h1" gutterBottom className="title">
              Micro-economics chatterbox
            </Typography>
            {/* <div className='user-info'></div> */}
          </Box>
          <Box sx={{ flexGrow: 1 }}>
            <Chat />
          </Box>
        </Box>
        <div>
          <div className="backgroundDiv">&nbsp;</div>
        </div>
    </ThemeProvider>
  );
}
