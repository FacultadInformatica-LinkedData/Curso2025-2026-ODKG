from flask import Flask, request, Response
import requests

app = Flask(__name__)

GRAPHDB_ENDPOINT = "http://127.0.0.1:7200/repositories/urban-sensors"

@app.route("/sparql", methods=["POST", "OPTIONS"])
def sparql():
    # Preflight CORS
    if request.method == "OPTIONS":
        resp = Response(status=204)
    else:
        # Leer la query que viene del navegador
        query = request.form.get("query", "")

        # Respetar el Accept del navegador (JSON para SELECT, Turtle para CONSTRUCT, etc.)
        accept_header = request.headers.get("Accept") or "application/sparql-results+json"

        headers = {
            "Accept": accept_header,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }

        # Reenviar a GraphDB
        r = requests.post(
            GRAPHDB_ENDPOINT,
            data={"query": query},
            headers=headers,
        )

        # Respuesta hacia el navegador
        resp = Response(r.content, status=r.status_code)
        if "content-type" in r.headers:
            resp.headers["Content-Type"] = r.headers["content-type"]

    # CORS: devolvemos exactamente el Origin que nos mandan (localhost:8000)
    origin = request.headers.get("Origin")
    resp.headers["Access-Control-Allow-Origin"] = origin or "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Accept"
    resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return resp


if __name__ == "__main__":
    app.run(host="localhost", port=9000, debug=True)
