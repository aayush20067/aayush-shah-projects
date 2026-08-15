import numpy as np
import matplotlib.pyplot as plt

# -------------------------
# SYSTEM PARAMETERS
# -------------------------
m1 = 0.285
k1 = 701.4

# frequency range (rad/s)
w = np.linspace(1, 100, 2000)

# -------------------------
# FUNCTION TO COMPUTE FRF
# -------------------------
def compute_frf(m2, k2, c2):
    X = []
    for wi in w:
        a11 = -m1*wi**2 + k1 + k2 + 1j*c2*wi
        a12 = -k2 - 1j*c2*wi
        a21 = -k2 - 1j*c2*wi
        a22 = -m2*wi**2 + k2 + 1j*c2*wi

        A = np.array([[a11, a12],
                      [a21, a22]])

        F = np.array([1, 0])
        X_sol = np.linalg.solve(A, F)

        X.append(abs(X_sol[0]))

    return np.array(X)

# =====================================================
# 1. DAMPING STUDY
# =====================================================

m2 = 0.055
k2 = 133.6

# ---- Plot 1: Undamped ----
plt.figure()
c2 = 0
X = compute_frf(m2, k2, c2)

plt.plot(w/(2*np.pi), X, label='zeta = 0')
plt.title("Undamped Response")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.grid()
plt.legend()
plt.savefig("python_damping_undamped.png", dpi=300)
plt.show()

# ---- Plot 2: Damped ----
zeta_vals = [0.02, 0.05, 0.1, 0.2]

plt.figure()
for z in zeta_vals:
    c2 = 2*z*np.sqrt(k2*m2)
    X = compute_frf(m2, k2, c2)
    plt.plot(w/(2*np.pi), X, label=f'zeta={z}')

plt.title("Effect of Damping")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.legend()
plt.grid()
plt.savefig("python_damping_study.png", dpi=300)
plt.show()

# =====================================================
# 2. MASS RATIO STUDY (WITH DAMPING)
# =====================================================

mu_vals = [0.05, 0.1, 0.2, 0.3]
zeta = 0.05

plt.figure()

for mu in mu_vals:
    m2 = mu * m1
    k2 = (k1/m1) * m2
    c2 = 2*zeta*np.sqrt(k2*m2)

    X = compute_frf(m2, k2, c2)
    plt.plot(w/(2*np.pi), X, label=f'mu={mu}')

plt.title("Effect of Mass Ratio (with damping)")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.legend()
plt.grid()
plt.savefig("python_mass_ratio.png", dpi=300)
plt.show()

# =====================================================
# 3. DEN HARTOG COMPARISON
# =====================================================

# =====================================================
# 3. DEN HARTOG COMPARISON (FIXED VERSION)
# =====================================================

# =====================================================
# 3. ABSORBER COMPARISON (CLEAN FINAL VERSION)
# =====================================================

# =====================================================
# 3. ABSORBER COMPARISON (FINAL CLEAN VERSION)
# =====================================================

mu = 0.1
m2 = mu * m1

# ---- Natural frequency ----
wn = np.sqrt(k1/m1)

# ---- Case 1: No absorber (baseline) ----
X_no_abs = []
for wi in w:
    X_no_abs.append(abs(1 / (-m1*wi**2 + k1)))
X_no_abs = np.array(X_no_abs)

# ---- Case 2: Absorber (no damping, slightly off tuning) ----
k2_basic = 0.9 * (k1/m1) * m2
c2_basic = 0

X_basic = compute_frf(m2, k2_basic, c2_basic)

# ---- Case 3: Den Hartog optimal ----
w_ratio = 1/(1+mu)
k2_opt = k1 * (w_ratio**2) * (m2/m1)

zeta_opt = np.sqrt(3*mu/(8*(1+mu)**3))
c2_opt = 2*zeta_opt*np.sqrt(k2_opt*m2)

X_opt = compute_frf(m2, k2_opt, c2_opt)

# ---- Plot ----
plt.figure()

plt.plot(w/(2*np.pi), X_no_abs, label="No absorber")
plt.plot(w/(2*np.pi), X_basic, label="Absorber (no damping)")
plt.plot(w/(2*np.pi), X_opt, label="Den Hartog optimal")

plt.axvline(wn/(2*np.pi), linestyle='--', label='Natural frequency')

plt.title("Absorber Performance Comparison")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.legend()
plt.grid()

plt.savefig("den_hartog_comparison.png", dpi=300)
plt.show()

print("Natural frequency (Hz):", wn/(2*np.pi))
print("Optimal damping ratio:", zeta_opt)