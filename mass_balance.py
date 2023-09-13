import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tracers import Isotope

class MassBalance:
    def __init__(self):
        self.P = None
        self.I = None
        self.E = None
        self.V = None
        self.Tc = None
        self.RH = None

        self.df = None

    def import_data(self, fpath="data/water_balance_data.xlsx"):
        """
        Read the data from Excel using Pandas.

        Parameters
        ----------
        fpath : str, optional
            _description_, by default "data/water_balance_data.xlsx"
        """

        df = pd.read_excel(
            fpath,
            index_col=0,
            parse_dates=True,
        )

        df['P'] = df['area'] * df['rain'] / 1000.
        df['E'] = df['area'] * df['evaporation'] / 1000.
        df['dV'] = -df['volume'].diff(periods=-1)
        df['I'] = df['P'] - df['E'] - df['dV']
        df["rh"] = df["rh"] / 100.

        self.df = df

    def calculate_mass_balance(self, tracer, pan_factor=1.2):
        if self.df is None:
            self.import_data()

        dM_E = 0.0 # Remains zero for non-isotope species

        M = np.empty(len(self.df))
        C = np.empty(len(self.df))

        P = self.df["P"].to_numpy()
        I = self.df["I"].to_numpy()
        E = self.df["E"].to_numpy() / pan_factor
        V = self.df["volume"].to_numpy()
        Tc = self.df["temperature"].to_numpy()
        RH = self.df["rh"].to_numpy()

        for i, (Vi, Pi, Ei, Ii, Tci, RHi) in enumerate(zip(V, P, E, I, Tc, RH)):
            if i == 0: # First day
                M[0] = Vi * tracer.C_0
                C[0] = M[0] / Vi # Gives delta_18O_0 of course!
            else:
                M[i] = M[i - 1] + dM_P - dM_E - dM_I
                C[i] = M[i] / Vi    

            dM_P = tracer.C_rain * Pi
            dM_I = C[i] * Ii

            if isinstance(tracer, Isotope):
                dM_E = tracer.delta_e(Tci, RHi, C[i]) * Ei

        self.df[tracer.name] = C

    def plot(self, tracer_name):
        if self.df is None:
            self.import_data()

        fig, ax = plt.subplots(figsize=(8,2))

        ax.plot(self.df.index, self.df[tracer_name])
        ax.plot(self.df.index, self.df[f"{tracer_name}_sample"], 'C0o', mfc='w')