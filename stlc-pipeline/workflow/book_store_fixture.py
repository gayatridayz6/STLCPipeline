"""Test-only localhost page for exercising the book-search UI harness."""

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer


PAGE = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Book search test fixture</title></head>
<body>
  <form id="search-form">
    <label for="search">Book title</label>
    <input id="search" type="search">
    <button id="submit" type="submit">Search</button>
  </form>
  <div class="details" hidden></div>
  <p class="empty" hidden>No books found</p>
  <script>
    const form = document.querySelector("#search-form");
    const details = document.querySelector(".details");
    const empty = document.querySelector(".empty");
    form.addEventListener("submit", event => {
      event.preventDefault();
      const title = document.querySelector("#search").value;
      const found = title === "Java Programming";
      details.hidden = !found;
      empty.hidden = found;
      details.textContent = found ? "Java Programming - Example Author" : "";
    });
  </script>
</body>
</html>
"""


class FixtureHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404, "Not found")
            return
        payload = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = HTTPServer(("127.0.0.1", args.port), FixtureHandler)
    print(f"Test-only fixture listening at http://127.0.0.1:{server.server_port}/", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
