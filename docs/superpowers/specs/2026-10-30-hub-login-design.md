# Chores: log in through the family hub

Date: 2026-10-30. Rollout step 4 of the family hub (FrankAndreas/family-hub), after the budget app and the meal
planner. It follows their switch (family-meal-planner `docs/superpowers/specs/2026-10-30-hub-login-design.md`). The
user asked to skip the questions, so the points marked **(my call)** were settled by Claude.

## Goals

1. **The login** is the hub's `hub_session` cookie (`Authorization: Bearer` for tests and scripts):
   - the hub's `/api/session?app=chores` says whose it is and whether they may use the chores app **(my call:** key
     `chores`);
   - a change made with the cookie needs `X-Requested-With: chores`;
   - home only: a request with `Cf-Connecting-Ip` is no login;
   - gone: PINs, the login page, `JWT_SECRET_KEY`, the SSE token and the seeded Admin.
2. **People come from the hub:** the name (`nickname`) and the language follow it.
   - **Roles (my call):**
     - a hub **parent** is **Admin** here;
     - a hub **child** keeps the game role a parent sets here (Contributor, Teenager, Child, or one made in Roles)
       and can never be Admin;
     - a new child starts as **Child**.
     - The Admin role can't be given by hand, and a parent's role can't be changed here.
   - **Linking existing rows:** they are linked by name, once, at the first sync. A hub parent matches an Admin row and
     a hub child matches a non-Admin row, so points, history, goals, push subscriptions and e-mail stay with their
     person.
3. **Removed in the hub:** the person is hidden (`is_active` false). Their points and history stay until a parent
   deletes their data. Meanwhile:
   - they get no daily tasks;
   - they don't show on the boards, in streaks or in notifications;
   - they're not in the people lists.
   - `DELETE /users/{id}` only works for hidden people: an active person gives 409 `still_in_hub`.
4. **"Log out"** goes to `<HUB_PUBLIC_URL>/logout?next=<app>`. A 401 sends the browser to the hub's login. "No
   access" and "hub unavailable" each get their own page.
5. **Kept as today:**
   - the family dashboard opens without a login (a tablet at home) **(my call)**;
   - e-mail and notification settings stay per person here;
   - the default language setting stays.

## Endpoints
- **New:**
  - `GET /users/me`;
  - `GET /users/removed` (admins);
  - `GET /hub` returning `{"login_url"}`.
- **`/events` (SSE):** authenticates with the hub cookie, which EventSource sends by itself; the token query parameter
  is gone.
- **Removed:**
  - `POST /login/`, `POST /users/`, `PUT /users/{id}/password`, `PUT /users/{id}/language`;
  - name changes through `PUT /users/{id}`.

## Data
An Alembic migration that works on PostgreSQL and SQLite:
- `users.hub_id` (unique, nullable);
- `users.is_active` (default true);
- `users.login_pin` dropped.

## Deploy
- **NAS `compose.yaml`:** the backend gets `HUB_URL`, `HUB_PUBLIC_URL` and `HUB_APP_KEY`; `JWT_SECRET_KEY` goes away.
- **In the hub:** the chores tile gets the key `chores`, with everyone ticked. Names and roles must match before the
  first login.
