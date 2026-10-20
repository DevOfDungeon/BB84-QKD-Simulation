import random

from flask import Flask, jsonify, request
from qiskit import QuantumCircuit, transpile
from qiskit.providers.basic_provider import BasicSimulator

app = Flask(__name__, static_folder="web", static_url_path="")
sim = BasicSimulator()
MAX_PHOTONS = 200  # keeps responses fast; each photon is one Qiskit circuit


def encode(bit, basis):
    qc = QuantumCircuit(1, 1)
    if bit:
        qc.x(0)  # bit 1 -> |1>
    if basis:
        qc.h(0)  # diagonal basis
    return qc


def add_measurement(qc, basis):
    if basis:
        qc.h(0)  # rotate back into the measurement basis
    qc.measure(0, 0)
    return qc


def run_batch(circuits):
    result = sim.run(transpile(circuits, sim), shots=1).result()
    return [int(next(iter(result.get_counts(i)))) for i in range(len(circuits))]


def bb84_qiskit(n, eve):
    rnd = lambda: random.randint(0, 1)
    a_bits = [rnd() for _ in range(n)]
    a_bases = [rnd() for _ in range(n)]
    b_bases = [rnd() for _ in range(n)]
    e_bases = e_bits = None

    if eve:
        e_bases = [rnd() for _ in range(n)]
        e_circs = [add_measurement(encode(b, ab), eb)
                   for b, ab, eb in zip(a_bits, a_bases, e_bases)]
        e_bits = run_batch(e_circs)
        # Eve resends what she measured, prepared in her own basis
        b_circs = [add_measurement(encode(b, eb), bb)
                   for b, eb, bb in zip(e_bits, e_bases, b_bases)]
    else:
        b_circs = [add_measurement(encode(b, ab), bb)
                   for b, ab, bb in zip(a_bits, a_bases, b_bases)]

    b_bits = run_batch(b_circs)

    keep = [i for i in range(n) if a_bases[i] == b_bases[i]]
    errors = sum(a_bits[i] != b_bits[i] for i in keep)
    qber = errors / len(keep) if keep else 0.0

    return {
        "n": n, "eve": eve,
        "aBits": a_bits, "aBases": a_bases,
        "eBases": e_bases, "eBits": e_bits,
        "bBases": b_bases, "bBits": b_bits,
        "keep": keep, "errors": errors, "qber": qber,
    }


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/run")
def api_run():
    try:
        n = max(4, min(MAX_PHOTONS, int(request.args.get("n", 20))))
    except ValueError:
        n = 20
    eve = request.args.get("eve", "0") == "1"
    return jsonify(bb84_qiskit(n, eve))


if __name__ == "__main__":
    app.run(debug=True, port=5000)