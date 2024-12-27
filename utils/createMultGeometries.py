"""
Realized by Davide Lisi, EPFL
Contact: davide.lisi@epfl.ch
"""

from utils.Bezier import * # maybe to be removed from here
from utils.GeometrySettings import *
from utils.stateFileModifier import *
import utils.Folder_management
import plotly.graph_objects as go

###########################################################
###########################################################

# SETTINGS OF THE SIMULATED DATASET

# Print Results & Conversion Output | Y/n = True/False
print_results = False
print_conversion_output = False

# Beta at inlet and outlet from 1D
beta_in_settings = 24.008 # (beta_2, beta in corrispondenza dell'hub all'inlet)
beta_out_settings = 35.15 # (beta_4, beta in corrispondenza dell'hub all'outlet)

# HUB AND SHROUD PARAMETERS
# Geometrical Parameters from 1D
L_ind = 30 #30
L_comp = 8 #8
r2s = 5.6 #5.6
r2h = 2 #2
r4  = 10 #10
b4  = 1 #1
r5  = 30 #30
# Hub ans Shroud | Weights for the control point of the hub and shroud profiles
w1_hb = 1
w1_sh = 1
# Splitter LE Cut, Meridional Target
splitter_LE_meridional_target_hub_settings = 0.3
splitter_LE_meridional_target_sh_settings = 0.3

# Constant thickness settings
thickness = 0.2

# Decide how many points to compute for the Bezier curves
beta_bezier_N = 300 # Number of points to compute for beta curve
HubShr_bezier_N = 300 # Number of points for the hub and shroud bezier

# DISCRETIZATION OF THE BETA/M% CURVE'S PARAMETERS
# Discrtization of the parameter tau_0
tau_0_N = 4 
tau_0_max = 0.7 #   0 < tau_0_max < 1      and     tau_0_max > tau_0_min
tau_0_min = 0.3 #   0 < tau_0_min < 1      and     tau_0_min < tau_0_min
# Discrtization of the parameter tau_1
tau_1_N = 4
tau_1_max = -0.3  # 2 to have P1 at beta_ou + delta
tau_1_min = -0.7  # - 1 to have P1 at bet_in - delta
# Discrtization of the parameter w1
w1_N = 3 
w1_min = 1
w1_max = 10 

# Folder Management Settings
Project_Name = "Database_tau_w1_betacurve"
Project_Folder = "D:\\Davide"
default_geometry_path = 'defaultBGI\\LUS_General_OnlySpan0_Copy.bgi'
std_BLADEGEN_Folder_settings = "C:\\Program Files\\ANSYS Inc\\v242\\aisol\\BladeModeler\\BladeGen"

###########################################################
###########################################################

Folder_management.Create_Project_Folder(Project_Name = Project_Name,
                      Project_Folder = Project_Folder,
                      default_geometry_path = default_geometry_path)

tau_0 = np.linspace(tau_0_min, tau_0_max, tau_0_N)
tau_1 = np.linspace(tau_1_min, tau_1_max, tau_1_N)
w1 = np.linspace(w1_min, w1_max, w1_N)
HubShroud_1D_dimensions = {'object':'HubShroud', 'HubShr_bezier_N':HubShr_bezier_N, 'definition':'xz', 'spline_degree':2, 'L_ind':L_ind,'L_comp':L_comp, 'r2s':r2s, 'r2h':r2h, 'r4':r4, 'b4':b4, 'r5':r5, 'w1_hb':w1_hb, 'w1_sh':w1_sh}


# Creating the parameters 
pars_list = [ParametrizationSettings(
    beta_in_settings = beta_in_settings,
    beta_out_settings = beta_out_settings,
    beta_bezier_N_settings = beta_bezier_N,
    HubShroud_1D_dimensions = HubShroud_1D_dimensions,
    print_conversion_output = print_conversion_output,
    tau_settings =  [tau_0_ijk, tau_1_ijk],
    w1_settings = w1_ijk,
    thickness = thickness,
    splitter_LE_meridional_target_hub_settings = splitter_LE_meridional_target_hub_settings,
    splitter_LE_meridional_target_sh_settings = splitter_LE_meridional_target_sh_settings,
    index = (i * tau_1_N * w1_N) + (j * w1_N) + k,
    par_name = f"{str(tau_0_ijk).replace('.', '')}_{str(tau_1_ijk).replace('.', '')}_{str(w1_ijk).replace('.', '')}")  # NAME OF THE SAVED FILE
                for i,tau_0_ijk in enumerate(tau_0)
                for j,tau_1_ijk in enumerate(tau_1)
                for k,w1_ijk in enumerate(w1)
    ]
print(f"-----------------------------------------\nCreated {len(pars_list)} geometries")

# Create a figure
fig = go.Figure()
# Iterate through `pars_list` and add each curve to the figure
for par in pars_list:
    if hasattr(par, 'Beta_M_bezier_curve_points') and par.Beta_M_bezier_curve_points is not None:
        # Extract x and y values from the 2D points
        x_values = [point[0] for point in par.Beta_M_bezier_curve_points]
        y_values = [point[1] for point in par.Beta_M_bezier_curve_points]
        
        # Add the curve to the figure
        fig.add_trace(go.Scatter(
            x=x_values,  # Use the first element of each pair as x-values
            y=y_values,  # Use the second element of each pair as y-values
            mode='lines',  # Line plot
            name=f"Par {par.par_name}"  # Legend label
        ))

# Customize layout
fig.update_layout(
    title="Design space - > See Terminal to go on",
    xaxis_title="m%",  # Meaningful label for x-axis
    yaxis_title="beta",  # Meaningful label for y-axis
    legend_title="Parameters",
    showlegend=True,
)

# Display the figure
fig.show()
print(f"\nExpected time to create BladeGen files: {3.5*tau_0_N*tau_1_N*w1_N/60} min\n")
Go_on = input("Are you sure you want to procede? Y/n > ")
print(f"-----------------------------------------")


if Go_on in ["y","Y"]:
    print("Starting process")
    # Creating the results dictionary 
    results_dict = { (i * tau_1_N * w1_N) + (j * w1_N) + k : [[tau_0_ijk, tau_1_ijk, w1_ijk],"Results"] #The "Results" string at the end is where the results will be stored (Still to be implemented), while the first one is the index
                    for i,tau_0_ijk in enumerate(tau_0)
                    for j,tau_1_ijk in enumerate(tau_1)
                    for k,w1_ijk in enumerate(w1) }
    Folder_management.save_json(f"{Project_Folder}\\{Project_Name}\\simulation_results.json", results_dict)

    i = 1
    for par in pars_list:
        print(f"\n######################## > Creating Geometry {i}/{len(pars_list)} < ########################")
        file_index = par.index # Index used for the name of the stored files
        file_code = f"{par.par_name}" # Code used for the name of the stored files
        file_name_settings = f"geometry_{file_index}_{file_code}"
        Geometry_i= Geometry(par,
                            defaultfilePath = f"defaultBGI\\LUS_General_OnlySpan0_Copy.bgi",
                            file_name = file_name_settings,
                            Project_Name = Project_Name,
                            Project_Folder = Project_Folder,
                            std_BLADEGEN_Folder = std_BLADEGEN_Folder_settings)

        #Geometry_i.create_unmodified_json_geometry()
        Geometry_i.create_modified_geometry() # TO BE MODIFIED : | 1 Setup Ansys Folder | 2: go to stateFileModifier.create_modified_geometry | 3: uncomment line saying self.convert_bgi_to_bgd(self.output_bgiPath, self.output_bgdPath, ANSYSfolderPath = self.std_ANSYS_Folder)
        #Geometry_i.create_unmodified_bgi_geometry()
        if print_results:
            print(f"Geometry was created for  : tau = {par.tau} | w1 = {par.w1} | Name = {par.par_name}")

        i+=1

    if print_results:
        print(f"Results Dictionary Initialized:\n{results_dict}\n")
    
    

else:
    print("No geometry has been created\n-------------------------------------")
