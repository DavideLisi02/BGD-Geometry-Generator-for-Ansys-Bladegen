"""
Realized by Davide Lisi, EPFL
Contact: davide.lisi@epfl.ch
"""

import os
import json
import re
from utils.run_command import run_command
import utils.Folder_management as Folder_management


class StateFileModifier:

    def __init__(self,
                 Geometry, # Class conatining all the data of the wanted geoetry, see GeometrySettings in GeometrySettings.py
                 destination_path = "D:\\Davide\\Geometry_test.bgd",
                 defaultfilePath ='defaultBGI\\LUS_General_OnlySpan0_Copy.bgi',
                 output_jsonFolder = Folder_management.output_jsonfolder_settings,
                 output_bgiFolder = Folder_management.output_bgifolder_settings,
                 output_unmodified_bgiFolder = Folder_management.output_unmodified_bgifolder_settings,
                 output_unmodified_bgdFolder = Folder_management.output_unmodified_bgdfolder_settings,
                 std_BLADEGEN_Folder = "C:\\Program Files\\ANSYS Inc\\v242\\aisol\\BladeModeler\\BladeGen",
                **kwargs):
        """
        Initializes the StateFileModifier class with the given parameters.
                Args:
                    Geometry (object): Class containing all the data of the desired geometry, see GeometrySettings in GeometrySettings.py.
                    destination_folder (str, optional): Path to the destination folder where output files will be saved. Defaults to "D:\\Davide".
                    defaultfilePath (str, optional): Path to the default BGI file. Defaults to 'defaultBGI\\LUS_General_OnlySpan0_Copy.bgi'.
                    output_jsonFolder (str, optional): Folder path for output JSON files, defined in Folder_management.output_jsonfolder_settings.
                    output_bgiFolder (str, optional): Folder path for output BGI files, defined in Folder_management.output_bgifolder_settings.
                    output_unmodified_bgiFolder (str, optional): Folder path for unmodified BGI files, defined in Folder_management.output_unmodified_bgifolder_settings.
                    output_unmodified_bgdFolder (str, optional): Folder path for unmodified BGD files, defined in Folder_management.output_unmodified_bgdfolder_settings.
                    std_BLADEGEN_Folder (str, optional): Standard BladeGen folder path. Defaults to "C:\\Program Files\\ANSYS Inc\\v242\\aisol\\BladeModeler\\BladeGen".
                    **kwargs: Additional keyword arguments.
                Attributes:
                    Geometry (object): Stores the Geometry object.
                    tau (float): Tau value from the Geometry object.
                    w1 (float): W1 value from the Geometry object.
                    output_bgdPath (str): Path to the destination folder for BGD files.
                    defaultfilePath (str): Path to the default BGI file.
                    output_project_path (str): Path to the current project directory.
                    output_jsonPath (str): Path to the output JSON file.
                    output_bgiPath (str): Path to the output BGI file.
                    output_unmodified_bgiPath (str): Path to the unmodified BGI file.
                    output_unmodified_bgdPath (str): Path to the unmodified BGD file.
                    std_BLADEGEN_Folder (str): Path to the standard BladeGen folder.
        """
        super(StateFileModifier, self).__init__()
        
        self.Geometry = Geometry
        self.tau = self.Geometry.tau
        self.w1 = self.Geometry.w1
    
        self.output_bgdPath = destination_path

        # Folders definition for utils
        self.defaultfilePath = defaultfilePath
        self.output_project_path = os.path.dirname(os.path.abspath(__file__))
        self.output_jsonPath = f"{self.output_project_path}\\{output_jsonFolder}\\MODgeometry.json"
        self.output_bgiPath = f"{self.output_project_path}\\{output_bgiFolder}\\MODgeoemtry.bgi"
        self.output_unmodified_bgiPath = f"{self.output_project_path}\\{output_unmodified_bgiFolder}\\UNMODgeoemtry.bgi"
        self.output_unmodified_bgdPath = f"{self.output_project_path}\\{output_unmodified_bgdFolder}\\UNMODgeoemtry.bgd"

        self.std_BLADEGEN_Folder = std_BLADEGEN_Folder

        return

    def readfile(self, filePath = 'defaultBGI\geometry00.bgi'):
        """
        Reads the .bgi file and returns a list of lines.
        """
        os.chdir(os.path.dirname(__file__))
        with open(filePath, 'r') as file:
            DataList = file.readlines()
        return DataList

    def convert_list_to_dict(self, list):
        """
        Converts the list of lines from the .bgi file into a structured dictionary.
        """
        data_dict = {}
        stack = []  # Stack to handle nested sections/subsections
        current_data = []  # For storing (x, y) or other data points
        current_subsection = None  # To track the current subsection
        subsection_counters = {}  # Track counters for repeated subsection names
        BladeCounter = 0

        for line in list:
            line = line.strip()
            if self.Geometry.print_conversion_output:
                print(f"Analyzed line = #{line}#")

            if line.startswith("Begin"):
                section_name = line.split()[1]
                new_section = {}
                if stack:
                    # Add the new section to the current section at the top of the stack
                    parent_section = stack[-1]

                    # Handle cases like 'SpanLayer' with multiple instances
                    if section_name in parent_section:
                        if section_name not in subsection_counters:
                            subsection_counters[section_name] = 1
                        subsection_counters[section_name] += 1
                        section_name_with_index = f"{section_name}{subsection_counters[section_name]}"
                    else:
                        section_name_with_index = section_name
                        subsection_counters[section_name] = 1

                    parent_section[section_name_with_index] = new_section
                else:
                    # This is a top-level section
                    data_dict[section_name] = new_section
                stack.append(new_section)  # Push the new section onto the stack
                current_subsection = None  # Reset current_subsection on new section

            elif line.startswith("End"):
                if current_data and stack:
                    # Store the current data into the section at the top of the stack
                    parent_section = stack[-1]
                    if "data" not in parent_section:
                        parent_section["data"] = []  # Initialize data list
                    parent_section["data"].extend(current_data)  # Append data to the "data" key
                    current_data = []
                # Pop the section off the stack when it ends
                stack.pop()
                if stack:  # Reset current_subsection when not at the top level
                    current_subsection = None

            elif "=" in line:
                # Handle key=value lines
                key, value = line.split("=", 1)
                if stack:
                    # Add the key-value pair to the current section
                    current_section = stack[-1]
                    current_section[key.strip()] = value.strip()
                else:
                    print(f"Warning: Key-value pair found outside of any section: {line}")

            elif "(" in line and ")" in line:
                # Handle data points in the form (x, y)
                # Extract and convert the (x, y) points to tuples of floats
                point = re.findall(r"\((.*?)\)", line)[0]
                x, y = map(float, point.split(','))
                current_data.append((x, y))

            elif "New" in line:
                if "Blade" in line:
                    section_name = f"{line.split()[1]}{BladeCounter}"
                    BladeCounter +=1
                    new_section = {}
                    if stack:
                        # Add the new section to the current section at the top of the stack
                        parent_section = stack[-1]

                        # Handle cases like 'SpanLayer' with multiple instances
                        if section_name in parent_section:
                            if section_name not in subsection_counters:
                                subsection_counters[section_name] = 1
                            subsection_counters[section_name] += 1
                            section_name_with_index = f"{section_name}{subsection_counters[section_name]}"
                        else:
                            section_name_with_index = section_name
                            subsection_counters[section_name] = 1

                        parent_section[section_name_with_index] = new_section
                    else:
                        # This is a top-level section
                        data_dict[section_name] = new_section
                    stack.append(new_section)  # Push the new section onto the stack
                    current_subsection = None  # Reset current_subsection on new section
                else:
                    # Handle new subsections (e.g., New Segment, New AngleCurve, etc.)
                    subsection_name = line
                    new_subsection = {}
                    if stack:
                        # Add the new subsection to the current section at the top of the stack
                        current_section = stack[-1]
                        if subsection_name not in current_section:
                            current_section[subsection_name] = []  # Initialize list for multiple segments
                        current_section[subsection_name].append(new_subsection)  # Add new subsection
                    stack.append(new_subsection)  # Push the new subsection onto the stack
                    current_subsection = subsection_name  # Track the current subsection

            elif line == '':
                # Ignore empty lines
                continue

            else:
                # Handle any other plain lines
                if stack:
                    # Add the line to the current section as a key with a value of None
                    current_section = stack[-1]
                    current_section[line] = None
                else:
                    print(f"Warning: Unrecognized line found outside of any section: {line}")

        return data_dict

    def modify_dict_numOfBlades(self, numOfBlades, modify_numOfBlades, data_dict):
        '''
        Modifies the default geometry, descripted in a json file, changing the number of blades
        '''
        modified_Dict = data_dict
        if modify_numOfBlades:
            modified_Dict["Model"]["NumMainBlades"] = str(numOfBlades)
            return modified_Dict

    def modify_dict_blade(self, Blade_definition, curve_points_list_blade, data_dict, fibers):
        '''
        Modifies the default geometry, descripted in a json file, accordingly to
        the object and the definition of the parametrization by inserting the curve data points 
        in a new json file which is the output of the function.
        '''
        modified_Dict = data_dict
        if Blade_definition == 'beta-M%' and fibers == 'General_only_at_Hub':
            layers = [0]
            modified_Dict["Blade0"]["AngleDefinition"]['SpanwiseDistribution'] = 'General'
            for layer in layers:
                modified_Dict["Blade0"]["AngleDefinition"]["New AngleCurve"][layer]["New Segment"][0]["Data"]["data"] = curve_points_list_blade
                modified_Dict["Blade0"]["AngleDefinition"]["New AngleCurve"][layer]["DefinitionType"] = "BetaCurve"
                modified_Dict["Blade0"]["AngleDefinition"]["New AngleCurve"][layer]["HorizDim"] = "PercentMeridional"
        return modified_Dict
    
    def modify_dict_HubShroud(self, HubShroud_definition, data_dict):
        '''
        Modifies the default geometry, descripted in a json file, accordingly to
        the object and the definition of the parametrization by inserting the curve data points 
        in a new json file which is the output of the function.
        '''
        modified_Dict = data_dict
        if HubShroud_definition == 'xz':
            
            # Modifying Hub profile
            total_Hub_profile = self.Geometry.total_Hub_profile

            modified_Dict["Meridional"]["HubCurve"]["New Segment"] = []
            
            for element in total_Hub_profile:
                if len(element) <= 10:
                    i = 0
                    while i in range(len(element)-1):
                        modified_Dict["Meridional"]["HubCurve"]["New Segment"].append({
                            "CurveType": "Spline",
                            "UpstreamControl": "Free",
                            "Data": {
                                "data": [ element[i] , element[i+1] ]
                            },
                            "DownstreamControl": "Free"
                        })
                        i+=1
                else:
                    modified_Dict["Meridional"]["HubCurve"]["New Segment"].append({
                        "CurveType": "Spline",
                        "UpstreamControl": "Free",
                        "Data": {
                            "data": element 
                        },
                        "DownstreamControl": "Free"
                    })

            
            # Modifying Shroud profile
            total_Shroud_profile = self.Geometry.total_Shroud_profile
            
            modified_Dict["Meridional"]["ShroudCurve"]["New Segment"] = []
            
            j=0
            for element in total_Shroud_profile:
                if len(element) <= 10:
                    i = 0
                    while i in range(len(element)-1):
                        modified_Dict["Meridional"]["ShroudCurve"]["New Segment"].append({
                            "CurveType": "Spline",
                            "UpstreamControl": "Free",
                            "Data": {
                                "data": [ element[i] , element[i+1] ]
                            },
                            "DownstreamControl": "Free"
                        })
                        i+=1
                        j+=1
                else:
                    modified_Dict["Meridional"]["ShroudCurve"]["New Segment"].append({
                        "CurveType": "Spline",
                        "UpstreamControl": "Free",
                        "Data": {
                            "data": element 
                        },
                        "DownstreamControl": "Free"
                    })
                j+=1

            # Modifying inlet curve
            inlet_curve = self.Geometry.inlet_curve
            modified_Dict["Meridional"]["InletCurve"]["New Segment"][0] = {
                        "CurveType": "Linear",
                        "Data": {
                            "data": inlet_curve 
                        },
                    }
            # Modifying exhaust curve
            exhaust_curve = self.Geometry.exhaust_curve
            modified_Dict["Meridional"]["ExhaustCurve"]["New Segment"][0] = {
                        "CurveType": "Linear",
                        "Data": {
                            "data": exhaust_curve 
                        },
                    }
            
            # Modifying Leading Edge
            leading_edge_curve = self.Geometry.leading_edge_curve
            modified_Dict["Meridional"]["LeadingEdgeCurve"]["New Segment"][0] = {
                        "CurveType": "Spline",
                        "UpstreamControl": "Free",
                        "Data": {
                            "data": leading_edge_curve 
                        },
                        "DownstreamControl": "Free"
                    }
            # Modifying Trailing Edge
            trailing_edge_curve = self.Geometry.trailing_edge_curve
            modified_Dict["Meridional"]["TrailingEdgeCurve"]["New Segment"][0] = {
                        "CurveType": "Spline",
                        "UpstreamControl": "Free",
                        "Data": {
                            "data": trailing_edge_curve 
                        },
                        "DownstreamControl": "Free"
                    }
            # Modifying Leading Edge of Splitter Blade
            splitter_LE = self.Geometry.splitter_LE
            modified_Dict["Blade1"]["LeadingEdgeCut"]["New Segment"][0] = {
                    "CurveType": "Spline",
                    "UpstreamControl": "Free",
                    "Data": {
                        "data": splitter_LE
                    },
                    "DownstreamControl": "Free"
                }

        return modified_Dict
    
    def modify_dict_thickness(self, thickness_curve, modify_Thickness, data_dict):
        '''
        Modifies the default geometry, descripted in a json file, changing the thickness curve
        '''
        modified_Dict = data_dict
        if modify_Thickness:
            modified_Dict["Blade0"]["ThicknessDefinition"]["New ThicknessCurve"][0]["HorizDim"] = "PercentMeridional"
            modified_Dict["Blade0"]["ThicknessDefinition"]["New ThicknessCurve"][0]["New Segment"][0]["Data"]["data"] = thickness_curve
        return modified_Dict

    def save_json(self, output_jsonPath, data_dict):
        """
        Saves the dictionary into a JSON file.
        """
        with open(output_jsonPath, 'w') as json_file:
            json.dump(data_dict, json_file, indent=4)
        return
        
    def convert_json_to_bgi(self, output_jsonPath, output_bgiPath):
        """
        Reads a JSON file and converts it into a .bgi format
        that preserves specific formatting.
        """
        with open(output_jsonPath, 'r') as file:
            json_data = json.load(file)

        with open(output_bgiPath, 'w') as file:
            def write_bji(data, indent_level=0):
                indent = '    ' * indent_level  # Use 4 spaces for indentation
                data_indent = '    ' * (indent_level)  # One additional level for data points inside "Data"

                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, dict):
                            if key in ["Case", "PlusData", "Model", "Equations", "Defaults", "Meridional", "HubCurve", "Data"]:
                                file.write(f"{indent}Begin {key}\n")
                                write_bji(value, indent_level + 1)
                                file.write(f"{indent}End {key}\n\n")
                            else:
                                if "Blade" in key:
                                    name_key = key[:-1]
                                else:
                                    name_key = key
                                file.write(f"{indent}New {name_key}\n")
                                write_bji(value, indent_level + 1)
                                file.write(f"{indent}End {name_key}\n\n")

                        elif isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    if key.startswith("New"):
                                        file.write(f"{indent}{key}\n")
                                        write_bji(item, indent_level + 1)
                                        file.write(f"{indent}End {key.split()[1]}\n")
                                    else:
                                        file.write(f"{indent}Begin {key}\n")
                                        write_bji(item, indent_level + 1)
                                        file.write(f"{indent}End {key}\n")
                                else:
                                    # Adjust indentation specifically for Data section points
                                    if key == 'data':
                                        item = tuple(item)
                                        file.write(f"{data_indent}{item}\n")  # Use data_indent (one additional level)
                                    else:
                                        file.write(f"{indent}{item}\n")

                        elif value is None:
                            file.write(f"{indent}{key}\n")

                        else:
                            file.write(f"{indent}{key}={value}\n")

                elif isinstance(data, list):
                    for item in data:
                        file.write(f"{indent}{item}\n")

            write_bji(json_data)

    def convert_bgi_to_bgd(self, output_bgiPath, output_bgdPath, BLADEGENfolderPath = "C:\\Program Files\\ANSYS Inc\\v242\\aisol\\BladeModeler\\BladeGen"):
        '''
        Runs terminal's commands to execute BladeBatch from BladeGen in order to run
        the .bgi file and obtain a .bgd
        '''

        # Command for Opening the Blade Batch folder
        folder_command = f'''cd {BLADEGENfolderPath}'''
        print(f"Opening the bladegen folder: {folder_command}")

        # Command to run BladeBatch
        blade_batch_command = f'BladeBatch {output_bgiPath} {output_bgdPath}'
        print(f"Converting using Blade Batch: {blade_batch_command}")
        
        
        full_command = f"dir && {blade_batch_command}"
        print(f"Full command: {full_command}")

        #running full command
        run_command(full_command, BLADEGENfolderPath)

        # full_command = f"{folder_command} && {blade_batch_command}"

        # Combine commands into a single command string for the terminal
        #full_command = f'cmd /c {path_command} && {folder_command} && {blade_batch_command}'
        #print(f"Full command: {full_command}\n-------------------")

        
    def create_modified_geometry(self):
        """
        Function that creates a modified geometry from the default one
        """
        DataList = self.readfile(filePath =  self.defaultfilePath)
        DataDict = self.convert_list_to_dict(DataList)
        ModDataDict_numofblades = self.modify_dict_numOfBlades(self.Geometry.numOfBlades, self.Geometry.modify_numOfBlades, DataDict)
        ModDataDict_blade = self.modify_dict_blade(self.Geometry.Beta_definition, self.Geometry.Beta_M_bezier_curve_points, ModDataDict_numofblades, self.Geometry.fibers)
        ModDataDict_hs = self.modify_dict_HubShroud(self.Geometry.HubShroud_definition, ModDataDict_blade)
        ModDataDict_final = self.modify_dict_thickness(self.Geometry.thickness_curve, self.Geometry.modify_Thickness, ModDataDict_hs)
        self.save_json(self.output_jsonPath, ModDataDict_final)
        self.convert_json_to_bgi(self.output_jsonPath, self.output_bgiPath)     
        self.convert_bgi_to_bgd(self.output_bgiPath,
                                self.output_bgdPath,
                                BLADEGENfolderPath = self.std_BLADEGEN_Folder)        
        return
    
    def create_unmodified_json_geometry(self):
        """
        Function that creates a json file from the default geometry without any modification
        Used for debugging reasons.
        """
        DataList = self.readfile(filePath = self.defaultfilePath)
        if self.Geometry.print_conversion_output:
            print(DataList)
        DataDict = self.convert_list_to_dict(DataList)
        self.save_json(self.output_jsonPath, DataDict)
        return
    
    def create_unmodified_bgi_geometry(self):
        """
        Function that creates a .bgi file from the default geometry without any modification
        Used for debugging reasons.
        """
        DataList = self.readfile(filePath =  self.defaultfilePath)
        UnModDataDict = self.convert_list_to_dict(DataList)
        self.save_json(self.output_jsonPath, UnModDataDict)
        self.convert_json_to_bgi(self.output_jsonPath, self.output_unmodified_bgiPath)
        self.convert_bgi_to_bgd(self.output_bgi_name,
                                self.output_abs_bgi_folder,
                                self.output_bgd_name,
                                self.output_bgd_folder,
                                BLADEGENfolderPath = self.std_BLADEGEN_Folder)
        return