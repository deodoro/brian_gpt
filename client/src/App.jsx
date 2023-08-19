import {React, useEffect} from "react";
import Box from '@mui/material/Box';
import Chat from './chat';
import Navigator from './navigator';
import Typography from '@mui/material/Typography';
import { useMsal, MsalProvider } from "@azure/msal-react";
import { ThemeProvider } from "@emotion/react";
import { createTheme } from "@mui/material";
import MsalUtils from "./msal-utils";
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

const LogoffButton = () => {
  const { instance, accounts } = useMsal();

  if (accounts.length === 0) {
      return null; // Don't show the button if not logged in
  }

  const handleLogout = () => {
      instance.logout(); // This will clear the cache and logout the user
  };

  return <button onClick={handleLogout}>Log out</button>;
}

export default function App() {
  MsalUtils.instance.initialize();
  return (
    <MsalProvider instance={MsalUtils.instance}>
      <AppContent />
    </MsalProvider>
  )
}

function AppContent() {
  const { instance, accounts } = useMsal();

  const doLogin = async () => {
      if (accounts.length === 0) {
          try {
              const response = await instance.loginPopup({
                  scopes: ["openid", "profile", "email"]
              });
              console.dir(`token=${response.accessToken}`);
          } catch (error) {
              console.log("Login failed:", error);
          }
      } else {
          const account = accounts[0];
          const response = await instance.acquireTokenSilent({
              account,
              scopes: ["openid", "profile", "email"]
          });
          console.dir(`token=${response.accessToken}`);
      }
  };

  useEffect(() => {
      doLogin();
  }, []);

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
          <LogoffButton />
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
