// Global variable to store the current renderer, scene, camera and controls
let currentViewer = null;

/**
 * Initialize a 3D visualization of the entire MEP design
 * @param {number} projectId - The project ID
 * @param {string} canvasId - The ID of the canvas element to render to
 */
function initializeOverviewVisualization(projectId, canvasId) {
    // If we already have a viewer, dispose it to prevent memory leaks
    if (currentViewer) {
        disposeViewer(currentViewer);
    }
    
    // Create a new scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a); // Dark background
    
    // Create camera
    const container = document.getElementById(canvasId);
    const camera = new THREE.PerspectiveCamera(
        70, // Field of view
        container.clientWidth / container.clientHeight, // Aspect ratio
        0.1, // Near clipping plane
        1000 // Far clipping plane
    );
    camera.position.set(10, 10, 10);
    camera.lookAt(0, 0, 0);
    
    // Create renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    
    // Clear the container
    container.innerHTML = '';
    container.appendChild(renderer.domElement);
    
    // Add orbit controls
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    
    // Add grid and coordinate axes
    addGridAndAxes(scene);
    
    // Load MEP design data
    fetch(`/api/design/${projectId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Add all systems to the scene
            if (data.mechanical) {
                addMechanicalSystem(scene, data.mechanical);
            }
            if (data.electrical) {
                addElectricalSystem(scene, data.electrical);
            }
            if (data.plumbing) {
                addPlumbingSystem(scene, data.plumbing);
            }
            
            // Find the center and size of the model to adjust camera
            const boundingBox = new THREE.Box3().setFromObject(scene);
            const center = boundingBox.getCenter(new THREE.Vector3());
            const size = boundingBox.getSize(new THREE.Vector3());
            
            // Position camera to see all objects
            const maxDim = Math.max(size.x, size.y, size.z);
            camera.position.copy(center);
            camera.position.z += maxDim * 2;
            camera.lookAt(center);
            
            // Center controls on the model
            controls.target.copy(center);
            controls.update();
        })
        .catch(error => {
            console.error('Error loading design data:', error);
            displayLoadingError(container);
        });
    
    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    function onWindowResize() {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    }
    
    // Store current viewer for cleanup
    currentViewer = {
        scene: scene,
        camera: camera,
        renderer: renderer,
        controls: controls,
        canvasId: canvasId
    };
    
    return currentViewer;
}

/**
 * Initialize a 3D visualization of a specific MEP system
 * @param {number} projectId - The project ID
 * @param {string} systemType - The system type ('mechanical', 'electrical', or 'plumbing')
 * @param {string} canvasId - The ID of the canvas element to render to
 */
function initializeSystemVisualization(projectId, systemType, canvasId) {
    // If we already have a viewer, dispose it to prevent memory leaks
    if (currentViewer && currentViewer.canvasId === canvasId) {
        disposeViewer(currentViewer);
    }
    
    // Create a new scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a); // Dark background
    
    // Create camera
    const container = document.getElementById(canvasId);
    const camera = new THREE.PerspectiveCamera(
        70, // Field of view
        container.clientWidth / container.clientHeight, // Aspect ratio
        0.1, // Near clipping plane
        1000 // Far clipping plane
    );
    camera.position.set(10, 10, 10);
    camera.lookAt(0, 0, 0);
    
    // Create renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    
    // Clear the container
    container.innerHTML = '';
    container.appendChild(renderer.domElement);
    
    // Add orbit controls
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    
    // Add grid and coordinate axes
    addGridAndAxes(scene);
    
    // Load MEP design data
    fetch(`/api/design/${projectId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Add only the requested system to the scene
            if (systemType === 'mechanical' && data.mechanical) {
                addMechanicalSystem(scene, data.mechanical);
            } else if (systemType === 'electrical' && data.electrical) {
                addElectricalSystem(scene, data.electrical);
            } else if (systemType === 'plumbing' && data.plumbing) {
                addPlumbingSystem(scene, data.plumbing);
            }
            
            // Find the center and size of the model to adjust camera
            const boundingBox = new THREE.Box3().setFromObject(scene);
            const center = boundingBox.getCenter(new THREE.Vector3());
            const size = boundingBox.getSize(new THREE.Vector3());
            
            // Position camera to see all objects
            const maxDim = Math.max(size.x, size.y, size.z);
            camera.position.copy(center);
            camera.position.z += maxDim * 2;
            camera.lookAt(center);
            
            // Center controls on the model
            controls.target.copy(center);
            controls.update();
        })
        .catch(error => {
            console.error('Error loading design data:', error);
            displayLoadingError(container);
        });
    
    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    function onWindowResize() {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    }
    
    // Store current viewer for cleanup
    currentViewer = {
        scene: scene,
        camera: camera,
        renderer: renderer,
        controls: controls,
        canvasId: canvasId
    };
    
    return currentViewer;
}

/**
 * Add grid and coordinate axes to the scene
 * @param {THREE.Scene} scene - The scene to add to
 */
function addGridAndAxes(scene) {
    // Add a grid
    const gridHelper = new THREE.GridHelper(20, 20, 0x888888, 0x444444);
    scene.add(gridHelper);
    
    // Add axes
    const axesHelper = new THREE.AxesHelper(5);
    scene.add(axesHelper);
}

/**
 * Add mechanical system components to the scene
 * @param {THREE.Scene} scene - The scene to add to
 * @param {Object} mechanicalData - The mechanical system data
 */
function addMechanicalSystem(scene, mechanicalData) {
    // Add air handlers
    if (mechanicalData.air_handlers) {
        mechanicalData.air_handlers.forEach(ahu => {
            const position = new THREE.Vector3(ahu.position[0], ahu.position[1], 0);
            const geometry = new THREE.BoxGeometry(2, 2, 1);
            const material = new THREE.MeshBasicMaterial({ color: 0xff4444 }); // Red
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.copy(position);
            scene.add(mesh);
            
            // Add label
            addLabel(scene, position, ahu.id);
        });
    }
    
    // Add diffusers
    if (mechanicalData.diffusers) {
        mechanicalData.diffusers.forEach(diffuser => {
            const position = new THREE.Vector3(diffuser.position[0], diffuser.position[1], 0);
            const geometry = new THREE.CylinderGeometry(0.3, 0.3, 0.1, 32);
            const material = new THREE.MeshBasicMaterial({ color: 0xff8888 }); // Light red
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.copy(position);
            scene.add(mesh);
        });
    }
    
    // Add ducts
    if (mechanicalData.ducts) {
        mechanicalData.ducts.forEach(duct => {
            if (duct.path && duct.path.length >= 2) {
                const points = duct.path.map(p => new THREE.Vector3(p[0], p[1], 0));
                const curve = new THREE.CatmullRomCurve3(points);
                const geometry = new THREE.TubeGeometry(curve, points.length * 10, 0.2, 8, false);
                const material = new THREE.MeshBasicMaterial({ color: 0xff6666 }); // Medium red
                const mesh = new THREE.Mesh(geometry, material);
                scene.add(mesh);
            }
        });
    }
}

/**
 * Add electrical system components to the scene
 * @param {THREE.Scene} scene - The scene to add to
 * @param {Object} electricalData - The electrical system data
 */
function addElectricalSystem(scene, electricalData) {
    // Add panels
    if (electricalData.panels) {
        electricalData.panels.forEach(panel => {
            const position = new THREE.Vector3(panel.position[0], panel.position[1], 0);
            const geometry = new THREE.BoxGeometry(1, 1.5, 0.5);
            const material = new THREE.MeshBasicMaterial({ color: 0x4444ff }); // Blue
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.copy(position);
            scene.add(mesh);
            
            // Add label
            addLabel(scene, position, panel.id);
        });
    }
    
    // Add outlets
    if (electricalData.outlets) {
        electricalData.outlets.forEach(outlet => {
            const position = new THREE.Vector3(outlet.position[0], outlet.position[1], 0);
            const geometry = new THREE.BoxGeometry(0.3, 0.3, 0.1);
            const material = new THREE.MeshBasicMaterial({ color: 0x8888ff }); // Light blue
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.copy(position);
            scene.add(mesh);
        });
    }
    
    // Add lights
    if (electricalData.lights) {
        electricalData.lights.forEach(light => {
            const position = new THREE.Vector3(light.position[0], light.position[1], 0);
            const geometry = new THREE.SphereGeometry(0.2, 16, 16);
            const material = new THREE.MeshBasicMaterial({ color: 0xffffaa }); // Yellow
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.copy(position);
            scene.add(mesh);
            
            // Add a point light to simulate light
            const pointLight = new THREE.PointLight(0xffffaa, 0.5, 3);
            pointLight.position.copy(position);
            scene.add(pointLight);
        });
    }
    
    // Add conduits
    if (electricalData.conduits) {
        electricalData.conduits.forEach(conduit => {
            if (conduit.path && conduit.path.length >= 2) {
                const points = conduit.path.map(p => new THREE.Vector3(p[0], p[1], 0));
                const curve = new THREE.CatmullRomCurve3(points);
                const geometry = new THREE.TubeGeometry(curve, points.length * 10, 0.1, 8, false);
                const material = new THREE.MeshBasicMaterial({ color: 0x6666ff }); // Medium blue
                const mesh = new THREE.Mesh(geometry, material);
                scene.add(mesh);
            }
        });
    }
}

/**
 * Add plumbing system components to the scene
 * @param {THREE.Scene} scene - The scene to add to
 * @param {Object} plumbingData - The plumbing system data
 */
function addPlumbingSystem(scene, plumbingData) {
    // Add fixtures
    if (plumbingData.fixtures) {
        plumbingData.fixtures.forEach(fixture => {
            const position = new THREE.Vector3(fixture.position[0], fixture.position[1], 0);
            
            let geometry, material;
            
            if (fixture.type === 'toilet' || fixture.type === 'water_closet') {
                geometry = new THREE.CylinderGeometry(0.4, 0.3, 0.4, 16);
                material = new THREE.MeshBasicMaterial({ color: 0xffffff }); // White
            } else if (fixture.type === 'sink' || fixture.type === 'lavatory') {
                geometry = new THREE.BoxGeometry(0.6, 0.4, 0.2);
                material = new THREE.MeshBasicMaterial({ color: 0xffffff }); // White
            } else if (fixture.type === 'water_source' || fixture.type === 'water_main') {
                geometry = new THREE.SphereGeometry(0.3, 16, 16);
                material = new THREE.MeshBasicMaterial({ color: 0x44ff44 }); // Green
            } else if (fixture.type === 'drain' || fixture.type === 'drain_main') {
                geometry = new THREE.CylinderGeometry(0.3, 0.3, 0.2, 16);
                material = new THREE.MeshBasicMaterial({ color: 0x666666 }); // Gray
            } else {
                geometry = new THREE.BoxGeometry(0.4, 0.4, 0.2);
                material = new THREE.MeshBasicMaterial({ color: 0x44ff44 }); // Green
            }
            
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.copy(position);
            scene.add(mesh);
            
            // Add label for main fixtures
            if (fixture.type === 'water_source' || fixture.type === 'drain_main') {
                addLabel(scene, position, fixture.id);
            }
        });
    }
    
    // Add pipes
    if (plumbingData.pipes) {
        plumbingData.pipes.forEach(pipe => {
            if (pipe.path && pipe.path.length >= 2) {
                const points = pipe.path.map(p => new THREE.Vector3(p[0], p[1], 0));
                const curve = new THREE.CatmullRomCurve3(points);
                
                // Different colors for different pipe types
                let color;
                if (pipe.type === 'water_pipe' || pipe.type === 'supply_pipe') {
                    color = 0x44aaff; // Light blue for water supply
                } else {
                    color = 0x886644; // Brown for drainage
                }
                
                const geometry = new THREE.TubeGeometry(curve, points.length * 10, pipe.diameter ? pipe.diameter / 10 : 0.1, 8, false);
                const material = new THREE.MeshBasicMaterial({ color: color });
                const mesh = new THREE.Mesh(geometry, material);
                scene.add(mesh);
            }
        });
    }
}

/**
 * Add a text label to the scene
 * @param {THREE.Scene} scene - The scene to add to
 * @param {THREE.Vector3} position - The position to place the label
 * @param {string} text - The text to display
 */
function addLabel(scene, position, text) {
    // Create a canvas for the label
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 64;
    
    // Draw text on canvas
    context.fillStyle = '#ffffff';
    context.font = 'Bold 24px Arial';
    context.fillText(text, 10, 40);
    
    // Create texture from canvas
    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;
    
    // Create sprite material with the texture
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(spriteMaterial);
    
    // Position the sprite
    sprite.position.set(position.x, position.y + 1, position.z);
    sprite.scale.set(2, 0.5, 1);
    
    // Add to scene
    scene.add(sprite);
}

/**
 * Display an error message when loading fails
 * @param {HTMLElement} container - The container element
 */
function displayLoadingError(container) {
    container.innerHTML = '';
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger m-3';
    errorDiv.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i>Error loading design data. Please try again later.';
    container.appendChild(errorDiv);
}

/**
 * Clean up a viewer to prevent memory leaks
 * @param {Object} viewer - The viewer object to dispose
 */
function disposeViewer(viewer) {
    if (!viewer) return;
    
    // Dispose of renderer
    if (viewer.renderer) {
        viewer.renderer.dispose();
    }
    
    // Remove all objects from scene
    if (viewer.scene) {
        while (viewer.scene.children.length > 0) {
            const obj = viewer.scene.children[0];
            viewer.scene.remove(obj);
        }
    }
    
    // Remove event listeners
    window.removeEventListener('resize', onWindowResize);
}

/**
 * Zoom in the current view
 */
function zoomIn() {
    if (currentViewer && currentViewer.camera) {
        currentViewer.camera.position.multiplyScalar(0.9);
        currentViewer.controls.update();
    }
}

/**
 * Zoom out the current view
 */
function zoomOut() {
    if (currentViewer && currentViewer.camera) {
        currentViewer.camera.position.multiplyScalar(1.1);
        currentViewer.controls.update();
    }
}

/**
 * Reset the view to the default position
 */
function resetView() {
    if (currentViewer) {
        // Find the center of the scene
        const boundingBox = new THREE.Box3().setFromObject(currentViewer.scene);
        const center = boundingBox.getCenter(new THREE.Vector3());
        const size = boundingBox.getSize(new THREE.Vector3());
        
        // Position camera to see all objects
        const maxDim = Math.max(size.x, size.y, size.z);
        currentViewer.camera.position.copy(center);
        currentViewer.camera.position.z += maxDim * 2;
        currentViewer.camera.lookAt(center);
        
        // Center controls on the model
        currentViewer.controls.target.copy(center);
        currentViewer.controls.update();
    }
}
