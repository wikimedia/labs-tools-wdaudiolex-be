# Token-Based Authentication

This application now uses token-based authentication instead of cookies/sessions. Here's how to use it:

## TL:DR

1. `GET /api/auth/login` returns `redirect_string` and `request_token`.
2. The frontend sends the user to Wikimedia, then `POST /api/oauth-callback`
   with the request token and the callback query string.
3. The API returns a JWT. Send it as `Authorization: Bearer <token>`.
4. `POST /api/auth/logout` invalidates the stored `temp_token`.

Writes (`POST /lexeme/audio/add`, user updates, skips) require a token.
Commons and Wikidata **reads** do not.

Password `action=login` / `clientlogin` is not supported.

OAuth consumer: **Wikidata**, so `wbcreateclaim` can add P443 on a lexeme form.
Set `CONSUMER_KEY` and `CONSUMER_SECRET` in `.env`.

## Authentication Flow

### 1. Initiate Login

**GET** `/api/auth/login`

Returns:

```json
{
  "redirect_string": "https://meta.wikimedia.org/w/index.php?title=Special:OAuth/authorize&oauth_token=...",
  "request_token": "{\"key\":\"...\",\"secret\":\"...\"}"
}
```

### 2. OAuth Callback

**POST** `/api/oauth-callback`

Request body:

```json
{
  "request_token": "{\"key\":\"...\",\"secret\":\"...\"}",
  "query_string": "oauth_token=...&oauth_verifier=..."
}
```

Returns:

```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "username": "your_username",
  "pref_langs": "de,en"
}
```

### 3. Using the Token

Include the token in your API requests using one of these methods:

#### Option A: Authorization Header (Recommended)

```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### Option B: Custom Header (Backward Compatibility)

```bash
x-access-tokens: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 4. Logout

**POST** `/api/auth/logout`

Request body:

```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Example Usage

### Frontend (Next.js/React)

```javascript
// Login flow
const loginResponse = await fetch('/api/auth/login');
const { redirect_string, request_token } = await loginResponse.json();

// Redirect user to OAuth
window.location.href = redirect_string;

// After OAuth callback, exchange for token
const tokenResponse = await fetch('/api/oauth-callback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    request_token: request_token,
    query_string: window.location.search.substring(1)
  })
});
const { token } = await tokenResponse.json();

// Store token (localStorage, sessionStorage, etc.)
localStorage.setItem('auth_token', token);

// Use token for authenticated requests
const usersResponse = await fetch('/api/users/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### Backend API Calls

```python
import requests

# Make authenticated request
headers = {
    'Authorization': f'Bearer {token}'
}
response = requests.get('http://localhost:5000/api/users/', headers=headers)
```

## Token Structure

The JWT token contains:

- `token`: User's temporary token for database lookup
- `access_token`: OAuth access token for Wikidata API calls
- `exp`: Expiration time (45 minutes from creation)

## Security Notes

- Tokens expire after 45 minutes
- Tokens are invalidated on logout
- Always use HTTPS in production
- Store tokens securely on the client side
- Never expose tokens in URLs or logs
