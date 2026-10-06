/** @type {import('next').NextConfig} */
const nextConfig = {
  poweredByHeader: false,
  // The app shell (src/frontend/app.html) is read from disk by a route
  // handler, so tell Vercel's file tracer to ship it with the function.
  outputFileTracingIncludes: {
    "/": ["./src/frontend/**/*"],
    "/s/[token]": ["./src/frontend/**/*"],
    "/api/seed/projects": ["./db/projects_seed.json"],
  },
  async headers() {
    return [
      {
        // slide photos / fonts are content-addressed, safe to cache forever
        source: "/media/:path*",
        headers: [{ key: "Cache-Control", value: "public, max-age=31536000, immutable" }],
      },
    ];
  },
};

export default nextConfig;
