/**
 * Validate the project creation form
 */
function validateProjectForm() {
    const form = document.querySelector('form[action*="new_project"]');
    if (!form) return;
    
    form.addEventListener('submit', function(event) {
        let isValid = true;
        
        // Validate project name
        const nameInput = document.getElementById('name');
        if (nameInput && !nameInput.value.trim()) {
            isValid = false;
            showError(nameInput, 'Project name is required');
        } else if (nameInput) {
            clearError(nameInput);
        }
        
        // If form is not valid, prevent submission
        if (!isValid) {
            event.preventDefault();
        }
    });
    
    // Add input event listeners to clear errors as user types
    const nameInput = document.getElementById('name');
    if (nameInput) {
        nameInput.addEventListener('input', function() {
            if (nameInput.value.trim()) {
                clearError(nameInput);
            }
        });
    }
}

/**
 * Validate the file upload form
 */
function validateUploadForm() {
    const form = document.querySelector('form[action*="upload_files"]');
    if (!form) return;
    
    // Validate file extensions for blueprint upload
    const blueprintInput = document.getElementById('blueprint');
    if (blueprintInput) {
        blueprintInput.addEventListener('change', function() {
            if (blueprintInput.files.length > 0) {
                const file = blueprintInput.files[0];
                const fileName = file.name.toLowerCase();
                const validExtensions = ['.dwg', '.dxf', '.rvt', '.ifc'];
                
                let isValid = false;
                for (const ext of validExtensions) {
                    if (fileName.endsWith(ext)) {
                        isValid = true;
                        break;
                    }
                }
                
                if (!isValid) {
                    showError(blueprintInput, 'Invalid file type. Allowed: DWG, DXF, RVT, IFC');
                } else {
                    clearError(blueprintInput);
                }
            }
        });
    }
    
    // Validate file extensions for building code upload
    const codeInput = document.getElementById('building_code');
    if (codeInput) {
        codeInput.addEventListener('change', function() {
            if (codeInput.files.length > 0) {
                const file = codeInput.files[0];
                const fileName = file.name.toLowerCase();
                const validExtensions = ['.pdf', '.docx', '.txt'];
                
                let isValid = false;
                for (const ext of validExtensions) {
                    if (fileName.endsWith(ext)) {
                        isValid = true;
                        break;
                    }
                }
                
                if (!isValid) {
                    showError(codeInput, 'Invalid file type. Allowed: PDF, DOCX, TXT');
                } else {
                    clearError(codeInput);
                }
            }
        });
    }
    
    // Update the hidden requirements field before form submission
    form.addEventListener('submit', function(event) {
        // Update requirements JSON before submission
        updateRequirementsJSON();
    });
}

/**
 * Update the requirements JSON hidden field with form values
 */
function updateRequirementsJSON() {
    // Collect form values
    const requirements = {
        mechanical: {
            hvac_type: document.getElementById('hvac_type')?.value || 'forced_air',
            cooling_load: parseFloat(document.getElementById('cooling_load')?.value || 400)
        },
        electrical: {
            voltage: parseInt(document.getElementById('voltage')?.value || 120),
            lighting_density: parseFloat(document.getElementById('lighting_density')?.value || 1.5)
        },
        plumbing: {
            water_pressure: parseFloat(document.getElementById('water_pressure')?.value || 40),
            fixture_units: parseInt(document.getElementById('fixture_units')?.value || 20)
        }
    };
    
    // Update hidden field
    const hiddenField = document.getElementById('requirements');
    if (hiddenField) {
        hiddenField.value = JSON.stringify(requirements);
    }
}

/**
 * Validate the feedback form
 */
function validateFeedbackForm() {
    const form = document.querySelector('form[action*="feedback"]');
    if (!form) return;
    
    form.addEventListener('submit', function(event) {
        let isValid = true;
        
        // Validate comment field
        const commentInput = document.getElementById('comment');
        if (commentInput && !commentInput.value.trim()) {
            isValid = false;
            showError(commentInput, 'Comment is required');
        } else if (commentInput) {
            clearError(commentInput);
        }
        
        // If form is not valid, prevent submission
        if (!isValid) {
            event.preventDefault();
        }
    });
    
    // Add input event listeners to clear errors as user types
    const commentInput = document.getElementById('comment');
    if (commentInput) {
        commentInput.addEventListener('input', function() {
            if (commentInput.value.trim()) {
                clearError(commentInput);
            }
        });
    }
}

/**
 * Display an error message for an input field
 * @param {HTMLElement} input - The input element
 * @param {string} message - The error message to display
 */
function showError(input, message) {
    // Clear any existing error
    clearError(input);
    
    // Add invalid class to input
    input.classList.add('is-invalid');
    
    // Create error message element
    const errorElement = document.createElement('div');
    errorElement.className = 'invalid-feedback';
    errorElement.textContent = message;
    
    // Add error message after input
    input.parentNode.appendChild(errorElement);
}

/**
 * Clear an error message for an input field
 * @param {HTMLElement} input - The input element
 */
function clearError(input) {
    // Remove invalid class
    input.classList.remove('is-invalid');
    
    // Remove existing error message if present
    const errorElement = input.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.remove();
    }
}

/**
 * Initialize all form validation when the DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    validateProjectForm();
    validateUploadForm();
    validateFeedbackForm();
});
