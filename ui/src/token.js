function decodeTokenPayload(token) {
    const tokenPayload = token.split('.')[1];
    const tokenDetails = JSON.parse(atob(tokenPayload));
    console.log(tokenDetails);

    return tokenDetails;
}

function isTokenExpired(token) {
    const tokenPayload = decodeTokenPayload(token);

    const secondsSinceEpoch = Math.round((new Date()).getTime() / 1000)

    return (tokenPayload.exp - secondsSinceEpoch) <= 0 ? true : false;
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

    if ((token === null) || (isTokenExpired(token))) {
        return null;
    }

    return token;
}