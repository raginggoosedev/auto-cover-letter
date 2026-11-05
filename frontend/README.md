# Auto Cover Letter frontend

The React interface uses Vite for development, testing, and production builds.
See the [project README](../README.md) for architecture, configuration, API,
privacy, and full setup instructions.

```bash
npm ci
npm run dev
npm run test:ci
npm run build
```

Vite proxies `/api` requests to Flask at `http://localhost:5000` while the
development server is running.
