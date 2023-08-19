import React from "react";
import Box from '@mui/material/Box';
import Chat from './chat';
import Navigator from './navigator';
import Typography from '@mui/material/Typography';
import { ThemeProvider } from "@emotion/react";
import { createTheme } from "@mui/material";
import './style/App.scss';
import OAuth2Login from 'react-simple-oauth2-login';

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

// const authConfig = {
//   scope: ["openid", "profile", "email"],
//   authorizeUrl: process.env.OAUTH_AUTHORIZATION_URI,
//   clientID:  process.env.OAUTH_CLIENT_ID,
//   redirectUri: process.env.OAUTH_REDIRECT_URI,
// };

export default function App() {

  // React.useEffect(() => {
  //   if (!token) {
  //     getToken();
  //   }
  // }, [token, getToken]);

  // if (!token) {
  //   return <div>Redirecting to Microsoft for authentication...</div>;
  // }

  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: '100vh'
        }}
      >
        <OAuth2Login
          responseType="code"
          scope="openid profile email"
          authorizationUrl={process.env.REACT_APP_OAUTH_AUTHORIZATION_URI}
          clientId={process.env.REACT_APP_OAUTH_CLIENT_ID}
          redirectUri={process.env.REACT_APP_OAUTH_REDIRECT_URI}
          onSuccess={(o) => console.dir(o)}
          onFailure={() => console.log('failure')}
          className='login-button'
        />,
        <Box className="header">
          {/* <img src="" alt="Logo" className="logo" /> */}
          <Typography variant="h4" component="h1" gutterBottom className="title">
            Micro-economics chatterbox
          </Typography>
          {/* <div className='user-info'></div> */}
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
