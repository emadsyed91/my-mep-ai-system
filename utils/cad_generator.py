"""
CAD Generator Module

This module handles the generation of CAD/BIM output files from the MEP design data.
"""

import os
import logging
import json
import datetime

# Configure logger
logger = logging.getLogger(__name__)

try:
    # Try to import ezdxf for DXF generation
    import ezdxf
    from ezdxf.layouts import Modelspace
    DXF_SUPPORT = True
except ImportError:
    logger.warning("ezdxf not available, DXF generation will be limited")
    DXF_SUPPORT = False

try:
    # Try to import ifcopenshell for IFC generation
    import ifcopenshell
    IFC_SUPPORT = True
except ImportError:
    logger.warning("ifcopenshell not available, IFC generation will be limited")
    IFC_SUPPORT = False

def generate_cad_output(project_id, mep_design, output_dir):
    """
    Generate CAD/BIM output files from the MEP design data
    
    Args:
        project_id: ID of the project
        mep_design: Dictionary containing MEP design data
        output_dir: Directory to save output files
        
    Returns:
        dict: Dictionary mapping file types to file paths
    """
    logger.info(f"Generating CAD output for project {project_id}")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate output files
    output_files = {}
    
    # Generate DXF file
    dxf_path = os.path.join(output_dir, f"project_{project_id}_mep.dxf")
    if generate_dxf(dxf_path, mep_design):
        output_files['DXF'] = dxf_path
    
    # Generate IFC file
    ifc_path = os.path.join(output_dir, f"project_{project_id}_mep.ifc")
    if generate_ifc(ifc_path, mep_design):
        output_files['IFC'] = ifc_path
    
    # Generate JSON file (for web viewing)
    json_path = os.path.join(output_dir, f"project_{project_id}_mep.json")
    with open(json_path, 'w') as f:
        json.dump(mep_design, f, indent=2)
    output_files['JSON'] = json_path
    
    return output_files

def generate_dxf(filepath, mep_design):
    """
    Generate a DXF file from the MEP design data
    
    Args:
        filepath: Path to save the DXF file
        mep_design: Dictionary containing MEP design data
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not DXF_SUPPORT:
        logger.warning("DXF generation skipped, ezdxf not available")
        return False
    
    try:
        # Create a new DXF document
        doc = ezdxf.new('R2010')
        
        # Add layers for MEP components
        doc.layers.new('MECHANICAL', dxfattribs={'color': 1})  # Red
        doc.layers.new('ELECTRICAL', dxfattribs={'color': 5})  # Blue
        doc.layers.new('PLUMBING', dxfattribs={'color': 3})  # Green
        
        # Access the modelspace
        msp = doc.modelspace()
        
        # Draw mechanical components
        draw_mechanical_components(msp, mep_design.get('mechanical', {}))
        
        # Draw electrical components
        draw_electrical_components(msp, mep_design.get('electrical', {}))
        
        # Draw plumbing components
        draw_plumbing_components(msp, mep_design.get('plumbing', {}))
        
        # Save the DXF file
        doc.saveas(filepath)
        logger.info(f"DXF file saved to {filepath}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error generating DXF file: {str(e)}")
        return False

def draw_mechanical_components(msp, mechanical_design):
    """
    Draw mechanical components in the modelspace
    
    Args:
        msp: ezdxf.layouts.Modelspace
        mechanical_design: Dictionary containing mechanical design data
    """
    # Draw air handlers
    for ahu in mechanical_design.get('air_handlers', []):
        pos = ahu.get('position', [0, 0])
        
        # Draw AHU as a rectangle
        msp.add_lwpolyline(
            [(pos[0] - 1, pos[1] - 1), (pos[0] + 1, pos[1] - 1), 
             (pos[0] + 1, pos[1] + 1), (pos[0] - 1, pos[1] + 1), 
             (pos[0] - 1, pos[1] - 1)],
            dxfattribs={'layer': 'MECHANICAL'}
        )
        
        # Add text label
        msp.add_text(
            ahu.get('id', 'AHU'),
            dxfattribs={
                'layer': 'MECHANICAL',
                'height': 0.25
            }
        ).set_pos(pos)
    
    # Draw diffusers
    for diffuser in mechanical_design.get('diffusers', []):
        pos = diffuser.get('position', [0, 0])
        
        # Draw diffuser as a circle
        msp.add_circle(
            center=(pos[0], pos[1]),
            radius=0.3,
            dxfattribs={'layer': 'MECHANICAL'}
        )
        
        # Add text label
        msp.add_text(
            diffuser.get('id', 'DIFF'),
            dxfattribs={
                'layer': 'MECHANICAL',
                'height': 0.15
            }
        ).set_pos((pos[0], pos[1] - 0.4))
    
    # Draw ducts
    for duct in mechanical_design.get('ducts', []):
        path = duct.get('path', [])
        
        if len(path) >= 2:
            # Draw duct as a polyline
            points = [(p[0], p[1]) for p in path]
            msp.add_lwpolyline(
                points,
                dxfattribs={
                    'layer': 'MECHANICAL',
                    'lineweight': 30  # Thicker line for ducts
                }
            )

def draw_electrical_components(msp, electrical_design):
    """
    Draw electrical components in the modelspace
    
    Args:
        msp: ezdxf.layouts.Modelspace
        electrical_design: Dictionary containing electrical design data
    """
    # Draw panels
    for panel in electrical_design.get('panels', []):
        pos = panel.get('position', [0, 0])
        
        # Draw panel as a rectangle
        msp.add_lwpolyline(
            [(pos[0] - 0.5, pos[1] - 0.75), (pos[0] + 0.5, pos[1] - 0.75), 
             (pos[0] + 0.5, pos[1] + 0.75), (pos[0] - 0.5, pos[1] + 0.75), 
             (pos[0] - 0.5, pos[1] - 0.75)],
            dxfattribs={'layer': 'ELECTRICAL'}
        )
        
        # Add text label
        msp.add_text(
            panel.get('id', 'PANEL'),
            dxfattribs={
                'layer': 'ELECTRICAL',
                'height': 0.2
            }
        ).set_pos(pos)
    
    # Draw outlets
    for outlet in electrical_design.get('outlets', []):
        pos = outlet.get('position', [0, 0])
        
        # Draw outlet as a small square
        msp.add_lwpolyline(
            [(pos[0] - 0.15, pos[1] - 0.15), (pos[0] + 0.15, pos[1] - 0.15), 
             (pos[0] + 0.15, pos[1] + 0.15), (pos[0] - 0.15, pos[1] + 0.15), 
             (pos[0] - 0.15, pos[1] - 0.15)],
            dxfattribs={'layer': 'ELECTRICAL'}
        )
    
    # Draw lights
    for light in electrical_design.get('lights', []):
        pos = light.get('position', [0, 0])
        
        # Draw light as a circle with an X
        msp.add_circle(
            center=(pos[0], pos[1]),
            radius=0.2,
            dxfattribs={'layer': 'ELECTRICAL'}
        )
        
        # Add X inside circle
        msp.add_line(
            start=(pos[0] - 0.15, pos[1] - 0.15),
            end=(pos[0] + 0.15, pos[1] + 0.15),
            dxfattribs={'layer': 'ELECTRICAL'}
        )
        msp.add_line(
            start=(pos[0] - 0.15, pos[1] + 0.15),
            end=(pos[0] + 0.15, pos[1] - 0.15),
            dxfattribs={'layer': 'ELECTRICAL'}
        )
    
    # Draw conduits
    for conduit in electrical_design.get('conduits', []):
        path = conduit.get('path', [])
        
        if len(path) >= 2:
            # Draw conduit as a polyline
            points = [(p[0], p[1]) for p in path]
            msp.add_lwpolyline(
                points,
                dxfattribs={'layer': 'ELECTRICAL'}
            )

def draw_plumbing_components(msp, plumbing_design):
    """
    Draw plumbing components in the modelspace
    
    Args:
        msp: ezdxf.layouts.Modelspace
        plumbing_design: Dictionary containing plumbing design data
    """
    # Draw fixtures
    for fixture in plumbing_design.get('fixtures', []):
        pos = fixture.get('position', [0, 0])
        fixture_type = fixture.get('type', '')
        
        if fixture_type in ['toilet', 'water_closet']:
            # Draw toilet as an oval
            msp.add_ellipse(
                center=(pos[0], pos[1]),
                major_axis=(0.4, 0),
                ratio=0.7,
                dxfattribs={'layer': 'PLUMBING'}
            )
        elif fixture_type in ['sink', 'lavatory']:
            # Draw sink as a rectangle with rounded corners
            msp.add_lwpolyline(
                [(pos[0] - 0.3, pos[1] - 0.2), (pos[0] + 0.3, pos[1] - 0.2), 
                 (pos[0] + 0.3, pos[1] + 0.2), (pos[0] - 0.3, pos[1] + 0.2), 
                 (pos[0] - 0.3, pos[1] - 0.2)],
                dxfattribs={'layer': 'PLUMBING'}
            )
        elif fixture_type in ['water_source', 'water_main']:
            # Draw water source as a circle with a dot
            msp.add_circle(
                center=(pos[0], pos[1]),
                radius=0.3,
                dxfattribs={'layer': 'PLUMBING'}
            )
            msp.add_circle(
                center=(pos[0], pos[1]),
                radius=0.05,
                dxfattribs={'layer': 'PLUMBING'}
            )
        elif fixture_type in ['drain', 'drain_main']:
            # Draw drain as a circle with an X
            msp.add_circle(
                center=(pos[0], pos[1]),
                radius=0.3,
                dxfattribs={'layer': 'PLUMBING'}
            )
            msp.add_line(
                start=(pos[0] - 0.2, pos[1] - 0.2),
                end=(pos[0] + 0.2, pos[1] + 0.2),
                dxfattribs={'layer': 'PLUMBING'}
            )
            msp.add_line(
                start=(pos[0] - 0.2, pos[1] + 0.2),
                end=(pos[0] + 0.2, pos[1] - 0.2),
                dxfattribs={'layer': 'PLUMBING'}
            )
    
    # Draw pipes
    for pipe in plumbing_design.get('pipes', []):
        path = pipe.get('path', [])
        pipe_type = pipe.get('type', '')
        
        if len(path) >= 2:
            # Draw pipe as a polyline
            points = [(p[0], p[1]) for p in path]
            
            # Use different line styles for different pipe types
            if pipe_type in ['water_pipe', 'supply_pipe']:
                # Solid line for water supply
                msp.add_lwpolyline(
                    points,
                    dxfattribs={'layer': 'PLUMBING'}
                )
            else:
                # Dashed line for drainage
                msp.add_lwpolyline(
                    points,
                    dxfattribs={
                        'layer': 'PLUMBING',
                        'linetype': 'DASHED'
                    }
                )

def generate_ifc(filepath, mep_design):
    """
    Generate an IFC file from the MEP design data
    
    Args:
        filepath: Path to save the IFC file
        mep_design: Dictionary containing MEP design data
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not IFC_SUPPORT:
        logger.warning("IFC generation skipped, ifcopenshell not available")
        return False
    
    try:
        # Create a new IFC model
        model = ifcopenshell.file()
        
        # Create header
        model.create_entity(
            "IfcProject",
            GlobalId=ifcopenshell.guid.new(),
            Name="MEP Design Project"
        )
        
        # Note: Full IFC generation is complex and requires more implementation
        # This is a placeholder for future implementation
        
        # Save the IFC file
        model.write(filepath)
        logger.info(f"IFC file saved to {filepath}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error generating IFC file: {str(e)}")
        return False
