#!/usr/bin/env python3
"""
Development server with no-cache headers
Prevents browser caching during development
"""
import http.server
import socketserver
from pathlib import Path

PORT = 8000

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler that sets no-cache headers for all files"""
    
    def end_headers(self):
        # Set no-cache headers
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging, or customize as needed
        pass

def main():
    """Start the development server"""
    import os
    os.chdir(Path(__file__).parent)
    
    with socketserver.TCPServer(("", PORT), NoCacheHTTPRequestHandler) as httpd:
        print(f"\n🚀 Development server running at http://localhost:{PORT}")
        print(f"📝 No-cache headers enabled - files will always reload\n")
        print(f"Press Ctrl+C to stop the server\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped\n")
            httpd.shutdown()

if __name__ == '__main__':
    main()

