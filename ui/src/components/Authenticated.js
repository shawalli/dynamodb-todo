import React, { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';


function Authenticated(props) {
    const onSuccess = (response) => {
        console.log('LOGIN SUCCESS - current user:', response);
        props.setIdToken(response.credential);
    }

    const onFailure = (error) => {
        console.log("LOGIN FAILURE - reason:", error)
    }

    const loginScreen = (
        <div style={{
            maxWidth: "100%",
            display: "flex",
            justifyContent: "center"
        }}>
            <GoogleLogin
                onSuccess={onSuccess}
                onError={onFailure}
                shape='circle'
                theme='filled_blue'
                width='400'
                size='large'
            />
        </div >
    );

    return props.idToken !== undefined ? props.children : loginScreen;
}

export default Authenticated;