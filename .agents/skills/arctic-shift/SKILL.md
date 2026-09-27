---
name: arctic-shift
description: Use this skill when you need to query Reddit post or comment data for research. Reddit's own site and API block automated access. Arctic Shift is the working alternative — it exposes archived Reddit data through a free HTTP API. Activate on: companion user research, community post analysis, r/Replika, r/CharacterAI, r/VoiceAIBots, or any task that requires reading Reddit content at scale.
---

# Arctic Shift

Arctic Shift makes archived Reddit data queryable. Use it instead of trying to fetch reddit.com directly — that fails every time.

Base URL: `https://arctic-shift.photon-reddit.com`  
Search UI: `https://arctic-shift.photon-reddit.com/search`  
Docs: `https://github.com/ArthurHeitmann/arctic_shift/tree/master/api`

---

## Key endpoints

### Search posts
```
GET /api/posts/search
```

### Search comments
```
GET /api/comments/search
```

---

## Parameters that matter

| Parameter | Notes |
|-----------|-------|
| `subreddit` | Required for scoped searches. No r/ prefix needed. |
| `title` | Keyword search in post titles. ⚠️ Only works when `author` or `subreddit` is also set. Fails on very high-traffic subreddits. |
| `body` | Keyword search in comment bodies. Same constraints as `title`. Works well with `subreddit`. |
| `query` | Searches both title and selftext. ⚠️ Returns 422 on high-traffic subreddits (CharacterAI, Replika) — use `title` or `body` instead. |
| `limit` | 1–100. Default 25. Use 50–100 for research sweeps. |
| `sort` | `asc` or `desc` by `created_utc`. |
| `after` / `before` | Date filter. Accepts ISO 8601 (`2024-01-01`) or epoch seconds. |
| `fields` | Comma-separated list to reduce response size. Common set: `title,selftext,score,id` for posts; `body,score,link_id` for comments. |

---

## Working query patterns

**Find positive/negative user experiences in a subreddit:**
```
/api/comments/search?subreddit=Replika&body=remembers+me&limit=50&sort=desc&fields=body,score,link_id
```

**Search for posts about a topic in a subreddit:**
```
/api/posts/search?subreddit=CharacterAI&title=memory&limit=50&sort=desc&fields=title,selftext,score,id
```

**Time-bounded sweep:**
```
/api/comments/search?subreddit=Replika&body=forgot&after=2024-01-01&before=2025-01-01&limit=100&fields=body,score
```

**Get full comment tree for a known post:**
```
/api/comments/tree?link_id=t3_<post_id>&limit=9999
```

---

## What doesn't work

- `query` param returns 422 on high-traffic subreddits. Use `body` for comments or `title` for posts instead.
- `title` and `body` keyword search is not supported for very active subreddits or users without a `subreddit` or `author` filter — always include at least one.
- Reddit.com, old.reddit.com, and the Reddit JSON API are all blocked for automated access. Don't try them.

---

## Rate limits

Free service. No auth required. If you get 429, wait — the `X-RateLimit-Reset` header says when. For large sweeps, use the monthly dump downloads instead of the API.

---

## Subreddits relevant to this project

| Subreddit | What it's good for |
|-----------|-------------------|
| `CharacterAI` | Companion memory complaints, model degradation reports, user frustration patterns |
| `Replika` | Positive memory experiences, what "being known" feels like to users, update-induced resets |
| `VoiceAIBots` | Creepiness/recall intrusiveness reports |
| `AICompanions` | Cross-product comparisons |

---

## How to call it

Use `webfetch` with the full URL. The API returns JSON directly.

```
webfetch("https://arctic-shift.photon-reddit.com/api/comments/search?subreddit=Replika&body=remembers&limit=50&fields=body,score,link_id")
```

Parse the `data` array in the response. Each item has the fields you requested. `link_id` is the post ID prefixed with `t3_` — useful for fetching the full thread with `/api/comments/tree`.

---

## Citation format

When noting findings in docs, cite as:

```
([r/SubredditName, Arctic Shift, YYYY](https://arctic-shift.photon-reddit.com))
```
