"""Extra analysis for the BB84 report: QBER versus fraction of photons Eve intercepts,
and how the measured QBER varies with sample size. Pure Python + matplotlib."""
import random, statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def measure(bit, prep, meas):
    return bit if prep == meas else random.randint(0, 1)

def run(n, f_eve):
    """Eve intercepts each photon with probability f_eve (intercept-resend)."""
    keep = errors = 0
    for _ in range(n):
        bit, a = random.randint(0, 1), random.randint(0, 1)
        sb, sbasis = bit, a
        if random.random() < f_eve:
            eb = random.randint(0, 1)
            sb, sbasis = measure(bit, a, eb), eb
        b = random.randint(0, 1)
        out = measure(sb, sbasis, b)
        if a == b:
            keep += 1
            errors += out != bit
    return errors / keep if keep else 0.0

if __name__ == "__main__":
    random.seed(84)
    fs = [i / 10 for i in range(11)]
    qb = [run(40000, f) for f in fs]
    for f, q in zip(fs, qb):
        print(f"f={f:.1f}  QBER={q*100:5.2f}%  theory={25*f:5.2f}%")
    # sample-size study (all photons intercepted)
    for n in (100, 300, 1000, 5000):
        vals = [run(n, 1.0) for _ in range(300)]
        print(f"n={n}: mean={statistics.mean(vals)*100:.1f}% sd={statistics.pstdev(vals)*100:.1f}% min={min(vals)*100:.1f}% max={max(vals)*100:.1f}%")
    print("no Eve n=5000:", run(5000, 0.0))
    plt.figure(figsize=(6.2, 3.6), dpi=200)
    plt.plot([f*100 for f in fs], [25*f for f in fs], "--", color="#0b7fa5", label="Theory: 25% x f")
    plt.plot([f*100 for f in fs], [q*100 for q in qb], "o", color="#d9531e", label="Simulation (40,000 photons per point)")
    plt.axhline(11, color="#5a6b82", linewidth=1, linestyle=":")
    plt.text(1, 11.7, "11% abort threshold", color="#5a6b82", fontsize=8)
    plt.xlabel("Photons intercepted by Eve (%)"); plt.ylabel("QBER (%)")
    plt.grid(alpha=0.25); plt.legend(fontsize=8, loc="upper left"); plt.tight_layout()
    plt.savefig("qber_vs_eve.png")