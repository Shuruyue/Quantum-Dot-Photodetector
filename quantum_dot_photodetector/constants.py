"""Physical constants in eV / nm units, rounded from CODATA 2018.

The validation suite compares each value with ``scipy.constants``.
"""

HB2_2M0 = 0.0380998      # ħ²/(2 m0), eV nm²
HB2_2M0_A = HB2_2M0 * 100  # ħ²/(2 m0), eV Å²
E2_4PIE0 = 1.439964      # e²/(4π ε0), eV nm
KB = 8.617333e-5         # Boltzmann constant, eV K⁻¹
HC = 1239.842            # h c, eV nm
Q = 1.602176634e-19      # elementary charge, C (exact in SI 2019)
