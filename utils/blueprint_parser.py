"""
Blueprint Parser Module

This module handles parsing and data extraction from various CAD/BIM formats:
- DWG/DXF using ezdxf
- IFC using IfcOpenShell (if available)
"""

import os
import json
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Check if ezdxf is available
try:
    import ezdxf
    from ezdxf.addons import odafc
    DXF_SUPPORT = True
except ImportError:
    logger.warning("ezdxf not available, DXF parsing will be limited")
    DXF_SUPPORT = False

# Check if IfcOpenShell is available
try:
    import ifcopenshell
    IFC_SUPPORT = True
except ImportError:
    logger.warning("IfcOpenShell not available, IFC parsing will be limited")
    IFC_SUPPORT = False

def parse_blueprint(file_path):
    """
    Parse blueprint file and extract spatial data
    
    Args:
        file_path: Path to the blueprint file
        
    Returns:
        dict: Dictionary containing spatial data extracted from the blueprint
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext in ['.dwg', '.dxf']:
        return parse_dxf(file_path)
    elif file_ext in ['.ifc']:
        return parse_ifc(file_path)
    elif file_ext in ['.rvt']:
        # Revit files require the Revit API, we'll use a placeholder
        return parse_revit(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")

def parse_dxf(file_path):
    """
    Parse DXF/DWG file using ezdxf
    
    Args:
        file_path: Path to the DXF/DWG file
        
    Returns:
        dict: Dictionary containing extracted spatial data
    """
    try:
        # For DWG files, convert to DXF first
        if file_path.lower().endswith('.dwg'):
            dxf_file = file_path.replace('.dwg', '.dxf')
            odafc.convert(file_path, dxf_file)
            file_path = dxf_file
        
        # Open the DXF file
        doc = ezdxf.readfile(file_path)
        
        # Extract model space
        msp = doc.modelspace()
        
        # Extract spatial data
        spaces = []
        walls = []
        doors = []
        windows = []
        
        # Process entities in the DXF file
        for entity in msp:
            if entity.dxftype() == 'LINE':
                # Walls are often represented as lines
                walls.append({
                    'type': 'wall',
                    'start': [entity.dxf.start.x, entity.dxf.start.y],
                    'end': [entity.dxf.end.x, entity.dxf.end.y],
                    'layer': entity.dxf.layer
                })
            elif entity.dxftype() == 'POLYLINE' or entity.dxftype() == 'LWPOLYLINE':
                # Rooms are often represented as polylines
                vertices = []
                for vertex in entity.vertices():
                    vertices.append([vertex.x, vertex.y])
                
                spaces.append({
                    'type': 'space',
                    'vertices': vertices,
                    'layer': entity.dxf.layer
                })
            elif entity.dxftype() == 'INSERT':
                # Doors and windows are often blocks
                if 'DOOR' in entity.dxf.name.upper():
                    doors.append({
                        'type': 'door',
                        'position': [entity.dxf.insert.x, entity.dxf.insert.y],
                        'rotation': entity.dxf.rotation,
                        'name': entity.dxf.name
                    })
                elif 'WINDOW' in entity.dxf.name.upper():
                    windows.append({
                        'type': 'window',
                        'position': [entity.dxf.insert.x, entity.dxf.insert.y],
                        'rotation': entity.dxf.rotation,
                        'name': entity.dxf.name
                    })
        
        # Compile spatial data
        spatial_data = {
            'spaces': spaces,
            'walls': walls,
            'doors': doors,
            'windows': windows
        }
        
        return spatial_data
        
    except Exception as e:
        logger.error(f"Error parsing DXF file: {str(e)}")
        # Return placeholder data if parsing fails
        return get_placeholder_spatial_data()

def parse_ifc(file_path):
    """
    Parse IFC file using IfcOpenShell
    
    Args:
        file_path: Path to the IFC file
        
    Returns:
        dict: Dictionary containing extracted spatial data
    """
    if not IFC_SUPPORT:
        logger.warning("IfcOpenShell not available, using placeholder data")
        return get_placeholder_spatial_data()
    
    try:
        # Open the IFC file
        ifc_file = ifcopenshell.open(file_path)
        
        # Extract spaces
        spaces = []
        for space in ifc_file.by_type('IfcSpace'):
            # Extract space geometry
            representation = space.Representation
            if representation:
                # This is simplified - real implementation would extract actual geometry
                spaces.append({
                    'type': 'space',
                    'id': space.id(),
                    'name': space.Name if hasattr(space, 'Name') else f"Space_{space.id()}",
                    'long_name': space.LongName if hasattr(space, 'LongName') else ""
                })
        
        # Extract walls
        walls = []
        for wall in ifc_file.by_type('IfcWall'):
            # Extract wall geometry
            representation = wall.Representation
            if representation:
                # This is simplified - real implementation would extract actual geometry
                walls.append({
                    'type': 'wall',
                    'id': wall.id(),
                    'name': wall.Name if hasattr(wall, 'Name') else f"Wall_{wall.id()}"
                })
        
        # Extract doors
        doors = []
        for door in ifc_file.by_type('IfcDoor'):
            # Extract door geometry
            representation = door.Representation
            if representation:
                # This is simplified - real implementation would extract actual geometry
                doors.append({
                    'type': 'door',
                    'id': door.id(),
                    'name': door.Name if hasattr(door, 'Name') else f"Door_{door.id()}"
                })
        
        # Extract windows
        windows = []
        for window in ifc_file.by_type('IfcWindow'):
            # Extract window geometry
            representation = window.Representation
            if representation:
                # This is simplified - real implementation would extract actual geometry
                windows.append({
                    'type': 'window',
                    'id': window.id(),
                    'name': window.Name if hasattr(window, 'Name') else f"Window_{window.id()}"
                })
        
        # Compile spatial data
        spatial_data = {
            'spaces': spaces,
            'walls': walls,
            'doors': doors,
            'windows': windows
        }
        
        return spatial_data
        
    except Exception as e:
        logger.error(f"Error parsing IFC file: {str(e)}")
        # Return placeholder data if parsing fails
        return get_placeholder_spatial_data()

def parse_revit(file_path):
    """
    Parse Revit file (placeholder implementation)
    
    Args:
        file_path: Path to the Revit file
        
    Returns:
        dict: Dictionary containing extracted spatial data
    """
    logger.warning("Revit file parsing is not fully implemented, using placeholder data")
    return get_placeholder_spatial_data()

def get_placeholder_spatial_data():
    """
    Generate placeholder spatial data for testing
    
    Returns:
        dict: Dictionary containing placeholder spatial data
    """
    return {
        'spaces': [
            {
                'type': 'space',
                'id': '1',
                'name': 'Living Room',
                'vertices': [[0, 0], [5, 0], [5, 4], [0, 4]]
            },
            {
                'type': 'space',
                'id': '2',
                'name': 'Kitchen',
                'vertices': [[5, 0], [9, 0], [9, 4], [5, 4]]
            },
            {
                'type': 'space',
                'id': '3',
                'name': 'Bathroom',
                'vertices': [[0, 4], [3, 4], [3, 7], [0, 7]]
            },
            {
                'type': 'space',
                'id': '4',
                'name': 'Bedroom',
                'vertices': [[3, 4], [9, 4], [9, 7], [3, 7]]
            }
        ],
        'walls': [
            {'type': 'wall', 'start': [0, 0], 'end': [9, 0]},
            {'type': 'wall', 'start': [9, 0], 'end': [9, 7]},
            {'type': 'wall', 'start': [9, 7], 'end': [0, 7]},
            {'type': 'wall', 'start': [0, 7], 'end': [0, 0]},
            {'type': 'wall', 'start': [5, 0], 'end': [5, 4]},
            {'type': 'wall', 'start': [0, 4], 'end': [9, 4]},
            {'type': 'wall', 'start': [3, 4], 'end': [3, 7]}
        ],
        'doors': [
            {'type': 'door', 'position': [2, 0], 'rotation': 0, 'width': 0.9},
            {'type': 'door', 'position': [5, 2], 'rotation': 90, 'width': 0.8},
            {'type': 'door', 'position': [1.5, 4], 'rotation': 0, 'width': 0.8},
            {'type': 'door', 'position': [6, 4], 'rotation': 0, 'width': 0.8}
        ],
        'windows': [
            {'type': 'window', 'position': [4, 0], 'rotation': 0, 'width': 1.2},
            {'type': 'window', 'position': [7, 0], 'rotation': 0, 'width': 1.2},
            {'type': 'window', 'position': [9, 2], 'rotation': 90, 'width': 1.0},
            {'type': 'window', 'position': [9, 6], 'rotation': 90, 'width': 1.0},
            {'type': 'window', 'position': [6, 7], 'rotation': 0, 'width': 1.2}
        ]
    }
