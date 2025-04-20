import os
import json
import logging
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file, session
from werkzeug.utils import secure_filename
from app import app, db
from models import Project, BuildingCode, OutputFile, Feedback, SpatialData, MEPDesign
from utils.blueprint_parser import parse_blueprint
from utils.code_parser import parse_building_code
from utils.mep_engine import generate_mep_design
from utils.pathfinding import optimize_routing
from utils.cad_generator import generate_cad_output

# Configure logging
logger = logging.getLogger(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'blueprints'))
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'codes'))
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'outputs'))

# Allowed file extensions
ALLOWED_BLUEPRINT_EXTENSIONS = {'dwg', 'dxf', 'rvt', 'ifc'}
ALLOWED_CODE_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_blueprint_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_BLUEPRINT_EXTENSIONS

def allowed_code_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_CODE_EXTENSIONS

@app.route('/')
def index():
    """Home page"""
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('index.html', projects=projects)

@app.route('/project/new', methods=['GET', 'POST'])
def new_project():
    """Create a new project"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        
        # Basic validation
        if not name:
            flash('Project name is required', 'danger')
            return redirect(url_for('new_project'))
            
        # Create new project
        project = Project(
            name=name,
            description=description
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash('Project created successfully', 'success')
        return redirect(url_for('project_detail', project_id=project.id))
        
    return render_template('upload.html')

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    """Show project details"""
    project = Project.query.get_or_404(project_id)
    return render_template('project.html', project=project)

@app.route('/project/<int:project_id>/upload', methods=['GET', 'POST'])
def upload_files(project_id):
    """Upload project files (blueprints and building codes)"""
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        # Check if blueprint file was uploaded
        if 'blueprint' in request.files:
            blueprint_file = request.files['blueprint']
            if blueprint_file.filename and allowed_blueprint_file(blueprint_file.filename):
                # Save blueprint file
                filename = secure_filename(blueprint_file.filename)
                blueprint_path = os.path.join(UPLOAD_FOLDER, 'blueprints', f"{project_id}_{filename}")
                blueprint_file.save(blueprint_path)
                
                # Update project
                project.blueprint_file = blueprint_path
                
                # Parse blueprint
                try:
                    spatial_data = parse_blueprint(blueprint_path)
                    
                    # Save spatial data to database
                    for data_type, data in spatial_data.items():
                        spatial_entry = SpatialData(
                            project_id=project.id,
                            data_type=data_type,
                            data=data
                        )
                        db.session.add(spatial_entry)
                        
                    flash('Blueprint uploaded and parsed successfully', 'success')
                except Exception as e:
                    logger.error(f"Error parsing blueprint: {str(e)}")
                    flash(f'Error parsing blueprint: {str(e)}', 'danger')
            else:
                flash('Invalid blueprint file. Allowed extensions: dwg, dxf, rvt, ifc', 'danger')
        
        # Check if building code file was uploaded
        if 'building_code' in request.files:
            code_file = request.files['building_code']
            if code_file.filename and allowed_code_file(code_file.filename):
                # Save code file
                filename = secure_filename(code_file.filename)
                code_path = os.path.join(UPLOAD_FOLDER, 'codes', f"{project_id}_{filename}")
                code_file.save(code_path)
                
                # Update project
                project.building_code_file = code_path
                
                # Parse building code
                try:
                    code_rules = parse_building_code(code_path)
                    
                    # Save code rules to database
                    for rule in code_rules:
                        code_entry = BuildingCode(
                            code_type=rule['type'],
                            region=rule.get('region', 'Unknown'),
                            rule_id=rule.get('id', ''),
                            description=rule['description'],
                            rule_data=rule
                        )
                        db.session.add(code_entry)
                        
                    flash('Building code uploaded and parsed successfully', 'success')
                except Exception as e:
                    logger.error(f"Error parsing building code: {str(e)}")
                    flash(f'Error parsing building code: {str(e)}', 'danger')
            else:
                flash('Invalid building code file. Allowed extensions: pdf, docx, txt', 'danger')
        
        # Save requirements if provided
        if 'requirements' in request.form:
            try:
                requirements = json.loads(request.form['requirements'])
                project.requirements = requirements
                flash('Requirements saved successfully', 'success')
            except Exception as e:
                logger.error(f"Error saving requirements: {str(e)}")
                flash(f'Error saving requirements: {str(e)}', 'danger')
                
        # Commit changes to database
        db.session.commit()
        return redirect(url_for('project_detail', project_id=project.id))
    
    return render_template('upload.html', project=project)

@app.route('/project/<int:project_id>/generate', methods=['POST'])
def generate_design(project_id):
    """Generate MEP design based on project data"""
    project = Project.query.get_or_404(project_id)
    
    try:
        # Check if we have necessary data
        if not project.blueprint_file:
            flash('Blueprint is required for design generation', 'danger')
            return redirect(url_for('project_detail', project_id=project.id))
            
        # Get spatial data
        spatial_data = SpatialData.query.filter_by(project_id=project_id).all()
        if not spatial_data:
            flash('Spatial data could not be found. Please re-upload blueprint', 'danger')
            return redirect(url_for('project_detail', project_id=project.id))
            
        # Get building codes
        building_codes = BuildingCode.query.all()
        
        # Compile spatial data
        spatial_data_dict = {}
        for data in spatial_data:
            spatial_data_dict[data.data_type] = data.data
            
        # Compile building codes
        code_rules = [{"type": code.code_type, 
                       "region": code.region, 
                       "id": code.rule_id, 
                       "description": code.description, 
                       **code.rule_data} for code in building_codes]
        
        # Generate MEP design
        mep_design = generate_mep_design(
            spatial_data_dict, 
            code_rules,
            project.requirements or {}
        )
        
        # Optimize routing
        optimized_design = optimize_routing(mep_design, spatial_data_dict)
        
        # Save design data
        for design_type, design_data in optimized_design.items():
            # Check if design already exists
            existing_design = MEPDesign.query.filter_by(
                project_id=project.id, 
                design_type=design_type
            ).first()
            
            if existing_design:
                existing_design.design_data = design_data
                existing_design.updated_at = datetime.utcnow()
            else:
                new_design = MEPDesign(
                    project_id=project.id,
                    design_type=design_type,
                    design_data=design_data
                )
                db.session.add(new_design)
        
        # Generate CAD output
        output_files = generate_cad_output(
            project.id, 
            optimized_design,
            os.path.join(UPLOAD_FOLDER, 'outputs')
        )
        
        # Save output file references
        for file_type, file_path in output_files.items():
            output_file = OutputFile(
                project_id=project.id,
                file_type=file_type,
                file_path=file_path
            )
            db.session.add(output_file)
        
        # Update project design data
        project.design_data = optimized_design
        
        # Commit changes
        db.session.commit()
        
        flash('MEP design generated successfully', 'success')
        return redirect(url_for('view_design', project_id=project.id))
        
    except Exception as e:
        logger.error(f"Error generating design: {str(e)}")
        flash(f'Error generating design: {str(e)}', 'danger')
        return redirect(url_for('project_detail', project_id=project.id))

@app.route('/project/<int:project_id>/design')
def view_design(project_id):
    """View generated MEP design"""
    project = Project.query.get_or_404(project_id)
    
    # Get MEP designs
    mep_designs = MEPDesign.query.filter_by(project_id=project_id).all()
    
    # Get output files
    output_files = OutputFile.query.filter_by(project_id=project_id).all()
    
    if not mep_designs:
        flash('No design has been generated yet', 'warning')
        return redirect(url_for('project_detail', project_id=project.id))
        
    return render_template('design.html', project=project, designs=mep_designs, outputs=output_files)

@app.route('/project/<int:project_id>/feedback', methods=['GET', 'POST'])
def project_feedback(project_id):
    """Submit feedback for a project"""
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        component = request.form.get('component')
        comment = request.form.get('comment')
        
        if not comment:
            flash('Comment is required', 'danger')
            return redirect(url_for('project_feedback', project_id=project.id))
            
        feedback = Feedback(
            project_id=project.id,
            component=component,
            comment=comment
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        flash('Feedback submitted successfully', 'success')
        return redirect(url_for('view_design', project_id=project.id))
        
    # Get all feedback for this project
    feedbacks = Feedback.query.filter_by(project_id=project_id).order_by(Feedback.created_at.desc()).all()
    
    return render_template('feedback.html', project=project, feedbacks=feedbacks)

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download a file"""
    return send_file(filename, as_attachment=True)

@app.route('/api/design/<int:project_id>', methods=['GET'])
def get_design_data(project_id):
    """API endpoint to get design data for visualization"""
    designs = MEPDesign.query.filter_by(project_id=project_id).all()
    
    if not designs:
        return jsonify({"error": "No design data found"}), 404
        
    design_data = {}
    for design in designs:
        design_data[design.design_type] = design.design_data
        
    return jsonify(design_data)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
