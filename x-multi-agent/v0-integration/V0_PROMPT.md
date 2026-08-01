Build a clean single-page Next.js UI for posting tweets to X account @Pzhise via our backend.

Requirements:
1. One text area where the user types natural language (Chinese or English) describing what to post.
2. Two buttons: "Preview" and "Post to X".
3. Preview calls POST /api/tweet with JSON { "prompt": "<user input>", "dryRun": true }.
4. Post calls POST /api/tweet with JSON { "prompt": "<user input>" }.
5. Show loading state, success/error, generated tweet text, and tweetUrl link when present.
6. Keep the first viewport simple: brand "Pzhisen", one headline "Post to @Pzhise", one short sentence, the form. No cards clutter, no purple gradient theme.
7. Include / copy these files from the repo if available:
   - app/api/tweet/route.ts (proxy to TWEET_AGENT_URL)
   - components/TweetComposer.tsx
8. Tell me to set env vars:
   - TWEET_AGENT_URL
   - TWEET_AGENT_TOKEN

Do not invent Twitter API keys in the frontend. All posting goes through /api/tweet only.
