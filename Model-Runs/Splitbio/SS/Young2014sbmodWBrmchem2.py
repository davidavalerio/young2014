# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 15:01:50 2019

@author: dvale
"""

#%% Load packages and determine the initial moles of relevant species

import pandas as pd
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import seaborn as sns

# Terrestrial fraction of global primary production from Field 1998
ft = .6
    
# Initial moles of combined isotopologues for relevant species
Os0 = 1 # O strat – initial moles, any small value works
O1Ds0 = 1 # O(1D) strat – initial moles, any small value works
O2s0 = 1 # O2 strat – initial moles, any small value works
CO2s0 = 4.8e15 # CO2 strat – initial moles, fixes mixing ratio of CO2
O3s0 = 1 # O3 strat – initial moles, any small value works
O2t0 = 1 # O2 trop – initial moles, any small value works
CO2t0 = 4.8e16 # CO2 trop – intial moles (270 ppm), 400ppm = 7.2e16
O2b0 = 1.83e19 # O2 bio total – from H2O initial moles, not used when H2O is infinite
O2g0 = 2e17 # O2 geo – moles available for oxidation by O2 trop

# Number of oxygens in each species
isok1 = pd.Series(np.array([2, 1, 2, 1, 2, 2, 1, 2, 2]), 
                  index = np.array(['Os', 'O1Ds', 'O2s', 'CO2s', 'O3s', 'O2t',
                                    'CO2t','O2b', 'O2g']))

# Multiplier for converting atomic ratios to isotopologue ratios for each species
isok2 = pd.Series(np.array([1, 1, 2, 1, 3, 2, 1, 2, 2]), 
                  index = np.array(['Os', 'O1Ds', 'O2s', 'CO2s', 'O3s', 'O2t',
                                    'CO2t','O2b', 'O2g']))

# Mole fraction/isotopic ratio used in Young 2014 Fortran Code 

# Q represents 18O, X represents 17O
rQ = 0.002044928
rX = 0.000370894

# SMOW
# =============================================================================
# rQ = 0.0020052
# rX = 0.0003799
# =============================================================================

# Fractional abundance of 18O and 17O from isotope ratios
def frac(R1, R2):
    rZ = R1 / (1 + R1 + R2)
    return rZ

# Calculate 18O/16O and 17O/16O ratios for each species
# Z is either 18O (Q) or 17O (X)
def xxZ(isok2, rZ):
    xxZ = (isok2 * rZ) / (isok2 * rQ + isok2 * rX + 1)
    return xxZ

for species in isok2:
    xxQ = xxZ(isok2, rQ)
    xxX = xxZ(isok2, rX)
    
# Calculate initial moles of species with Q and X using isotopologue ratios
Qs0 = xxQ[0] * Os0 # Q strat - initial moles
Xs0 = xxX[0] * Os0 # X strat - initial moles
Q1Ds0 = xxQ[1] * O1Ds0 # Q1D strat - inital moles
X1Ds0 = xxX[1] * O1Ds0 # X1D strat - intial moles
OQs0 = xxQ[2] * O2s0 # OQ strat - inital moles
OXs0 = xxX[2] * O2s0 # OX strat - initial moles
COQs0 = xxQ[3] * CO2s0 # COQ strat - initial moles
COXs0 = xxX[3] * CO2s0 # COX strat - initial moles
OOQs0 = xxQ[4] * O3s0 # OOQ strat - initial moles
OOXs0 = xxX[4] * O3s0 # OOX strat - initial moles
OQt0 = xxQ[5] * O2t0 # OQ trop - initial moles
OXt0 = xxX[5] * O2t0 # OX trop - initial moles
COQt0 = xxQ[6] * CO2t0 # COQ trop - initial moles
COXt0 = xxX[6] * CO2t0 # COX trop - initial moles
OQb0 = xxQ[7] * O2b0 # OQ bio - initial moles
OXb0 = xxX[7] * O2b0 # OX bio - initial moles
OQg0 = xxQ[8] * O2g0 # OQ geo - initial moles
OXg0 = xxX[8] * O2g0 # OX geo - initial moles

# Initial moles of common isotopologues (i.e. no Q or X)
Os0 = Os0 - Qs0 - Xs0 # O strat - initial moles
O1Ds0 = O1Ds0 - Q1Ds0 - X1Ds0 # O1D strat - initial moles
O2s0 = O2s0 - OQs0 - OXs0 # O2 strat - initial moles
CO2s0 = CO2s0 - COQs0 - COXs0 # CO2 strat - inital moles
O3s0 = O3s0 - OOQs0 - OOXs0 # O3 strat - initial moles
O2t0 = O2t0 - OQt0 - OXt0 # O2 strat - initial moles
CO2t0 = CO2t0 - COQt0 - COXt0 # CO2 strat - initial moles
O2b0 = O2b0 - OQb0 - OXb0 # O2 bio - initial moles
O2g0 = O2g0 - OQg0 - OXg0 # O2 geo - initial moles

#%% Constants relevant to calculations

# Fractionation factors
tequil = 0.528 # nominal TOI equilibration slope
tevap0 = 0.520 # original evapotranspiration theta from Young2014
isowater = 1.00525 # tuned photosynthesis source water composition from Young 2014
alphari = 1 / 1.0182 # isotopic fractionation due to respiration
#alphar = 1 / isowater * alphari # Calculated base fractionation
#alphar = 0.9770279689 # from Young 2014 Fortran code 
#alphart = ft * alphar # original from Young2014
#alpharm = (1 - ft) * alphar # original from Young2014
alphaCO2H2O = 1.0413 # from Beck et al. 2005

# Updated fractionation factors
tresp = 0.5149 # global average oxygen uptake theta consistent with Wostbrock2020
tevap = 0.519 # evapotranspiration theta from Landais2006
tphoto = 0.525 # photosynthetic theta from LuzBarkan2011
isoevap = 1.006825 # isotopic enrichment of water from evapotranspiration from Young2014
isophoto = 1.0029 # isotopic enrichment of photosynthetic O2 from Eisenstadt 2011
alphart = 1 / isoevap * alphari  # terrestrial respiration fractionation factor
alpharm = 1 / isophoto * alphari # marine respiration fractionation factor

# Moles of air in atmosphere from Young 2014
airs = 1.8e19 # moles of air in the stratosphere
airt = 1.8e20 # moles of air in the troposphere is about 1/10 that of the stratosphere

# Volume of stratosphere and troposphere in cm^3
vs = 2.8e25 # volume of stratosphere
vt = vs * 10 # volume of troposphere is 1/10 that of the stratosphere

# Constants for calculating reaction rates
secyear = 31536000 # number of seconds in a year
avo = 6.0221409e23 # Avogadro's number

# Molar masses of oxygen isotopes and carbon from PubChem
mO = 15.994915 # molar mass of oxygen
mX = 16.999131 # molar mass of oxygen-17
mQ = 17.99916  # molar mass of oxygen-18
mC = 12 # molar mass of carbon


#%% Assign reaction rates  from initial spreadsheet

# Equations used to calculate reaction rates

# Reduced mass equation
def rm(m1, m2):
    rm = (m1 * m2) / (m1 + m2)
    return rm

# Convert reaction rate from units of cm^3/s to 1 / (mol yr)
def tomol(cm3s):
    tomol = cm3s * secyear * (avo / vs)
    return tomol

# Low pressure limit rate constant calculation from JPL 19-5
def lpk(ko298, T, n):
    k = ko298 * (T / 298) ** (-1 * n)
    return k;

# Arrhenius expression from JPL 19-5
def Arr(A, T, ER):
    k = A * np.exp(-1 * ER * (1 / T))
    return k;

# Rate constants for transport between boxes
# 1 - troposphere, 2 - biosphere/hydrosphere, 3 - geosphere, 4 - stratosphere
# k12 means 1 (trop) -> 2 (bio/hydro) and similarly for others
k12 = 0.0008 # respiration rate constant yr^-1
k12t = ft * k12 # respiration rate constant from bio terrestrial yr^-1
k12m = (1 - ft) * k12 # respiration rate constant from bio marine yr^-1
k21 = 0.00165 # photosynthesis rate constant yr^-1
k21t = ft * k21 # photosynthesis rate constant from bio terrestrial yr^-1
k21m = (1 - ft) * k21 # photosynthesis rate constant from bio marine yr^-1
k13 = 6e-07 # oxidation rate constant yr^-1
k31 = 5e-05 # organic burial rate constant yr^-1
k23 = 1.75e-05 # organic detritus delivery from biosphere to oceans yr^-1
k23t = ft * k23 # organic detritus delivery from terrestrial biosphere to oceans yr^-1
k23m = (1 - ft) * k23 # organic detritus delivery from marine biosphere to oceans yr^-1
k41 = 1 # stat-trop mixing rate constant yr^-1
k14 = 0.1 # trop-strat mixing rate constant yr^-1

# Rate constants for all relevant reactions in mol/yr from initial spreadsheet
KMIFo = 1.065 # MIF for O3 formation
K1o = 3e-5 # O2 + PHO -> O + O mol/yr
K2o = K1o # OQ + PHO -> Q + O mol/yr
K3o = K1o # OX + PHO -> X + O mol/yr
K4o = 7.0931893e-10 # O2 + O -> O3 mol/yr
K5o = KMIFo * K4o # O2 + Q -> OOQ mol/yr
K6o = KMIFo * K4o # O2 + X -> OOX mol/yr
K7o = KMIFo * K4o # OQ + O -> OOQ mol/yr
K8o = KMIFo * K4o # OX + O -> OOX mol/yr
K9o = 10000 # O3 + PHO -> O2 + O mol/yr
K10o = K9o * (1/3) # OOQ + PHO -> O2 + mol/yr
K11o = K9o * (2/3) # OOQ + PHO -> OQ + O mol/yr
K12o = K9o * (1/3) # OOX + PHO -> O2 + X mol/yr
K13o = K9o * (2/3) # OOX + PHO -> OX + O mol/yr
K14o = 15768 # O3 + PHO -> O2 + O1D mol/yr
K15o = K14o * (1/3) # OOQ + PHO -> O2 + Q1D mol/yr
K16o = K14o * (2/3) # OOQ + PHO -> OQ + O1D mol/yr
K17o = K14o * (1/3) # OOX + PHO -> O2 + X1D mol/yr
K18o = K14o * (2/3) # OOX + PHO -> OX + O1D mol/yr
K19o = 4.6548631e-10 # O3 + O -> O2 + O2 mol/yr
K20o = K19o # OOQ + O -> O2 + OQ mol/yr
K21o = K19o # OOX + O -> O2 + OX mol/yr
K22o = K19o # O3 + Q -> O2 + OQ mol/yr
K23o = K19o # O3 + X -> O2 + OX mol/yr
K24o = 8.139058e-05 # O3 + O1D -> O2 + O2 mol/yr
K25o = K24o * (1/2)  # OOQ + O1D -> O2 + OQ mol/yr
K26o = K24o * (1/2) # OOX + O1D -> O2 + OX mol/yr
K27o = K24o * (1/2) # O3 + Q1D -> O2 + OQ mol/yr
K28o = K24o * (1/2) # O3 + X1D -> O2 + OX mol/yr
K29o = K24o * (1/2) # O3 + O1D -> O2 + O + O mol/yr
K30o = K24o * (1/2) # OOQ + O1D -> O2 + O + Q mol/yr
K31o = K24o * (1/2) # OOQ + O1D -> OQ + O + O mol/yr
K32o = K24o * (1/2) # OOX + O1D -> O2 + O + X mol/yr
K33o = K24o * (1/2) # OOX + O1D -> OX + O + O mol/yr
K34o = K24o * (1/2) # O3 + Q1D -> O2 + O + Q mol/yr
K35o = K24o * (1/2) # O3 + Q1D -> OQ + O + O mol/yr
K36o = K24o * (1/2) # O3 + X1D -> O2 + O + X mol/yr
K37o = K24o * (1/2) # O3 + X1D -> OX + O + O mol/yr
K38o = 1.4e-4 # O2 + O1D -> O2 + O mol/yr
K39o = K38o # O2 + Q1D -> O2 + Q mol/yr
K40o = 0 # O2 + Q1D -> OQ + O mol/yr
K41o = K38o # O2 + X1D -> O2 + X mol/yr
K42o = 0 # O2 + X1D -> OX + O mol/yr
K43o = 1.35651e-10 # O2 + Q -> OQ + O mol/yr
K44o = K43o * (1/2) # OQ + O -> O2 + Q mol/yr
K45o = K43o # O2 + X -> OX + O mol/yr
K46o = K43o * (1/2) # OX + O -> O2 + X mol/yr
K47o = 3.022982e-05 # CO2 + O1D -> CO2 + O mol/yr
K48o = 1.4484581e-05 # CO2 + Q1D -> CO2 + Q mol/yr
K49o = 1.4484581e-05 # CO2 + Q1D -> COQ + O mol/yr
K50o = 1.5026874e-05 # COQ + O1D -> CO2 + Q mol/yr
K51o = 1.5026874e-05 # COQ + O1D -> COQ + O mol/yr
K52o = 1.4783854e-05 # CO2 + X1D -> CO2 + X mol/yr
K53o = 1.4783854e-05 # CO2 + X1D -> COX + O mol/yr
K54o = 1.5069884e-05 # COX + O1D -> CO2 + X mol/yr
K55o = 1.5069884e-05 # COX + O1D -> COX + O mol/yr

# Compiled original rate constants
Kod = np.array([KMIFo, K1o, K2o, K3o, K4o, K5o, K6o, K7o, K8o, K9o, K10o,
                K11o, K12o, K13o, K14o, K15o, K16o, K17o, K18o, K19o, K20o,
                K21o, K22o, K23o, K24o, K25o, K26o, K27o, K28o, K29o, K30o,
                K31o, K32o, K33o, K34o, K35o, K36o, K37o, K38o, K39o, K40o,
                K41o, K42o, K43o, K44o, K45o, K46o, K47o, K48o, K49o, K50o,
                K51o, K52o, K53o, K54o, K55o])
Koi = np.array(['KMIFo', 'K1o', 'K2o', 'K3o', 'K4o', 'K5o', 'K6o', 'K7o',
                'K8o', 'K9o', 'K10o', 'K11o', 'K12o', 'K13o', 'K14o', 'K15o',
                'K16o', 'K17o', 'K18o', 'K19o', 'K20o', 'K21o', 'K22o',
                'K23o', 'K24o', 'K25o', 'K26o', 'K27o', 'K28o', 'K29o',
                'K30o', 'K31o', 'K32o', 'K33o', 'K34o', 'K35o', 'K36o',
                'K37o', 'K38o', 'K39o', 'K40o', 'K41o', 'K42o', 'K43o',
                'K44o', 'K45o', 'K46o', 'K47o', 'K48o', 'K49o', 'K50o',
                'K51o', 'K52o', 'K53o', 'K54o', 'K55o'])
Ko = pd.DataFrame(Kod, Koi)

#%% Calculate reaction rates without reduced mass scaling and most recent NIST values
KMIF = 1.065 # MIF for O3 formation
K1 = 1.109e-12 * secyear # O2 + PHO -> O + O 1/(yr mol)
K2 = K1 # OQ + PHO -> Q + O 1/(yr mol)
K3 = K1 # OX + PHO -> X + O 1/(yr mol)
k4i = (lpk(6.1e-34, 220, 2.5) * 8.3e17)
K4 = tomol(k4i) # O2 + O -> O3 1/(yr mol)
K5 = KMIF * K4 # O2 + Q -> OOQ 1/(yr mol)
K6 = KMIF * K4 # O2 + X -> OOX 1/(yr mol)
K7 = KMIF * K4 # OQ + O -> OOQ 1/(yr mol)
K8 = KMIF * K4 # OX + O -> OOX 1/(yr mol)
K9 = 2.96e-4 * secyear # O3 + PHO -> O2 + O 1/(yr mol)
K10 = K9 * (1/3) # OOQ + PHO -> O2 + Q 1/(yr mol)
K11 = K9 * (2/3) # OOQ + PHO -> OQ + O 1/(yr mol)
K12 = K9 * (1/3) # OOX + PHO -> O2 + X 1/(yr mol)
K13 = K9 * (2/3) # OOX + PHO -> OX + O 1/(yr mol)
K14 = 5.01e-4 * secyear # O3 + PHO -> O2 + O1D 1/(yr mol)
K15 = K14 * (1/3) # OOQ + PHO -> O2 + Q1D 1/(yr mol)
K16 = K14 * (2/3) # OOQ + PHO -> OQ + O1D 1/(yr mol)
K17 = K14 * (1/3) # OOX + PHO -> O2 + X1D 1/(yr mol)
K18 = K14 * (2/3) # OOX + PHO -> OX + O1D 1/(yr mol)
k19i = Arr(8e-12, 220, 2060)
K19 = tomol(k19i) # O3 + O -> O2 + O2 mol/yr
K20 = K19 # OOQ + O -> O2 + OQ 1/(yr mol)
K21 = K19 # OOX + O -> O2 + OX 1/(yr mol)
K22 = K19 # O3 + Q -> O2 + OQ 1/(yr mol)
K23 = K19 # O3 + X -> O2 + OX 1/(yr mol)
k24i = Arr(2.4e-10, 220, 0)
K24 = tomol(k24i) * (1/2) # O3 + O1D -> O2 + O2 1/(yr mol)
K25 = K24 * (1/2) # OOQ + O1D -> O2 + OQ 1/(yr mol)
K26 = K24 * (1/2) # OOX + O1D -> O2 + OX 1/(yr mol)
K27 = K24 * (1/2) # O3 + Q1D -> O2 + OQ 1/(yr mol)
K28 = K24 * (1/2) # O3 + X1D -> O2 + OX 1/(yr mol)
K29 = K24 * (1/2) # O3 + O1D -> O2 + O + O 1/(yr mol)
K30 = K24 * (1/2) # OOQ + O1D -> O2 + O + Q 1/(yr mol)
K31 = K24 * (1/2) # OOQ + O1D -> OQ + O + O 1/(yr mol)
K32 = K24 * (1/2) # OOX + O1D -> O2 + O + X 1/(yr mol)
K33 = K24 * (1/2) # OOX + O1D -> OX + O + O 1/(yr mol)
K34 = K24 * (1/2) # O3 + Q1D -> O2 + O + Q 1/(yr mol)
K35 = K24 * (1/2) # O3 + Q1D -> OQ + O + O 1/(yr mol)
K36 = K24 * (1/2) # O3 + X1D -> O2 + O + X 1/(yr mol)
K37 = K24 * (1/2) # O3 + X1D -> OX + O + O 1/(yr mol)
k38i = Arr(3.3e-11, 220, -55)
K38 = tomol(k38i) * (0.78 + 0.21) / 0.21 # O2 + O1D -> O2 + O mol/yr
K39 = K38 # O2 + Q1D -> O2 + Q 1/(yr mol)
K40 = 0 # O2 + Q1D -> OQ + O 1/(yr mol)
K41 = K38 # O2 + X1D -> O2 + X 1/(yr mol)
K42 = 0 # O2 + X1D -> OX + O 1/(yr mol)
K43 = tomol(2.7e-12 * (220/300) ** 0.9) # O2 + Q -> OQ + O 1/(yr mol)
#K43 = K43o
K44 = K43 * (1/2) # OQ + O -> O2 + Q 1/(yr mol)
K45 = K43 # O2 + X -> OX + O 1/(yr mol)
K46 = K43 * (1/2) # OX + O -> O2 + X 1/(yr mol)
k47i = Arr(7.5e-11, 220, -115)
K47 = tomol(k47i) # CO2 + O1D -> CO2 + O 1/(yr mol)
#K47 = K47o
K48 = K47 * (1/3) # CO2 + Q1D -> CO2 + Q 1/(yr mol)
#K48 = K48o
K49 = K47 * (2/3) # CO2 + Q1D -> COQ + O 1/(yr mol)
#K49 = K49o
K50 = K47 * (1/3) # COQ + O1D -> CO2 + Q 1/(yr mol)
#K50 = K50o
K51 = K47 * (2/3) # COQ + O1D -> COQ + O 1/(yr mol)
#K51 = K51o
K52 = K47 * (1/3) # CO2 + X1D -> CO2 + X 1/(yr mol)
#K52 = K52o
K53 = K47 * (2/3) # CO2 + X1D -> COX + O 1/(yr mol)
#K53 = K53o
K54 = K47 * (1/3) # COX + O1D -> CO2 + X 1/(yr mol)
#K54 = K54o
K55 = K47 * (2/3) # COX + O1D -> COX + O 1/(yr mol)
#K55 = K55o

# Compiled calculated reaction rates
Kcd = np.array([KMIF, K1, K2, K3, K4, K5, K6, K7, K8, K9, K10,
                K11, K12, K13, K14, K15, K16, K17, K18, K19, K20,
                K21, K22, K23, K24, K25, K26, K27, K28, K29, K30,
                K31, K32, K33, K34, K35, K36, K37, K38, K39, K40,
                K41, K42, K43, K44, K45, K46, K47, K48, K49, K50,
                K51, K52, K53, K54, K55])
Ki = np.array(['KMIF', 'K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7',
                'K8', 'K9', 'K10', 'K11', 'K12', 'K13', 'K14', 'K15',
                'K16', 'K17', 'K18', 'K19', 'K20', 'K21', 'K22',
                'K23', 'K24', 'K25', 'K26', 'K27', 'K28', 'K29',
                'K30', 'K31', 'K32', 'K33', 'K34', 'K35', 'K36',
                'K37', 'K38', 'K39', 'K40', 'K41', 'K42', 'K43',
                'K44', 'K45', 'K46', 'K47', 'K48', 'K49', 'K50',
                'K51', 'K52', 'K53', 'K54', 'K55'])

# Original hydrosphere rate constants (assuming infinite reservoir)
kr9o = 0.00213987 # CO2 + H2Q -> COQ + H2O  1/(yr mol)
#kr9o = 0.000930443
kr10o = 1 # COQ + H2O -> CO2 + H2Q 1/(yr mol)
#kr10o = 0.4370797 
kr11o = 0.00037989 # CO2 + H2X -> COX + H2O 1/(yr mol)
#kr11o = 0.00016875677 
kr12o = 1 # COX + H2O -> CO2 + H2X 1/(yr mol)
#kr12o = 0.44544841

# Hydrosphere multipliers from original model
kr9x = kr9o / (alphaCO2H2O * isowater * rQ)
kr11x = kr11o / (alphaCO2H2O ** tequil * isowater ** tevap0 * rX)

# Splitbio hydrosphere rate constants for base model
kr10t = ft * kr10o # COQ + H2O -> CO2 + H2Q 1/(yr mol) terrestrial
kr10m = (1 - ft) * kr10o # COQ + H2O -> CO2 + H2Q 1/(yr mol) marine
kr12t = ft * kr12o # COX + H2O -> CO2 + H2X 1/(yr mol) terrestrial 
kr12m = (1 - ft) * kr12o # COX + H2O -> CO2 + H2X 1/(yr mol) marine

# Splitbio hydrosphere rate constants for updated model
kr9t = ft * kr9x * alphaCO2H2O * isoevap * rQ # CO2 + H2Q -> COQ + H2O 1/(yr mol) terrestrial
kr9m = (1 - ft) * kr9x * alphaCO2H2O * isophoto * rQ # CO2 + H2Q -> COQ + H2O 1/(yr mol) marine
kr11t = ft * kr11x  * alphaCO2H2O ** tequil * isoevap ** tevap * rX # CO2 + H2X -> COX + H2O 1/(yr mol) terrestrial
kr11m = (1 - ft) * kr11x * alphaCO2H2O ** tequil * isophoto ** tphoto * rX # COX + H2O -> CO2 + H2X 1/(yr mol) marine

#%% Solve the system of differential equations

# Function containing all the ODEs
def f(y, t):
    Osi = y[0]
    Xsi = y[1]
    O1Dsi = y[2]
    Qsi = y[3] 
    X1Dsi = y[4]
    Q1Dsi = y[5]
    O2si = y[6]
    OXsi = y[7]
    OQsi = y[8]
    CO2si = y[9]
    COXsi = y[10]
    COQsi = y[11]
    O3si = y[12]
    OOXsi = y[13]
    OOQsi = y[14]
    O2ti = y[15]
    OQti = y[16]
    OXti = y[17]
    CO2ti = y[18]
    COQti = y[19]
    COXti = y[20]
    O2bi = y[21]
    OQbi = y[22]
    OXbi = y[23]
    O2gi = y[24]
    OQgi = y[25]
    OXgi = y[26]
    
    # k(species)I represents input flux, k(species)O represents output flux
    
    # Stratosphere ODEs
    
    # O Stratosphere
    kOsI = (2 * K1 * O2si + K2 * OQsi + K3 * OXsi + K9 * O3si + K11 * OOQsi +
            K13 * OOXsi + 2 * K29 * O3si * O1Dsi + K30 * OOQsi * O1Dsi +
            2 * K31 * OOQsi * O1Dsi + K32 * OOXsi * O1Dsi +
            2 * K33 * OOXsi * O1Dsi + K34 * O3si * Q1Dsi +
            2 * K35 * O3si * Q1Dsi + K36 * O3si * X1Dsi +
            2 * K37 * O3si * X1Dsi + K38 * O2si * O1Dsi +
            K40 * O2si * Q1Dsi + K42 * O2si * X1Dsi + K43 * O2si * Qsi +
            K45 * O2si * Xsi + K47 * CO2si * O1Dsi + K49 * CO2si * Q1Dsi +
            K51 * COQsi * O1Dsi + K53 * CO2si * X1Dsi + K55 * COXsi * O1Dsi)
    kOsO = (K4 * O2si + K7 * OQsi + K8 * OXsi + K19 * O3si + K20 * OOQsi +
            K21 * OOXsi + K44 * OQsi + K46 * OXsi)
    dOs = kOsI - Osi * kOsO
    
    # X (17O) Stratosphere 
    kXsI = (K3 * OXsi + K12 * OOXsi + K32 * OOXsi * O1Dsi +
            K36 * O3si * X1Dsi + K41 * O2si * X1Dsi + K46 * OXsi * Osi +
            K52 * CO2si * X1Dsi + K54 * COXsi * O1Dsi)
    kXsO = (K6 * O2si + K23 * O3si + K45 * O2si)
    dXs = kXsI - Xsi * kXsO
    
    # Q (18O) Stratosphere
    kQsI = (K2 * OQsi + K10 * OOQsi + K30 * OOQsi * O1Dsi +
            K34 *  O3si * Q1Dsi + K39 * O2si * Q1Dsi + K44 * OQsi * Osi +
            K48 * CO2si * Q1Dsi + K50 * COQsi * O1Dsi)
    kQsO = (K5 * O2si + K22 * O3si + K43 * O2si)
    dQs = kQsI - Qsi * kQsO
    
    # O(1D) Stratosphere
    kO1DsI = (K14 * O3si + K16 * OOQsi + K18 * OOXsi)
    kO1DsO = (K24 * O3si + K25 * OOQsi + K26 * OOXsi + K29 * O3si +
              K30 * OOQsi + K31 * OOQsi + K32 * OOXsi + K33 * OOXsi +
              K38 * O2si + K47 * CO2si + K50 * COQsi + K51 * COQsi +
              K54 * COXsi + K55 * COXsi)
    dO1Ds = kO1DsI - O1Dsi * kO1DsO    
    
    # X(1D) (17O(1D)) Stratosphere
    kX1DsI = (K17 * OOXsi)
    kX1DsO = (K28 * O3si + K36 * O3si + K37 * O3si + K41 * O2si +
              K42 * O2si + K52 * CO2si + K53 * CO2si)
    dX1Ds = kX1DsI - X1Dsi * kX1DsO
    
    # Q(1D) (18O(1D)) Stratosphere
    kQ1DsI = (K15 * OOQsi)
    kQ1DsO = (K27 * O3si + K34 * O3si + K35 * O3si + K39 * O2si +
              K40 * O2si + K48 * CO2si + K49 * CO2si)
    dQ1Ds = kQ1DsI - Q1Dsi * kQ1DsO
    
    # O2 Stratosphere
    kO2sI = (K9 * O3si + K10 * OOQsi + K12 * OOXsi + K14 * O3si +
             K15 * OOQsi + K17 * OOXsi + 2 * K19 * O3si * Osi +
             K20 * OOQsi * Osi + K21 * OOXsi * Osi + K22 * O3si * Qsi +
             K23 * O3si * Xsi + 2 * K24 * O3si * O1Dsi +
             K25 * OOQsi * O1Dsi + K26 * OOXsi * O1Dsi +
             K27 * O3si * Q1Dsi + K28 * O3si * X1Dsi + K29 * O3si * O1Dsi +
             K30 * OOQsi * O1Dsi + K32 * OOXsi * O1Dsi + K34 * O3si * Q1Dsi +
             K36 * O3si * X1Dsi + K38 * O2si * O1Dsi + K39 * O2si * Q1Dsi +
             K41 * O2si * X1Dsi + K44 * OQsi * Osi + K46 * OXsi * Osi +
             k14 * O2ti)
    kO2sO = (K1 + K4 * Osi + K5 * Qsi + K6 * Xsi + K38 * O1Dsi +
             K39 * Q1Dsi + K40 * Q1Dsi + K41 * X1Dsi + K42 * X1Dsi +
             K43 * Qsi + K45 * Xsi + k41)
    dO2s = kO2sI - O2si * kO2sO
    
    # OX (O17O) Stratosphere
    kOXsI = (K13 * OOXsi + K18 * OOXsi + K21 * OOXsi * Osi +
             K23 * O3si * Xsi + K26 * OOXsi * O1Dsi + K28 * O3si * X1Dsi +
             K33 * OOXsi * O1Dsi + K37 * O3si * X1Dsi + K42 * O2si * X1Dsi +
             K45 * O2si * Xsi + k14 * OXti)
    kOXsO = (K3 + K8 * Osi + K46 * Osi + k41)
    dOXs = kOXsI - OXsi * kOXsO
    
    # OQ (O18O) Stratosphere
    kOQsI = (K11 * OOQsi + K16 * OOQsi + K20 * OOQsi * Osi +
             K22 * O3si * Qsi + K25 * OOQsi * O1Dsi + K27 * O3si * Q1Dsi +
             K31 * OOQsi * O1Dsi + K35 *  O3si * Q1Dsi + K40 * O2si * Q1Dsi +
             K43 * O2si * Qsi + k14 * OQti)
    kOQsO = (K2 + K7 * Osi + K44 * Osi + k41)
    dOQs = kOQsI - OQsi * kOQsO
    
    # CO2 Stratosphere
    kCO2sI = (K47 * CO2si * O1Dsi + K48 * CO2si * Q1Dsi + K50 * COQsi * O1Dsi +
              K52 * CO2si * X1Dsi + K54 * COXsi * O1Dsi + k14 * CO2ti)
    kCO2sO = (K47 * O1Dsi + K48 * Q1Dsi + K49 * Q1Dsi + K52 * X1Dsi +
              K53 * X1Dsi + k41)
    dCO2s = kCO2sI - CO2si * kCO2sO
    
    # COX (CO17O) Stratosphere
    kCOXsI = (K53 * CO2si * X1Dsi + K55 * COXsi * O1Dsi + k14 * COXti)
    kCOXsO = (K54 * O1Dsi + K55 * O1Dsi + k41)
    dCOXs = kCOXsI - COXsi * kCOXsO
    
    # COQ (CO18O) Stratosphere
    kCOQsI = (K49 * CO2si * Q1Dsi + K51 * COQsi * O1Dsi + k14 * COQti)
    kCOQsO = (K50 * O1Dsi + K51 * O1Dsi + k41)
    dCOQs = kCOQsI - COQsi * kCOQsO
    
    # O3 Stratosphere
    kO3sI = (K4 * O2si * Osi)
    kO3sO = (K9 + K14 + K19 * Osi + K22 * Qsi + K23 * Xsi +
             K24 * O1Dsi + K27 * Q1Dsi + K28 * X1Dsi + K29 * O1Dsi +
             K34 * Q1Dsi + K35 * Q1Dsi + K36 * X1Dsi + K37 * X1Dsi)
    dO3s = kO3sI - O3si * kO3sO
    
    # OOX (OO17O) Stratosphere
    kOOXsI = (K6 * O2si * Xsi + K8 * OXsi * Osi)
    kOOXsO = (K12 + K13 + K17 + K18 + K21 * Osi + K26 * O1Dsi +
              K32 * O1Dsi + K33 * O1Dsi)
    dOOXs = kOOXsI - OOXsi * kOOXsO
    
    # OOQ (OO18O) Stratosphere
    kOOQsI = (K5 * O2si * Qsi + K7 * OQsi * Osi)
    kOOQsO = (K10 + K11 + K15 + K16 + K20 * Osi + K25 * O1Dsi +
              K30 * O1Dsi + K31 * O1Dsi)
    dOOQs = kOOQsI - OOQsi * kOOQsO
    
    # Troposphere ODEs
    
    # O2 Troposphere
    kO2tI = (k41 * O2si + (k21t + k21m) * O2bi + k31 * O2gi)
    kO2tO = ((k12t + k12m) + k13 + k14)
    dO2t = kO2tI - O2ti * kO2tO
    
    # OX (O17O) Troposphere
    kOXtI = (k41 * OXsi + (k21t + k21m) * OXbi + k31 * OXgi)
    kOXtO = (k12t * (alphart ** tresp) + k12m * (alpharm ** tresp) + k13 + k14)
    dOXt = kOXtI - OXti * kOXtO
    
    # OQ (O18O) Troposphere
    kOQtI = (k41 * OQsi + (k21t + k21m) * OQbi + k31 * OQgi)
    kOQtO = (k12t * alphart + k12m * alpharm + k13 + k14)
    dOQt = kOQtI - OQti * kOQtO
    
    # CO2 Troposphere
    kCO2tI = ((kr10t + kr10m) * COQti + (kr12t + kr12m) * COXti + k41 * CO2si)
    kCO2tO = ((kr9t + kr9m) + (kr11t + kr11m) + k14)
    dCO2t = kCO2tI - CO2ti * kCO2tO
    
    # COX (CO17O) Troposphere
    kCOXtI = ((kr11t + kr11m) * CO2ti + k41 * COXsi) 
    kCOXtO = ((kr12t + kr12m) + k14)
    dCOXt = kCOXtI - COXti * kCOXtO
    
    # COQ (CO18O) Troposphere
    kCOQtI = ((kr9t + kr9m) * CO2ti  + k41 * COQsi)
    kCOQtO = ((kr10t + kr10m) + k14) 
    dCOQt = kCOQtI - COQti * kCOQtO
    
    # Biosphere ODEs (equations not used because we assume an infinite reservoir)
    
   # O2 Biosphere
    # kO2bI = (k12 * O2ti)
    # kO2bO = (k21 + k23)
    # dO2b = kO2bI - O2bi *  kO2bO
    dO2b = 0
    
    # OX (17OO) Biosphere
    # kOXbI = (k12 * ((alphar ** tresp) * OXti)
    # kOXbO = (k21 + k23)
    # dOXb = kOXbI - OXbi * kOXbO
    dOXb = 0
    
    # OQ (18OO) Biosphere
    # kOQbI = (k12 * alphar * O2ti)
    # kOQbO = (k21 + k23)
    # dOQb = kOQbI - OQbi * kOQbO
    dOQb = 0
    
    # Geosphere ODEs
    
    # O2 Geosphere
    kO2gI = (k23t * O2bi + k23m * O2bi + k13 * O2ti)
    kO2gO = k31
    dO2g = kO2gI - O2gi * kO2gO
    
     # OX (O17O) Geosphere
    kOXgI = (k23t * OXbi + k23m * OXbi + k13 * OXti)
    kOXgO = k31
    dOXg = kOXgI - OXgi * kOXgO
    
    # OQ (O18O) Geosphere
    kOQgI = (k23t * OQbi + k23m * OQbi + k13 * OQti)
    kOQgO = k31
    dOQg = kOQgI - OQgi * kOQgO
    
    return np.array([dOs, dXs, dO1Ds, dQs, dX1Ds, dQ1Ds, dO2s, dOXs, dOQs,
                     dCO2s, dCOXs, dCOQs, dO3s, dOOXs, dOOQs, dO2t, dOQt,
                     dOXt, dCO2t, dCOQt, dCOXt,dO2b, dOQb, dOXb, dO2g, dOQg,
                     dOXg])

# Initial conditions for solver
y0 = np.array([Os0, Xs0, O1Ds0, Qs0, X1Ds0, Q1Ds0, O2s0, OXs0, OQs0, CO2s0,
               COXs0, COQs0, O3s0, OOXs0, OOQs0, O2t0, OQt0, OXt0, CO2t0,
               COQt0, COXt0, O2b0, OQb0, OXb0, O2g0,
               OQg0, OXg0])


# Time grid
t = np.arange(0, 10e5, 0.1)

# Order of species in molar output
moleso = np.array(['Os', 'Xs', 'O1Ds', 'Qs', 'X1Ds', 'Q1Ds', 'O2s', 'OXs',
                   'OQs', 'CO2s', 'COXs', 'COQs', 'O3s', 'OOXs', 'OOQs',
                   'O2t', 'OQt', 'OXt', 'CO2t', 'COQt', 'COXt', 'O2b',
                   'OQb', 'OXb', 'O2g', 'OQg', 'OXg'])

# Solve the DEs
moles = odeint(f, y0, t, mxstep = 1000000)
    
# Set up output dataframe
moles = pd.DataFrame(moles, columns = moleso)
moles = pd.concat([moles.tail(1)]).reset_index(drop=True)
moles = moles.transpose().reset_index(drop=True)
moles['Index'] = moleso
moles = moles.set_index('Index')

#%% Isotopes output

# Functions that calculate atomic isotopologue ratios (18O/16O and 17O/16O)
# Z is either 18O (Q) or 17O (X) and O refers to non rare isotopologue
def atomZ(isok2, Z, O):
    atomZ = (1 / isok2) * (Z / O)
    return atomZ

# Use atomic isotopologue ratios to calculate delta values relative to SMOW
def deltaZ(atomZ, rZ):
    deltaZ = 1000 * np.log(atomZ / rZ)
    return deltaZ

# Use delta values to calculate cap17
def capD(deltaX, deltaQ):
    capD = deltaX - tequil * deltaQ
    return capD

# Calculate the 18O/16O and 17O/16O ratios of molecules at end of model run
R18_Os = atomZ(isok2[0], moles.loc['Qs'], moles.loc['Os'])
R17_Os = atomZ(isok2[0], moles.loc['Xs'], moles.loc['Os'])
R18_O1Ds = atomZ(isok2[1], moles.loc['Q1Ds'], moles.loc['O1Ds'])
R17_O1Ds = atomZ(isok2[1], moles.loc['X1Ds'], moles.loc['O1Ds'])
R18_O2s = atomZ(isok2[2], moles.loc['OQs'], moles.loc['O2s'])
R17_O2s = atomZ(isok2[2], moles.loc['OXs'], moles.loc['O2s'])
R18_CO2s = atomZ(isok2[3], moles.loc['COQs'], moles.loc['CO2s'])
R17_CO2s = atomZ(isok2[3], moles.loc['COXs'], moles.loc['CO2s'])
R18_O3s = atomZ(isok2[4], moles.loc['OOQs'], moles.loc['O3s'])
R17_O3s = atomZ(isok2[4], moles.loc['OOXs'], moles.loc['O3s'])
R18_O2t = atomZ(isok2[5], moles.loc['OQt'], moles.loc['O2t'])
R17_O2t = atomZ(isok2[5], moles.loc['OXt'], moles.loc['O2t'])
R18_CO2t = atomZ(isok2[6], moles.loc['COQt'], moles.loc['CO2t'])
R17_CO2t = atomZ(isok2[6], moles.loc['COXt'], moles.loc['CO2t'])
R18_O2b = atomZ(isok2[7], moles.loc['OQb'], moles.loc['O2b'])
R17_O2b = atomZ(isok2[7], moles.loc['OXb'], moles.loc['O2b'])
R18_O2g = atomZ(isok2[8], moles.loc['OQg'], moles.loc['O2g'])
R17_O2g = atomZ(isok2[8], moles.loc['OXg'], moles.loc['O2g'])

# Calculate the d17O and d18O of species.
d18_Os = deltaZ(R18_Os, rQ)
d17_Os = deltaZ(R17_Os, rX)
d18_O1Ds = deltaZ(R18_O1Ds, rQ)
d17_O1Ds = deltaZ(R17_O1Ds, rX)
d18_O2s = deltaZ(R18_O2s, rQ)
d17_O2s = deltaZ(R17_O2s, rX)
d18_CO2s = deltaZ(R18_CO2s, rQ)
d17_CO2s = deltaZ(R17_CO2s, rX)
d18_O3s = deltaZ(R18_O3s, rQ)
d17_O3s = deltaZ(R17_O3s, rX)
d18_O2t = deltaZ(R18_O2t, rQ)
d17_O2t = deltaZ(R17_O2t, rX)
d18_CO2t = deltaZ(R18_CO2t, rQ)
d17_CO2t = deltaZ(R17_CO2t, rX)
d18_O2b = deltaZ(R18_O2b, rQ)
d17_O2b = deltaZ(R17_O2b, rX)
d18_O2g = deltaZ(R18_O2g, rQ)
d17_O2g = deltaZ(R17_O2g, rX)

# Calculate D17 at end of model run
D17_Os = capD(d17_Os, d18_Os)
D17_O1Ds = capD(d17_O1Ds, d18_O1Ds)
D17_O2s = capD(d17_O2s, d18_O2s)
D17_CO2s = capD(d17_CO2s, d18_CO2s)
D17_O3s = capD(d17_O3s, d18_O3s)
D17_O2t = capD(d17_O2t, d18_O2t)
D17_CO2t = capD(d17_CO2t, d18_CO2t)
D17_O2b = capD(d17_O2b, d18_O2b)
D17_O2g = capD(d17_O2g, d18_O2g)

# Order of species in isotope output dataframe
isotopeso = np.array(['d18_Os', 'd18_O1Ds', 'd18_O2s', 'd18_CO2s', 'd18_O3s',
                      'd18_O2t', 'd18_CO2t', 'd18_O2b', 'd18_O2g', 'd17_Os',
                      'd17_O1Ds', 'd17_O2s', 'd17_CO2s', 'd17_O3s', 'd17_O2t',
                      'd17_CO2t', 'd17_O2b', 'd17_O2g', 'D17_Os', 'D17_O1Ds',
                      'D17_O2s', 'D17_CO2s', 'D17_O3s', 'D17_O2t', 'D17_CO2t',
                      'D17_O2b', 'D17_O2g'])

#%% Mole fraction and flux outputs

# Mole fraction of O2 in troposphere
def xO2(O2, OX, OQ, air):
    xO2 = (O2 + OX + OQ) / air
    return xO2

# Mole fraction of CO2 in troposphere and stratosphere
def xCO2(CO2, COX, COQ, air):
    xCO2 = (CO2 + COX + COQ) / air
    return xCO2

# Mole fraction of O3 in stratosphere
def xO3(O3, OOX, OOQ, air):
    xO3 = (O3 + OOX + OOQ) / air
    return xO3

# D17O XO3 molar flux in per mil moles CO2/yr
def xJ(xCO2s, capDCO2s, airs, k41):
    xJ = (xCO2s * capDCO2s * airs) / (1 / k41)
    return xJ

# Calculate mole fraction of O2 in the troposphere
xO2 = xO2(moles.loc['O2t'], moles.loc['OXt'], moles.loc['OQt'], airt)

# Calculate mole fraction of CO2 in the troposphere
xCO2t = xCO2(moles.loc['CO2t'], moles.loc['COXt'], moles.loc['COQt'], airt)

# Calculate mole fraction of CO2 in the stratosphere
xCO2s = xCO2(moles.loc['CO2s'], moles.loc['COXs'], moles.loc['COQs'], airs)

# Calculate mole fraction of O3 in the stratosphere
xO3s = xO3(moles.loc['O3s'], moles.loc['OOXs'], moles.loc['OOQs'], airs)

# Calculate D17O flux
xJ = xJ(xCO2s, D17_CO2s, airs, k41)

# Order of species in mole fraction and isotope flux output
fracfluxo = np.array(['xO2', 'xCO2t', 'xCO2s', 'xO3s', 'xJ'])

#%% Output dataframes to spreadsheet

# Create empty dataframes for isotope and fraction/flux outputs
isotopes = pd.DataFrame(np.full((1, 27), 0, dtype=float), columns = isotopeso)
fracflux = pd.DataFrame(np.full((1, 5), 0, dtype=float), columns = fracfluxo)

# Assign calculated isotope values to dataframe
isotopes = pd.DataFrame(np.array([d18_Os, d18_O1Ds, d18_O2s, d18_CO2s,
                                  d18_O3s, d18_O2t, d18_CO2t, d18_O2b,
                                  d18_O2g, d17_Os, d17_O1Ds, d17_O2s,
                                  d17_CO2s, d17_O3s, d17_O2t, d17_CO2t,
                                  d17_O2b, d17_O2g, D17_Os, D17_O1Ds,
                                  D17_O2s, D17_CO2s, D17_O3s, D17_O2t,
                                  D17_CO2t, D17_O2b, D17_O2g]),
                        index = isotopeso)

# Assign calculated mole fraction and flux values to dataframe
fracflux = pd.DataFrame(np.array([xO2, xCO2t, xCO2s, xO3s, xJ]),
                        index =fracfluxo)

#%% Calculate difference between target SS solution and calculated values

# Target mole values from Young 2014
molest = pd.DataFrame(np.array([1.22e9, 465171, 3835.85, 2629860, 1.51757,
                                8.42261, 3.8e18, 2.85e15, 1.59e16, 4.79e15,
                                1.82e12, 1e13, 1.29e14, 1.53e11, 8.52e11,
                                3.8e19, 1.59e17, 2.85e16, 4.79e16, 1e14,
                                1.81e13, np.nan, np.nan, np.nan, np.nan,
                                np.nan, np.nan]),
                      index = moleso)
                
# Target isotopic values from Young 2014
isotopest = pd.DataFrame(np.array([51.941, 71.167, 23.298, 39.802, 76.349,
                                  23.298, 40.1118, np.nan, np.nan,
                                  26.8616, 64.5622, 11.8758, 22.8326, 69.7506,
                                  11.8767, 21.5126, np.nan,np.nan,
                                  -.56313, 26.9861, -.42564, 1.81727, 29.4383,
                                  -.42469, 0.33356, np.nan, np.nan]),
                         index = isotopeso)

# Target mole fraction and isotope flux values from Young 2014
fracfluxt = pd.DataFrame(np.array([0.21193, 2.7e-4, 2.7e-4, 7.2e-6,
                                   8.72e15]), index = fracfluxo)

# Percent difference between target moles and calculated moles
def pdiff(m, t):
    pdiff = ((m - t) / t) * 100
    return pdiff

perdmoles = pdiff(moles, molest)

# Absolute and percent difference between target isotopic values and calculated isotopic values
absdisotopes = isotopes - isotopest
perdisotopes = pdiff(isotopes, isotopest)

# Percent difference between target mole fraction/flux and calculated mole fraction/flux
perdfracflux = pdiff(fracflux, fracfluxt)

#%% Append difference between target SS and calculated to output sheets
moles['Percent diff'] = perdmoles[0]
moles.columns = ['Moles', 'Percent diff']
isotopes['Abs diff'] = absdisotopes[0]
isotopes['Percent diff'] = perdisotopes[0]
isotopes.columns = ['Per mil', 'Abs diff', 'Percent diff']
fracflux['Percent diff'] = perdfracflux[0]
fracflux.columns = ['Mole fraction/flux', 'Percent diff']

#%% Plots

print(str(D17_O2t))

# Figure 1 from paper

# Reference slope lines
x1 = np.linspace(0, 100)
pureMIF1 = (1 * x1 - 1 * isotopes['Per mil'].loc['d18_O2t'] +
            isotopes['Per mil'].loc['d17_O2t'])
highT = tequil * x1

# Setting up figure parameters
fig1 = plt.figure(figsize = (5, 5))
with sns.axes_style("whitegrid"):
    fig1 = fig1.add_subplot(1, 1, 1)
fig1.set(xlim = (0, 100), ylim = (0, 100))

# Plotting steady state solutions
fig1.plot(isotopes['Per mil'].loc['d18_O3s'], isotopes['Per mil'].loc['d17_O3s'],
             label = 'O3 (strat)', marker = 'o', ms = 5, color = 'blue')
fig1.plot(isotopes['Per mil'].loc['d18_O1Ds'], isotopes['Per mil'].loc['d17_O1Ds'],
             label = 'O(1D) (strat)', marker = 's', ms = 5, color = 'blue')
fig1.plot(isotopes['Per mil'].loc['d18_CO2s'], isotopes['Per mil'].loc['d17_CO2s'],
             label = 'CO2 (strat)', marker = 'D', ms = 5, color = 'blue')
fig1.plot(isotopes['Per mil'].loc['d18_CO2t'], isotopes['Per mil'].loc['d17_CO2t'],
             label = 'CO2 (trop)', marker = 'D', ms = 5, color = 'red')
fig1.plot(isotopes['Per mil'].loc['d18_O2t'], isotopes['Per mil'].loc['d17_O2t'],
             label = 'O2 (trop)', marker = 'X', ms = 5, color = 'red')

# PLotting reference lines, label = "D17_O2t as function of t resp')
fig1.plot(x1, pureMIF1, label = 'slope = 1', zorder = 1)
fig1.plot(x1, highT, label = 'slope .528', zorder = 1)

# Legend and title
fig1.set_xlabel("$\delta'^{18}$O")
fig1.set_ylabel("$\delta'^{17}$O")
fig1.set_title('Young2014sbmod SS Solution')
fig1.legend(loc = 'best', fontsize = 'small')

# Saving plot
plt.savefig('Young2014sbmodSS.png', dpi = 800)

#Export data as excel spreadsheet
writer = pd.ExcelWriter('Young2014sbmodWBSSrmchem2.xlsx', engine = 'xlsxwriter')
moles.to_excel(writer, sheet_name = 'Moles')
isotopes.to_excel(writer, sheet_name = 'Isotopes')
fracflux.to_excel(writer, sheet_name = 'Mole fraction flux')
writer.save()

#%% Comparing rate constants
K = pd.DataFrame(Kod, index=Ki).rename(columns={0:'Ko'})
K['Kc'] = Kcd
K['Percent diff'] = pdiff(Kcd, Kod)

#Export data as excel spreadsheet
writer = pd.ExcelWriter('Kcompare.xlsx', engine = 'xlsxwriter')
K.to_excel(writer, sheet_name = 'K')
writer.save()
