# Authentication

Phase 3 implements MediaWiki OAuth the same way [agpb-api](https://github.com/) does.

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
