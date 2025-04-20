"""
MEP Design Engine Module

This module handles the generation of MEP (Mechanical, Electrical, Plumbing) designs
based on spatial data, building code rules, and user requirements.
"""

import logging
import math
import random
import json
from utils.pathfinding import find_path, Point

# Configure logger
logger = logging.getLogger(__name__)

def generate_mep_design(spatial_data, code_rules, requirements):
    """
    Generate MEP design based on spatial data, building code rules, and user requirements
    
    Args:
        spatial_data: Dictionary containing spatial data extracted from the blueprint
        code_rules: List of dictionaries containing building code rules
        requirements: Dictionary containing user requirements
        
    Returns:
        dict: Dictionary containing generated MEP design data
    """
    logger.info("Generating MEP design")
    
    # Initialize the design data
    design_data = {
        'mechanical': generate_mechanical_design(spatial_data, code_rules, requirements),
        'electrical': generate_electrical_design(spatial_data, code_rules, requirements),
        'plumbing': generate_plumbing_design(spatial_data, code_rules, requirements)
    }
    
    return design_data

def generate_mechanical_design(spatial_data, code_rules, requirements):
    """
    Generate mechanical design (HVAC)
    
    Args:
        spatial_data: Dictionary containing spatial data
        code_rules: List of dictionaries containing building code rules
        requirements: Dictionary containing user requirements
        
    Returns:
        dict: Dictionary containing mechanical design data
    """
    logger.info("Generating mechanical (HVAC) design")
    
    # Get mechanical-specific code rules
    mechanical_rules = [rule for rule in code_rules if rule['type'] == 'M']
    
    # Extract spaces from spatial data
    spaces = spatial_data.get('spaces', [])
    
    # Generate HVAC components
    air_handlers = []
    diffusers = []
    ducts = []
    
    # Place a central air handler
    ahu_location = find_utility_location(spatial_data)
    air_handlers.append({
        'id': 'AHU-1',
        'type': 'air_handler',
        'position': ahu_location,
        'capacity': calculate_total_cooling_load(spaces, requirements)
    })
    
    # Place diffusers in each space
    for i, space in enumerate(spaces):
        # Calculate room area
        area = calculate_space_area(space)
        
        # Determine number of diffusers based on area
        num_diffusers = max(1, int(area / 20))  # One diffuser per 20 sq meters
        
        for j in range(num_diffusers):
            # Place diffuser at a reasonable position within the space
            diffuser_pos = get_point_in_space(space, 0.5)  # 50% of the way into the space
            
            diffuser = {
                'id': f'DIFF-{i+1}-{j+1}',
                'type': 'diffuser',
                'position': diffuser_pos,
                'flow_rate': 200  # CFM
            }
            diffusers.append(diffuser)
            
            # Create duct from AHU to diffuser
            path_points = find_path(ahu_location, diffuser_pos, spatial_data)
            
            if path_points:
                duct = {
                    'id': f'DUCT-{i+1}-{j+1}',
                    'type': 'duct',
                    'path': path_points,
                    'diameter': 12,  # inches
                    'source': 'AHU-1',
                    'target': f'DIFF-{i+1}-{j+1}'
                }
                ducts.append(duct)
    
    # Create mechanical design data
    mechanical_design = {
        'air_handlers': air_handlers,
        'diffusers': diffusers,
        'ducts': ducts
    }
    
    return mechanical_design

def generate_electrical_design(spatial_data, code_rules, requirements):
    """
    Generate electrical design
    
    Args:
        spatial_data: Dictionary containing spatial data
        code_rules: List of dictionaries containing building code rules
        requirements: Dictionary containing user requirements
        
    Returns:
        dict: Dictionary containing electrical design data
    """
    logger.info("Generating electrical design")
    
    # Get electrical-specific code rules
    electrical_rules = [rule for rule in code_rules if rule['type'] == 'E']
    
    # Extract spaces from spatial data
    spaces = spatial_data.get('spaces', [])
    
    # Generate electrical components
    panels = []
    outlets = []
    lights = []
    conduits = []
    
    # Place a main electrical panel
    panel_location = find_utility_location(spatial_data)
    panels.append({
        'id': 'PANEL-MAIN',
        'type': 'panel',
        'position': panel_location,
        'rating': 200  # Amps
    })
    
    # Place outlets and lights in each space
    for i, space in enumerate(spaces):
        # Calculate room area
        area = calculate_space_area(space)
        
        # Determine number of outlets based on area and code requirements
        # Typically 1 outlet per 12 sq ft of wall space
        perimeter = calculate_space_perimeter(space)
        num_outlets = max(2, int(perimeter / 12))
        
        # Place outlets around the perimeter
        for j in range(num_outlets):
            # Place outlet on the perimeter
            outlet_pos = get_point_on_perimeter(space, j / num_outlets)
            
            outlet = {
                'id': f'OUTLET-{i+1}-{j+1}',
                'type': 'outlet',
                'position': outlet_pos,
                'circuit': j % 3 + 1  # Distribute across 3 circuits
            }
            outlets.append(outlet)
            
            # Create conduit from panel to outlet
            path_points = find_path(panel_location, outlet_pos, spatial_data)
            
            if path_points:
                conduit = {
                    'id': f'CONDUIT-O-{i+1}-{j+1}',
                    'type': 'conduit',
                    'path': path_points,
                    'size': 0.75,  # inches
                    'source': 'PANEL-MAIN',
                    'target': f'OUTLET-{i+1}-{j+1}'
                }
                conduits.append(conduit)
        
        # Determine number of lights based on area
        # Typically 1 light fixture per 50-100 sq ft
        num_lights = max(1, int(area / 50))
        
        # Place lights in a grid pattern
        for j in range(num_lights):
            # Place light at a reasonable position within the space
            light_pos = get_point_in_space(space, (j + 0.5) / num_lights)
            
            light = {
                'id': f'LIGHT-{i+1}-{j+1}',
                'type': 'light',
                'position': light_pos,
                'circuit': (j % 2) + 4  # Lighting circuits start at 4
            }
            lights.append(light)
            
            # Create conduit from panel to light
            path_points = find_path(panel_location, light_pos, spatial_data)
            
            if path_points:
                conduit = {
                    'id': f'CONDUIT-L-{i+1}-{j+1}',
                    'type': 'conduit',
                    'path': path_points,
                    'size': 0.5,  # inches
                    'source': 'PANEL-MAIN',
                    'target': f'LIGHT-{i+1}-{j+1}'
                }
                conduits.append(conduit)
    
    # Create electrical design data
    electrical_design = {
        'panels': panels,
        'outlets': outlets,
        'lights': lights,
        'conduits': conduits
    }
    
    return electrical_design

def generate_plumbing_design(spatial_data, code_rules, requirements):
    """
    Generate plumbing design
    
    Args:
        spatial_data: Dictionary containing spatial data
        code_rules: List of dictionaries containing building code rules
        requirements: Dictionary containing user requirements
        
    Returns:
        dict: Dictionary containing plumbing design data
    """
    logger.info("Generating plumbing design")
    
    # Get plumbing-specific code rules
    plumbing_rules = [rule for rule in code_rules if rule['type'] == 'P']
    
    # Extract spaces from spatial data
    spaces = spatial_data.get('spaces', [])
    
    # Generate plumbing components
    fixtures = []
    pipes = []
    
    # Place a main water source and drain
    utility_location = find_utility_location(spatial_data)
    water_source = {
        'id': 'WATER-MAIN',
        'type': 'water_source',
        'position': utility_location
    }
    drain_main = {
        'id': 'DRAIN-MAIN',
        'type': 'drain',
        'position': [utility_location[0], utility_location[1] + 1]  # Slightly offset from water source
    }
    
    fixtures.append(water_source)
    fixtures.append(drain_main)
    
    # Identify bathroom spaces (simplified approach)
    bathroom_spaces = []
    for i, space in enumerate(spaces):
        # Check if space name contains bathroom/restroom-related terms
        if hasattr(space, 'name') and any(term in space['name'].lower() for term in ['bath', 'restroom', 'toilet', 'wc']):
            bathroom_spaces.append(space)
        # If no name is available, assume the 3rd space is a bathroom (for demo)
        elif i == 2:
            bathroom_spaces.append(space)
    
    # Place plumbing fixtures in bathroom spaces
    for i, space in enumerate(bathroom_spaces):
        # Get center point of the bathroom
        center = get_point_in_space(space, 0.5)
        
        # Place a toilet
        toilet_pos = get_point_in_space(space, 0.3)  # 30% into the space
        toilet = {
            'id': f'TOILET-{i+1}',
            'type': 'toilet',
            'position': toilet_pos
        }
        fixtures.append(toilet)
        
        # Place a sink
        sink_pos = get_point_in_space(space, 0.7)  # 70% into the space
        sink = {
            'id': f'SINK-{i+1}',
            'type': 'sink',
            'position': sink_pos
        }
        fixtures.append(sink)
        
        # Create water supply pipe from main to sink
        water_path = find_path(utility_location, sink_pos, spatial_data)
        if water_path:
            water_pipe = {
                'id': f'WATER-PIPE-{i+1}',
                'type': 'water_pipe',
                'path': water_path,
                'diameter': 0.75,  # inches
                'source': 'WATER-MAIN',
                'target': f'SINK-{i+1}'
            }
            pipes.append(water_pipe)
        
        # Create drain pipe from sink to main drain
        sink_drain_path = find_path(sink_pos, drain_main['position'], spatial_data)
        if sink_drain_path:
            sink_drain = {
                'id': f'SINK-DRAIN-{i+1}',
                'type': 'drain_pipe',
                'path': sink_drain_path,
                'diameter': 1.5,  # inches
                'source': f'SINK-{i+1}',
                'target': 'DRAIN-MAIN'
            }
            pipes.append(sink_drain)
        
        # Create drain pipe from toilet to main drain
        toilet_drain_path = find_path(toilet_pos, drain_main['position'], spatial_data)
        if toilet_drain_path:
            toilet_drain = {
                'id': f'TOILET-DRAIN-{i+1}',
                'type': 'drain_pipe',
                'path': toilet_drain_path,
                'diameter': 3,  # inches
                'source': f'TOILET-{i+1}',
                'target': 'DRAIN-MAIN'
            }
            pipes.append(toilet_drain)
        
        # Create water supply pipe from main to toilet
        toilet_water_path = find_path(utility_location, toilet_pos, spatial_data)
        if toilet_water_path:
            toilet_water = {
                'id': f'TOILET-WATER-{i+1}',
                'type': 'water_pipe',
                'path': toilet_water_path,
                'diameter': 0.5,  # inches
                'source': 'WATER-MAIN',
                'target': f'TOILET-{i+1}'
            }
            pipes.append(toilet_water)
    
    # Create plumbing design data
    plumbing_design = {
        'fixtures': fixtures,
        'pipes': pipes
    }
    
    return plumbing_design

def find_utility_location(spatial_data):
    """
    Find a suitable location for utility equipment
    
    Args:
        spatial_data: Dictionary containing spatial data
        
    Returns:
        list: [x, y] coordinates for utility placement
    """
    # Look for spaces first (if they have names/types)
    spaces = spatial_data.get('spaces', [])
    
    for space in spaces:
        # Check if space name contains utility-related terms
        if hasattr(space, 'name') and any(term in space['name'].lower() for term in ['utility', 'mechanical', 'electrical']):
            return get_point_in_space(space, 0.5)  # Center of the utility room
    
    # If no utility room found, place near a corner of the overall layout
    all_points = []
    
    # Collect all wall points
    walls = spatial_data.get('walls', [])
    for wall in walls:
        if 'start' in wall and 'end' in wall:
            all_points.append(wall['start'])
            all_points.append(wall['end'])
    
    # Collect all space vertices
    for space in spaces:
        if 'vertices' in space:
            all_points.extend(space['vertices'])
    
    # If we have points, find the minimum x and y coordinates
    if all_points:
        min_x = min(point[0] for point in all_points)
        min_y = min(point[1] for point in all_points)
        max_x = max(point[0] for point in all_points)
        max_y = max(point[1] for point in all_points)
        
        # Place utility in the bottom left corner plus a small offset
        return [min_x + 1, min_y + 1]
    
    # Fallback to a default position
    return [0, 0]

def calculate_space_area(space):
    """
    Calculate the area of a space
    
    Args:
        space: Dictionary containing space data
        
    Returns:
        float: Area of the space
    """
    if 'vertices' in space:
        vertices = space['vertices']
        
        # Calculate area using the Shoelace formula
        n = len(vertices)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i][0] * vertices[j][1]
            area -= vertices[j][0] * vertices[i][1]
        area = abs(area) / 2.0
        
        return area
    
    # Default area if vertices not available
    return 100.0  # Square feet

def calculate_space_perimeter(space):
    """
    Calculate the perimeter of a space
    
    Args:
        space: Dictionary containing space data
        
    Returns:
        float: Perimeter of the space
    """
    if 'vertices' in space:
        vertices = space['vertices']
        
        # Calculate perimeter
        n = len(vertices)
        perimeter = 0.0
        for i in range(n):
            j = (i + 1) % n
            dx = vertices[j][0] - vertices[i][0]
            dy = vertices[j][1] - vertices[i][1]
            perimeter += math.sqrt(dx*dx + dy*dy)
        
        return perimeter
    
    # Default perimeter if vertices not available
    return 40.0  # Linear feet

def get_point_in_space(space, ratio=0.5):
    """
    Get a point within a space at the specified ratio from center
    
    Args:
        space: Dictionary containing space data
        ratio: Float between 0 and 1 to determine position
        
    Returns:
        list: [x, y] coordinates of the point
    """
    if 'vertices' in space:
        vertices = space['vertices']
        
        # Calculate centroid
        n = len(vertices)
        cx = sum(v[0] for v in vertices) / n
        cy = sum(v[1] for v in vertices) / n
        
        # Find point at the specified ratio from center to a random vertex
        vertex = random.choice(vertices)
        x = cx + (vertex[0] - cx) * ratio
        y = cy + (vertex[1] - cy) * ratio
        
        return [x, y]
    
    # Default position if vertices not available
    return [0, 0]

def get_point_on_perimeter(space, ratio=0):
    """
    Get a point on the perimeter of a space
    
    Args:
        space: Dictionary containing space data
        ratio: Float between 0 and 1 to determine position along perimeter
        
    Returns:
        list: [x, y] coordinates of the point
    """
    if 'vertices' in space:
        vertices = space['vertices']
        n = len(vertices)
        
        # Calculate the perimeter segments
        segments = []
        total_length = 0
        
        for i in range(n):
            j = (i + 1) % n
            dx = vertices[j][0] - vertices[i][0]
            dy = vertices[j][1] - vertices[i][1]
            length = math.sqrt(dx*dx + dy*dy)
            
            segments.append({
                'start': vertices[i],
                'end': vertices[j],
                'length': length,
                'cumulative': total_length
            })
            
            total_length += length
        
        # Add total to each segment
        for segment in segments:
            segment['total'] = total_length
        
        # Find the target position
        target_distance = total_length * ratio
        
        # Find the segment containing the target position
        for segment in segments:
            if segment['cumulative'] <= target_distance < (segment['cumulative'] + segment['length']):
                # Calculate position along this segment
                segment_ratio = (target_distance - segment['cumulative']) / segment['length']
                
                x = segment['start'][0] + segment_ratio * (segment['end'][0] - segment['start'][0])
                y = segment['start'][1] + segment_ratio * (segment['end'][1] - segment['start'][1])
                
                return [x, y]
        
        # Fallback to first vertex
        return vertices[0]
    
    # Default position if vertices not available
    return [0, 0]

def calculate_total_cooling_load(spaces, requirements):
    """
    Calculate the total cooling load for the spaces
    
    Args:
        spaces: List of dictionaries containing space data
        requirements: Dictionary containing user requirements
        
    Returns:
        float: Total cooling load in BTU/h
    """
    total_area = sum(calculate_space_area(space) for space in spaces)
    
    # Default cooling load: 400 BTU/h per sq ft
    cooling_load_per_sqft = 400
    
    # Adjust based on requirements if specified
    if 'cooling_load' in requirements:
        cooling_load_per_sqft = requirements['cooling_load']
    
    total_load = total_area * cooling_load_per_sqft
    
    return total_load
