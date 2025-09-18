import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:3001';

/**
 * A generic handler that proxies all requests (GET, POST, etc.)
 * from the Next.js frontend to the FastAPI backend.
 */
async function handler(req: NextRequest) {
  const { pathname, search } = new URL(req.url);
  // Remove the /api/proxy prefix to get the actual API path
  const apiPath = pathname.replace('/api/proxy', '');
  const backendUrl = `${BACKEND_URL}/api/v1${apiPath}${search}`;

  try {
    const response = await fetch(backendUrl, {
      method: req.method,
      headers: {
        ...req.headers,
        // The 'host' header must be updated to match the backend's expected host
        host: new URL(BACKEND_URL).host,
      },
      body: req.body,
      // @ts-ignore - duplex is required for streaming bodies
      duplex: 'half',
    });

    return response;
  } catch (error) {
    console.error('API proxy error:', error);
    return new NextResponse('Proxy error', { status: 500 });
  }
}

/**
 * Export the generic handler for all common HTTP methods.
 * This ensures consistent proxying behavior for the entire API.
 */
export { handler as GET };
export { handler as POST };
export { handler as PUT };
export { handler as DELETE };
export { handler as PATCH };