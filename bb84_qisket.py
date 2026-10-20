import random
from qiskit import QuantumCircuit, transpile
from qiskit.providers.basic_provider import BasicSimulator

sim = BasicSimulator()

def encode(bit, basis):
    qc = QuantumCircuit(1, 1)
    if bit:
        qc.x(0)       # bit 1 -> |1>
    if basis:
        qc.h(0)       # diagonal basis -> |+> or |->
    return qc

def add_measurement(qc, basis):
    if basis:
        qc.h(0)       # rotate back before measuring
    qc.measure(0, 0)
    return qc

def run_batch(circuits):
    result = sim.run(transpile(circuits, sim), shots=1).result()
    return [int(next(iter(result.get_counts(i)))) for i in range(len(circuits))]

def bb84_qiskit(n=200, eve=False):
    alice_bits = [random.randint(0, 1) for _ in range(n)]
    alice_bases = [random.randint(0, 1) for _ in range(n)]
    bob_bases = [random.randint(0, 1) for _ in range(n)]

    if eve:
        eve_bases = [random.randint(0, 1) for _ in range(n)]
        eve_circs = [add_measurement(encode(b, ab), eb)
                     for b, ab, eb in zip(alice_bits, alice_bases, eve_bases)]
        eve_bits = run_batch(eve_circs)
        # Eve resends what she measured, in her basis
        bob_circs = [add_measurement(encode(b, eb), bb)
                     for b, eb, bb in zip(eve_bits, eve_bases, bob_bases)]
    else:
        bob_circs = [add_measurement(encode(b, ab), bb)
                     for b, ab, bb in zip(alice_bits, alice_bases, bob_bases)]

    bob_bits = run_batch(bob_circs)

    keep = [i for i in range(n) if alice_bases[i] == bob_bases[i]]
    errors = sum(alice_bits[i] != bob_bits[i] for i in keep)
    return len(keep), errors / len(keep)

if __name__ == "__main__":
    for eve in (False, True):
        k, q = bb84_qiskit(300, eve)
        print(f"Eve={eve!s:5} | sifted={k} | QBER={q:.1%}")