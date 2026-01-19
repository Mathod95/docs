---
title: "JWTs Are Not Session Tokens , Stop Using Them Like One"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@ThreadSafeDiaries/jwts-are-not-session-tokens-stop-using-them-like-one-c1901ae8c670"
author:
  - "[[ThreadSafe Diaries]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

When JSON Web Tokens (JWTs) hit the mainstream, they were hailed as the solution to everything wrong with session management. ==Stateless! Compact!== Tamper-proof! Suddenly, everyone started stuffing them into every web app like ketchup on bad code.

But somewhere along the way, we forgot that JWTs are not a drop-in replacement for session tokens. They’re not magical. And if you’re using them like sessions, you’re probably building a security nightmare you’ll regret at scale.

Let’s unpack that, with brutal honesty, some code, and a wake-up call.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*LnVuh0qndBDFPzmP.png)

## First, Let’s Get One Thing Straight

**JWTs are not session tokens.**  
JWTs are *self-contained claims*. Session tokens are *pointers to state on the server*.

Mix these up, and you’ll fall into dangerous traps like:

- Unrevocable tokens
- Bloated auth payloads
- Infinite sessions
- Broken logout
- Surprise security breaches

But before we go deeper, let’s lay the foundation right.

## Stateless vs Stateful Authentication

Let’s say you log into a site.

### Stateful Auth (Session Tokens)

- The server stores your session info in a database or in-memory store (Redis).
- You get a **random session ID** back as a cookie.
- Every request includes that session ID, and the server looks it up.
- If you log out, the server deletes your session from the store.

This is **stateful** the server maintains session state.

```c
// Express session example
app.use(session({
  secret: 'super-secret',
  store: new RedisStore(),
  resave: false,
  saveUninitialized: true,
  cookie: { secure: true }
}));
```

### Stateless Auth (JWTs)

- The server encodes user info into a JWT and signs it.
- No session is stored.
- Every request includes the token (usually in the Authorization header).
- The server *verifies* the token but doesn’t *look anything up*.

This is **stateless** there’s no persistent session store.

```c
// JWT verification
const jwt = require('jsonwebtoken');
app.use((req, res, next) => {
  const token = req.headers.authorization?.split(" ")[1];
  const user = jwt.verify(token, JWT_SECRET);
  req.user = user;
  next();
});
```

## So What’s the Problem?

### 1\. No Built-in Revocation

JWTs are self-contained. Once issued, they’re valid until expiration.

This means:

- You can’t revoke them early.
- “Logout” is meaningless.
- If someone steals a valid JWT, they’re authenticated until it expires.

Compare that to session tokens:

- Just delete the session from your Redis store.
- Boom. User logged out everywhere instantly.

Here’s a nasty example:

```c
// Token expires in 1 hour
const token = jwt.sign({ userId: 123 }, secret, { expiresIn: '1h' });
// User gets hacked 10 minutes later
// There's NO WAY to invalidate this token unless you track every one
```

### 2\. They’re Not Short

JWTs are huge compared to session IDs. Especially when you start encoding roles, permissions, org IDs, feature flags…

Your `Authorization` header quickly bloats like a bad SQL query.

Example:

```c
// Realistic JWT payload
{
  "sub": "1234567890",
  "name": "Jane Doe",
  "email": "jane@example.com",
  "roles": ["admin", "editor"],
  "featureFlags": ["beta-access"],
  "exp": 1719282812
}
```

Add a signature and base64 encoding? That’s ~800 bytes per request. Multiply that by thousands of API requests and your bandwidth and cache hit rates suffer.

### 3\. No Rotation, No Grace Periods

You can’t rotate JWTs without complex setups. Refresh tokens help, but many devs:

- Don’t implement refresh token rotation
- Store both access + refresh in localStorage
- Miss edge cases like parallel logout/login

Session tokens, on the other hand, naturally support grace periods:

- Rotate session IDs server-side
- Allow some overlap between old and new sessions

JWTs need dance routines to get this right:

- Rotate access tokens every 15 mins
- Rotate refresh tokens every use
- Keep blacklist of refresh token IDs
- Pray you didn’t screw it up

## Benchmarks Don’t Lie

We tested a simple API behind a load balancer using:

- Session cookies (Redis-backed)
- JWT tokens (200 bytes)
- JWT tokens (800 bytes)
```c
| Type          | Avg Request Size | Req/sec @ 100 users | Avg Latency |
| ------------- | ---------------- | ------------------- | ----------- |
| Session Token |  ~150 bytes      | 3200                | 18ms        |
| JWT (200B)    |  ~350 bytes      | 3100                | 21ms        |
| JWT (800B)    |  ~950 bytes      | 2800                | 27ms        |
```

Yes, token size matters. Especially at scale. And if you’re mobile-first? Every byte counts.

## When Are JWTs Actually Good?

JWTs **shine** when you need:

- **Cross-domain SSO** (e.g., OAuth2 / OpenID Connect)
- **Stateless microservice auth**
- **Short-lived access tokens**
- **API-to-API communication**

But here’s the thing: in **web apps with login, logout, user sessions**?

JWTs are usually overkill.

## What You Should Never Do

- Store long-lived JWTs in `localStorage`. That’s a CSRF + XSS buffet.
- Treat JWTs as permanent sessions.
- Skip refresh token rotation.
- Forget to handle logout. (Yes, even with stateless auth.)

## The Right Way to Use JWTs (If You Must)

Still want JWTs? Fine. But do it right.

### Use Access + Refresh Token Pair

- Access Token: short-lived (5–15 mins), sent with requests
- Refresh Token: long-lived, stored **securely**, used to get new access tokens
```c
// On login
{
  "accessToken": "eyJhbGciOi...",
  "refreshToken": "eyJhdWQiOi..."
}
```

==**Store refresh tokens in HTTP-only, Secure cookies**==**.**  
Or if you’re building an SPA, **rotate them frequently** and track refresh token IDs server-side.

## Build Token Revocation List (Blacklist)

Even if JWTs are stateless, you can track:

- Revoked refresh token IDs
- User logout events
- Rotation mismatches

Yes, it’s extra infra. But you can’t avoid this if you care about security.

## Architecture Diagram

Here’s a secure, hybrid flow that combines stateless access with stateful refresh:

```c
+-------------+         +-------------+         +---------------+
|  Frontend   | <-----> | API Gateway | <-----> | Auth Service  |
+-------------+         +-------------+         +---------------+
     |                        |                           |
     |--- login ------------->|                           |
     |                        |-- validate credentials--> |
     |                        |<-- access+refresh tokens--|
     |<-- 200 OK ------------ |
     |                        |
     |-- request with access->|
     |                        |-- verify signature ------> (stateless)
     |                        |<-- 200 OK ----------------|
     |                        |
     |-- expired access token |
     |-- send refresh token -->|-- check DB --------------> (stateful)
     |                        |-- issue new access token--|
     |<-- 200 OK -------------|
```

## But My App Works Fine With JWTs

Sure it does until:

- You need to revoke access
- A user logs out and still has access for 60 mins
- Someone steals a token from localStorage
- You move to multiple services and can’t coordinate expiration

Then you realize you reinvented a worse version of sessions.

## Your options:

```c
| Use Case           | Use                        |
| ------------------ | -------------------------- |
| Web login/logout   | Session token              |
| Mobile auth        | Access + Refresh JWTs      |
| Microservices      | JWT                        |
| SSO / OAuth        | JWT                        |
| High-security apps | Hybrid (JWT + token store) |
```

Don’t get seduced by the hype. Know the trade-offs. Design for revocation. And please stop using JWTs like session tokens.

Sharing insights on tech, growth, and life as it unfolds — one runtime at a time.

## More from ThreadSafe Diaries

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--c1901ae8c670---------------------------------------)