import { NextRequest, NextResponse } from 'next/server';

// Proxy configuration for Docker backend
const BACKEND_URL = 'http://brant-api-1:3001';
const DOCKER_BACKEND_URL = 'http://brant-api-1:3001';

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const url = `${DOCKER_BACKEND_URL}/api/v1/${path}`;
  
  try {
    const response = await fetch(url, {
      headers: Object.fromEntries(request.headers.entries()),
    });
    
    const data = await response.text();
    
    return new NextResponse(data, {
      status: response.status,
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'application/json',
      },
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to backend' },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const url = `${DOCKER_BACKEND_URL}/api/v1/${path}`;
  
  try {
    // Handle FormData for file uploads
    const contentType = request.headers.get('content-type') || '';
    let body;
    
    if (contentType.includes('multipart/form-data')) {
      body = await request.formData();
    } else {
      body = await request.text();
    }
    
    const response = await fetch(url, {
      method: 'POST',
      body: body,
      headers: contentType.includes('multipart/form-data') 
        ? {} // Let fetch set the boundary
        : Object.fromEntries(request.headers.entries()),
    });
    
    const data = await response.text();
    
    return new NextResponse(data, {
      status: response.status,
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'application/json',
      },
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to backend' },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const url = `${DOCKER_BACKEND_URL}/api/v1/${path}`;
  
  try {
    const response = await fetch(url, {
      method: 'PUT',
      body: await request.text(),
      headers: Object.fromEntries(request.headers.entries()),
    });
    
    const data = await response.text();
    
    return new NextResponse(data, {
      status: response.status,
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'application/json',
      },
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to backend' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const url = `${DOCKER_BACKEND_URL}/api/v1/${path}`;
  
  try {
    const response = await fetch(url, {
      method: 'DELETE',
      headers: Object.fromEntries(request.headers.entries()),
    });
    
    const data = await response.text();
    
    return new NextResponse(data, {
      status: response.status,
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'application/json',
      },
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to backend' },
      { status: 500 }
    );
  }
}