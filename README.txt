# BGD Geometry Generator

## Overview
The BGD Geometry Generator is a Python-based tool designed to generate and manipulate geometric configurations for blade design, specifically for use with the Ansys BladeGen library. The main script, `generator.py`, contains several functions that facilitate the creation, modification, and analysis of blade geometries.

## Purpose of `generator.py`
The `generator.py` script is the core component of the BGD Geometry Generator. It includes various functions that allow users to generate blade geometries, apply transformations, and export the results for further analysis or use in other applications.

## Functions in `generator.py`
1. **GeometrySettings**
    - **Description**: A class that encapsulates the settings and parameters for defining the geometry of the blade, including blade parameters, hub and shroud parameters, and splitter settings.
    - **Parameters**: Various attributes such as `beta_in`, `beta_out`, `thickness`, `tau`, `w1`, `beta_bezier_N`, `L_ind`, `L_comp`, `r2s`, `r2h`, `r4`, `b4`, `r5`, `modify_HubShroud`, `w1_hb`, `w1_sh`, `splitter_LE_meridional_target_hub`, and `splitter_LE_meridional_target_sh`.
    - **Returns**: An instance of the `GeometrySettings` class with the specified parameters.

2. **StateFileModifier**
    - **Description**: A class responsible for modifying the state file of the blade geometry based on the provided geometry settings and file paths.
    - **Parameters**: 
      - `geometry_settings`: An instance of `GeometrySettings` containing the blade geometry parameters.
      - `defaultfilePath`: The path to the default geometry file.
      - `destination_path`: The path where the modified geometry file will be saved.
      - `std_BLADEGEN_Folder`: The path to the BladeGen folders.
    - **Returns**: An instance of the `StateFileModifier` class.

3. **create_modified_geometry()**
    - **Description**: A method of the `StateFileModifier` class that creates a modified geometry file based on the provided geometry settings and saves it to the specified destination path.

## Author
Davide Lisi

## Contact
For any questions or further information, please contact Davide at davide.lisi@epfl.ch.
