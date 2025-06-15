import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

FIXTURE_PATH = (
    Path(__file__).parent.parent.parent / "e2e" / "fixtures" / "current_fixture.json"
)


class MockOpenAIHandler(BaseHTTPRequestHandler):
    # Shared state across requests
    response_index = 0
    cached_responses = None

    def _load_fixture(self):
        if not FIXTURE_PATH.exists():
            return None
        try:
            data = json.loads(FIXTURE_PATH.read_text())
            return data.get("responses", [])
        except json.JSONDecodeError:
            return None

    def do_POST(self):
        if self.path == "/v1/chat/completions":
            if MockOpenAIHandler.cached_responses is None:
                MockOpenAIHandler.cached_responses = self._load_fixture()

            responses = MockOpenAIHandler.cached_responses

            if not responses or MockOpenAIHandler.response_index >= len(responses):
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"No more mock responses available.")
                return

            response = responses[MockOpenAIHandler.response_index]
            response_body = json.dumps(response).encode()
            MockOpenAIHandler.response_index += 1

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)
            self.wfile.flush()
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    port = 8000
    server = HTTPServer(("localhost", port), MockOpenAIHandler)
    print(f"Mock server running at http://localhost:{port}")
    server.serve_forever()
