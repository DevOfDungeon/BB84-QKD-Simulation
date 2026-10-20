import random

def measure(bit, prep_basis, meas_basis):
    """Same basis -> true bit. Different basis -> random 50/50 result."""
    return bit if prep_basis == meas_basis else random.randint(0, 1)

def bb84(n=1000, eve=False, seed=None):
    if seed is not None:
        random.seed(seed)

    # Alice: random bits and bases (0 = rectilinear +, 1 = diagonal x)
    alice_bits = [random.randint(0, 1) for _ in range(n)]
    alice_bases = [random.randint(0, 1) for _ in range(n)]
    photons = list(zip(alice_bits, alice_bases))

    # Eve: intercept-resend attack in random bases
    if eve:
        intercepted = []
        for bit, basis in photons:
            e_basis = random.randint(0, 1)
            e_bit = measure(bit, basis, e_basis)
            intercepted.append((e_bit, e_basis))  # resends in her own basis
        photons = intercepted

    # Bob: random bases
    bob_bases = [random.randint(0, 1) for _ in range(n)]
    bob_bits = [measure(b, pb, mb) for (b, pb), mb in zip(photons, bob_bases)]

    # Sifting: keep only positions where Alice's and Bob's bases matched
    keep = [i for i in range(n) if alice_bases[i] == bob_bases[i]]
    alice_key = [alice_bits[i] for i in keep]
    bob_key = [bob_bits[i] for i in keep]

    errors = sum(a != b for a, b in zip(alice_key, bob_key))
    qber = errors / len(keep) if keep else 0.0
    return alice_key, bob_key, qber

if __name__ == "__main__":
    for eve in (False, True):
        a, b, q = bb84(2000, eve=eve, seed=42)
        print(f"Eve={eve!s:5} | sifted key length={len(a)} | QBER={q:.1%}")
        print("  Alice key (first 20):", "".join(map(str, a[:20])))
        print("  Bob key   (first 20):", "".join(map(str, b[:20])))
        print("  Verdict:", "ABORT, eavesdropper detected" if q > 0.11 else "Key accepted")