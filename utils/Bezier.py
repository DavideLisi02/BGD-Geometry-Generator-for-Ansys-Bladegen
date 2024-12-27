"""
Realized by Davide Lisi, EPFL
Contact: davide.lisi@epfl.ch
"""

import numpy as np
from scipy.interpolate import make_interp_spline
import matplotlib.pyplot as plt

class Bezier:
    """Bezier curve"""
    def __init__(self, curve_parameters, **kwargs):

        super(Bezier, self).__init__()
        print(f"{curve_parameters}")
        # Curve parameters - see parameters.py for more details
        self.object = curve_parameters['object']  
        self.definition = curve_parameters['definition']

        if self.object == 'Blade' and self.definition == 'beta-M%':
            
            self.beta_in = curve_parameters['beta_in']  
            self.beta_out = curve_parameters['beta_out']
            self.tau = curve_parameters['tau']  
            self.w1 = curve_parameters['w1']
            self.spline_degree = curve_parameters['spline_degree']
            self.beta_bezier_N = curve_parameters['beta_bezier_N']
            
            if self.spline_degree == 2:

                # Control points
                self.P0 = np.array([0, self.beta_in])  # Start point
                self.P1 = np.array([100*self.tau[0], self.beta_in+(self.beta_out-self.beta_in)*self.tau[1]])  # Control point
                self.P2 = np.array([100, self.beta_out])  # End point

                # Meridional length values
                self.m_values = np.linspace(0, 100, self.beta_bezier_N) # Discretization of Meridional length

                points = np.array([((1 - m/100)**2 * self.P0 + 2 * (1 - m/100) * m/100 * self.w1 * self.P1 + (m/100)**2 * self.P2) /
                                        ((1 - m/100)**2 + 2 * (1 - m/100) * m/100 * self.w1 + (m/100)**2)   for m in self.m_values])# Bezier curve calculation for each meridional point of the discretization
                
                self.points = points.tolist()
                

            else: # For the possibility of using spline curves with different degrees and number of control points
                self.points = None

            # NOTE: This overrides the previous declarations
            self.__dict__.update(kwargs)

        elif self.object == 'HubShroud' and self.definition == 'xz':
            self.HubShr_bezier_N = curve_parameters['HubShr_bezier_N']
            self.L_ind = curve_parameters['L_ind']
            self.L_comp = curve_parameters['L_comp']
            self.r2s = curve_parameters['r2s']
            self.r2h = curve_parameters['r2h']
            self.r4 = curve_parameters['r4']
            self.b4 = curve_parameters['b4']
            self.r5 = curve_parameters['r5']
            self.spline_degree = curve_parameters['spline_degree']
            self.w1_hb = curve_parameters['w1_hb']
            self.w1_sh = curve_parameters['w1_sh']

            if self.spline_degree == 2:
                # Control points for Hub Profile
                self.D    = np.array([0, self.r2h])  # Start point
                self.Ph_1 = np.array([1, self.r2h])  # Control point
                self.E    = np.array([1, self.r4])   # End point

                # Hub axial length values
                self.x_hub_values = np.linspace(0, 1, self.HubShr_bezier_N)

                # Control points for Shroud Profile
                self.L    = np.array([0, self.r2s])  # Start point
                self.Ps_1 = np.array([1, self.r2s])  # Control point
                self.M    = np.array([1, self.r4])   # End point

                # Shroud axial length values
                self.x_shr_values = np.linspace(0, 1, self.HubShr_bezier_N)
                
                # Bezier curve calculation for Hub profile
                points_hub = np.array([((1 - x)**2 * self.D + 2 * (1 - x) * x * self.w1_hb * self.Ph_1 + (x)**2 * self.E) /
                                        ((1 - x)**2 + 2 * (1 - x) * x * self.w1_hb + (x)**2)   for x in self.x_hub_values])
                Lead_Hub_point = [0.01,self.r2h]  # Point for Leading Edge at hub | 0.005 stands for (distance between leading edge at hub and inducer)/(L_comp)
                points_hub = np.insert(points_hub, 1, Lead_Hub_point, axis=0)  # Insert Lead_Hub_point as second point
                Trail_Hub_point = [1, self.r4*0.99]  # Point for Trailing Edge at hub
                points_hub = np.insert(points_hub, -1, Trail_Hub_point, axis=0)  # Insert Trail_Hub_point as one before last point
                points_hub[:, 0] *= self.L_comp
                points_hub[:, 0] += self.L_ind
                self.points_hub = points_hub.tolist()
                # Bezier curve calculation for Shroud profile
                points_shr = np.array([((1 - x)**2 * self.L + 2 * (1 - x) * x * self.w1_sh * self.Ps_1 + (x)**2 * self.M) /
                                        ((1 - x)**2 + 2 * (1 - x) * x * self.w1_sh + (x)**2)   for x in self.x_shr_values])
                Lead_Shr_point = [0.015,self.r2s]  # Point for Leading Edge at hub | 0.008 stands for (distance between leading edge at shroud and inducer)/(L_comp-b4)
                points_shr = np.insert(points_shr, 1, Lead_Shr_point, axis=0)  # Insert Lead_Hub_point as second point
                Trail_Shr_point = [1, self.r4*0.99]  # Point for Trailing Edge at hub
                points_shr = np.insert(points_shr, -1, Trail_Shr_point, axis=0)  # Insert Trail_Hub_point as one before last point
                points_shr[:, 0] *= self.L_comp-self.b4
                points_shr[:, 0] += self.L_ind
                self.points_shr = points_shr.tolist()
                self.points = [self.points_hub, self.points_shr]

            else: # For the possibility of using spline curves with different degrees and number of control points
                self.points = None

            # NOTE: This overrides the previous declarations
            self.__dict__.update(kwargs)
        

