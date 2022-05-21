function decodeTokenPayload(token) {
    const tokenPayload = token.split('.')[1];
    const tokenDetails = JSON.parse(atob(tokenPayload));
    console.log(tokenDetails);

    return tokenDetails;
}

export function getUserIdFromToken(token) {
    const tokenPayload = decodeTokenPayload(token);

    return tokenPayload.email;
}

export function saveTokenToStorage(token) {
    localStorage.setItem('apiToken', token)
}

export function retrieveTokenFromStorage() {
    const token = localStorage.getItem('apiToken');

    return token;
}