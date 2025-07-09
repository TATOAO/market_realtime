/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_MONITORING_URL: process.env.REACT_APP_MONITORING_URL || 'http://localhost:8001',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/:path*`,
      },
      {
        source: '/monitoring/:path*',
        destination: `${process.env.REACT_APP_MONITORING_URL || 'http://localhost:8001'}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig; 