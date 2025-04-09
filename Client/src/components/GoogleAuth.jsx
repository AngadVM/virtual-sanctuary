import React from 'react';
import { GoogleOAuthProvider, useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';

const GoogleAuth = () => {
  const login = useGoogleLogin({
    onSuccess: async (codeResponse) => {
      const response = await axios.post('auth/google_login', { code: codeResponse.code });
      console.log(response.data);
    },
    flow: 'auth-code',
  });

  return <button onClick={() => login()}>SIGN UP WITH GOOGLE</button>;
};

export default function AuthWrapper() {
  return (
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
      <GoogleAuth />
    </GoogleOAuthProvider>
  );
}
