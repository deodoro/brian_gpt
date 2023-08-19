import { PublicClientApplication } from "@azure/msal-browser";

const msalConfig = {
  auth: {
    clientId: process.env.REACT_APP_OAUTH_CLIENT_ID,
    authority: process.env.REACT_APP_OAUTH_AUTHORITY,
    redirectUri: process.env.REACT_APP_OAUTH_REDIRECT_URI,
  },
  cache: {
    cacheLocation: "localStorage",
    storeAuthStateInCookie: false,
  },
};

const msalInstance = new PublicClientApplication(msalConfig);

class MsalUtils {

  static get instance() {
    return msalInstance;
  }

  static async getAccessToken() {
    const accounts = msalInstance.getAllAccounts();

    if (accounts && accounts.length > 0) {
      const request = {
        scopes: ["user.read"],
        account: accounts[0]
      };

      try {
        const response = await msalInstance.acquireTokenSilent(request);
        return response.accessToken;
      } catch (error) {
        console.error("Error getting the token:", error);
        try {
          // If silent token acquisition fails, try to get it interactively
          const response = await msalInstance.acquireTokenPopup(request);
          return response.accessToken;
        } catch (err) {
          console.error("Error acquiring the token interactively:", err);
          return null;
        }
      }
    } else {
      console.warn("No accounts detected");
      return null;
    }
  }
}

export default MsalUtils;
