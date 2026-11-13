"""Material parameters and published device data.

Numbers in square brackets are the reference numbers used in the README and on the slides.
Values marked "assumed" are modelling choices, not measurements.
"""

# ---------------------------------------------------------------- PbS
EG_PBS = 0.41          # eV, bulk band gap at 300 K [6, 7]
M_STAR = 0.085         # m_e* = m_h*, units of m0; isotropic two-band value [18]
EPS_INF = 17.2         # high-frequency dielectric constant; enters only the Coulomb term
COULOMB_COEFF = 1.786  # electron–hole Coulomb coefficient of the 1s state in a sphere [5]
A_PBS = 0.5936         # nm, rock-salt lattice constant of galena [27]

# Empirical sizing curve E0(d) = Eg + 1 / (a d² + b d), d in nm, E in eV [7]
MOREELS_A = 0.0252     # eV⁻¹ nm⁻²
MOREELS_B = 0.283      # eV⁻¹ nm⁻¹

# Wavelengths of ST's quantum-dot image sensors [12]
ST_WAVELENGTHS_NM = (940.0, 1400.0)

# ---------------------------------------------------------------- other semiconductors
EG_SI = 1.12           # eV, Si at 300 K [22]
EG_INGAAS = 0.75       # eV, In0.53Ga0.47As at room temperature [24]

# ---------------------------------------------------------------- transport between dots
MOBILITY_FACTOR_PER_A = 2.6  # mobility gain per Å of shorter ligand, PbSe + alkanedithiols [19, 20]
BETA_SAM = 0.79              # Å⁻¹, tunnelling decay of alkanethiol monolayers [21]
PHI_SAM = 1.39               # eV, barrier height fitted together with BETA_SAM [21]
PHI_VAC = 4.5                # eV, typical metal work function for an STM vacuum gap (assumed)

# ---------------------------------------------------------------- devices
QD_PHOTODIODE = {           # PbS CQD photodiode, Vafaie et al. 2021 [23]
    "wavelength_nm": 1550.0,
    "eqe": 0.80,
    "responsivity_reported": 1.0,   # A/W
    "dark_current": 1.4e-7,         # A cm⁻², room temperature
    "dstar": 8e11,                  # Jones
    "gap": 0.80,                    # eV
}

INGAAS_FPA = {              # 1280×1024 InGaAs FPA, Zhang et al. 2021 [24]
    "wavelength_nm": 1550.0,
    "eqe": 0.88,
    "dark_current": 2.25e-9,        # A cm⁻² at 25 °C
    "temperature": 298.15,          # K
    "dstar": 1.1e13,                # Jones
    "gap": EG_INGAAS,               # eV
}

IMX990 = {                  # Sony IMX990 in the QHY990 camera [25]; pixel pitch [17]
    "dark_e_per_s": 64.6,           # electrons per second per pixel
    "pitch_um": 5.0,
    "temperature": 243.15,          # K (−30 °C)
}

ST_QE_1400 = 0.60           # quantum efficiency of ST's test photodiode at 1400 nm [11]

PIXEL_PITCH_UM = {          # sensors compared on the products slide
    "acuros": 15.0,         # onsemi Acuros CQD camera [26]
    "imx990": 5.0,          # Sony IMX990 InGaAs [17]
    "st": 1.62,             # ST QD-on-CMOS [10]
}
