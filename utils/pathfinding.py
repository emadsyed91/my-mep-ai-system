"""
Pathfinding Module

This module implements pathfinding algorithms to route MEP components through the building.
"""

import math
import heapq
import logging

# Configure logger
logger = logging.getLogger(__name__)

class Point:
    """Class representing a 2D point"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def distance(self, other):
        """Calculate Euclidean distance to another point"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def manhattan_distance(self, other):
        """Calculate Manhattan distance to another point"""
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def to_list(self):
        """Convert to list format"""
        return [self.x, self.y]

def find_path(start, end, spatial_data, algorithm='a_star'):
    """
    Find a path between two points using the specified algorithm
    
    Args:
        start: List [x, y] or Point representing start position
        end: List [x, y] or Point representing end position
        spatial_data: Dictionary containing spatial data for collision detection
        algorithm: String specifying the algorithm to use ('a_star' or 'dijkstra')
        
    Returns:
        list: List of [x, y] coordinates representing the path
    """
    # Convert list coordinates to Point objects if needed
    if isinstance(start, list):
        start = Point(start[0], start[1])
    if isinstance(end, list):
        end = Point(end[0], end[1])
    
    # Choose algorithm
    if algorithm == 'a_star':
        path = a_star(start, end, spatial_data)
    elif algorithm == 'dijkstra':
        path = dijkstra(start, end, spatial_data)
    else:
        raise ValueError(f"Unknown pathfinding algorithm: {algorithm}")
    
    # Convert Path objects back to list format
    if path:
        return [point.to_list() for point in path]
    else:
        # If no path found, return a simple direct path
        return [start.to_list(), end.to_list()]

def a_star(start, end, spatial_data):
    """
    A* pathfinding algorithm
    
    Args:
        start: Point representing start position
        end: Point representing end position
        spatial_data: Dictionary containing spatial data for collision detection
        
    Returns:
        list: List of Point objects representing the path
    """
    # Create grid for pathfinding
    grid = create_grid(spatial_data)
    
    # Priority queue for A*
    open_set = []
    heapq.heappush(open_set, (0, start))
    
    # Cost from start to each node
    g_score = {start: 0}
    
    # Estimated total cost from start to end through node
    f_score = {start: start.manhattan_distance(end)}
    
    # For reconstructing the path
    came_from = {}
    
    while open_set:
        # Get node with lowest f_score
        _, current = heapq.heappop(open_set)
        
        # If we've reached the end
        if current.manhattan_distance(end) < 1.0:
            return reconstruct_path(came_from, current)
        
        # Generate neighbors
        neighbors = get_neighbors(current, grid, spatial_data)
        
        for neighbor in neighbors:
            # Tentative g_score
            tentative_g_score = g_score.get(current, float('inf')) + current.distance(neighbor)
            
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                # This path is better
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + neighbor.manhattan_distance(end)
                
                # Add to open set if not already present
                if neighbor not in [item[1] for item in open_set]:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    # No path found
    logger.warning(f"No path found from {start.to_list()} to {end.to_list()}")
    return []

def dijkstra(start, end, spatial_data):
    """
    Dijkstra's pathfinding algorithm
    
    Args:
        start: Point representing start position
        end: Point representing end position
        spatial_data: Dictionary containing spatial data for collision detection
        
    Returns:
        list: List of Point objects representing the path
    """
    # Create grid for pathfinding
    grid = create_grid(spatial_data)
    
    # Priority queue for Dijkstra
    open_set = []
    heapq.heappush(open_set, (0, start))
    
    # Cost from start to each node
    dist = {start: 0}
    
    # For reconstructing the path
    came_from = {}
    
    while open_set:
        # Get node with lowest distance
        _, current = heapq.heappop(open_set)
        
        # If we've reached the end
        if current.manhattan_distance(end) < 1.0:
            return reconstruct_path(came_from, current)
        
        # Generate neighbors
        neighbors = get_neighbors(current, grid, spatial_data)
        
        for neighbor in neighbors:
            # Tentative distance
            tentative_dist = dist.get(current, float('inf')) + current.distance(neighbor)
            
            if tentative_dist < dist.get(neighbor, float('inf')):
                # This path is better
                came_from[neighbor] = current
                dist[neighbor] = tentative_dist
                
                # Add to open set if not already present
                if neighbor not in [item[1] for item in open_set]:
                    heapq.heappush(open_set, (dist[neighbor], neighbor))
    
    # No path found
    logger.warning(f"No path found from {start.to_list()} to {end.to_list()}")
    return []

def create_grid(spatial_data):
    """
    Create a grid representation of the spatial data
    
    Args:
        spatial_data: Dictionary containing spatial data
        
    Returns:
        dict: Dictionary representing walkable grid cells
    """
    # This is a simplified implementation
    # In a real system, we would create a detailed grid representation
    # of the building with proper collision detection
    
    grid = {}
    
    # Process walls
    walls = spatial_data.get('walls', [])
    for wall in walls:
        if 'start' in wall and 'end' in wall:
            # Mark wall as not walkable
            start = Point(wall['start'][0], wall['start'][1])
            end = Point(wall['end'][0], wall['end'][1])
            
            # Create a simple line of blocked cells
            dx = end.x - start.x
            dy = end.y - start.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                steps = int(distance * 2)  # 2 points per unit
                for i in range(steps + 1):
                    t = i / steps
                    x = start.x + t * dx
                    y = start.y + t * dy
                    
                    # Block a 0.5 unit radius around the wall
                    for ox in range(-1, 2):
                        for oy in range(-1, 2):
                            grid_x = round(x + ox * 0.5)
                            grid_y = round(y + oy * 0.5)
                            grid[(grid_x, grid_y)] = False  # Not walkable
    
    return grid

def get_neighbors(point, grid, spatial_data):
    """
    Get neighboring points for pathfinding
    
    Args:
        point: Point to find neighbors for
        grid: Grid representation of the building
        spatial_data: Dictionary containing spatial data
        
    Returns:
        list: List of neighboring Point objects
    """
    neighbors = []
    
    # Cardinal directions (up, right, down, left)
    directions = [
        (0, 1), (1, 0), (0, -1), (-1, 0),
        # Diagonals
        (1, 1), (1, -1), (-1, -1), (-1, 1)
    ]
    
    for dx, dy in directions:
        nx = round(point.x + dx)
        ny = round(point.y + dy)
        
        # Skip if cell is blocked
        if grid.get((nx, ny), True) is False:
            continue
        
        # Add neighbor
        neighbors.append(Point(nx, ny))
    
    return neighbors

def reconstruct_path(came_from, current):
    """
    Reconstruct path from came_from dictionary
    
    Args:
        came_from: Dictionary mapping points to their predecessor
        current: End point of the path
        
    Returns:
        list: List of Point objects representing the path
    """
    path = [current]
    
    while current in came_from:
        current = came_from[current]
        path.append(current)
    
    # Reverse to get path from start to end
    path.reverse()
    
    # Optimize the path by removing unnecessary waypoints
    optimized_path = optimize_routing(path)
    
    return optimized_path

def optimize_routing(path):
    """
    Optimize routing by removing unnecessary waypoints
    
    Args:
        path: List of Point objects representing the path
        
    Returns:
        list: Optimized list of Point objects
    """
    if len(path) <= 2:
        return path
    
    optimized = [path[0]]
    last_direction = None
    
    for i in range(1, len(path) - 1):
        # Calculate direction from previous point
        prev_direction = (
            path[i].x - path[i-1].x,
            path[i].y - path[i-1].y
        )
        
        # Calculate direction to next point
        next_direction = (
            path[i+1].x - path[i].x,
            path[i+1].y - path[i].y
        )
        
        # If the direction changes, keep this waypoint
        if prev_direction != next_direction:
            optimized.append(path[i])
        
        last_direction = next_direction
    
    # Always include the last point
    optimized.append(path[-1])
    
    return optimized

def optimize_routing(mep_design, spatial_data):
    """
    Optimize the MEP routing for the generated design
    
    Args:
        mep_design: Dictionary containing the MEP design data
        spatial_data: Dictionary containing spatial data
        
    Returns:
        dict: Optimized MEP design
    """
    logger.info("Optimizing MEP routing")
    
    # Clone the design to avoid modifying the original
    optimized_design = {
        'mechanical': mep_design.get('mechanical', {}),
        'electrical': mep_design.get('electrical', {}),
        'plumbing': mep_design.get('plumbing', {})
    }
    
    # Optimize mechanical ducts
    if 'ducts' in optimized_design['mechanical']:
        optimized_ducts = []
        
        for duct in optimized_design['mechanical']['ducts']:
            if 'path' in duct:
                # Convert path to Point objects
                path = [Point(p[0], p[1]) for p in duct['path']]
                
                # Optimize path
                optimized_path = optimize_duct_path(path, spatial_data)
                
                # Update duct with optimized path
                duct['path'] = [p.to_list() for p in optimized_path]
            
            optimized_ducts.append(duct)
        
        optimized_design['mechanical']['ducts'] = optimized_ducts
    
    # Optimize electrical conduits
    if 'conduits' in optimized_design['electrical']:
        optimized_conduits = []
        
        for conduit in optimized_design['electrical']['conduits']:
            if 'path' in conduit:
                # Convert path to Point objects
                path = [Point(p[0], p[1]) for p in conduit['path']]
                
                # Optimize path
                optimized_path = optimize_conduit_path(path, spatial_data)
                
                # Update conduit with optimized path
                conduit['path'] = [p.to_list() for p in optimized_path]
            
            optimized_conduits.append(conduit)
        
        optimized_design['electrical']['conduits'] = optimized_conduits
    
    # Optimize plumbing pipes
    if 'pipes' in optimized_design['plumbing']:
        optimized_pipes = []
        
        for pipe in optimized_design['plumbing']['pipes']:
            if 'path' in pipe:
                # Convert path to Point objects
                path = [Point(p[0], p[1]) for p in pipe['path']]
                
                # Optimize path
                optimized_path = optimize_pipe_path(path, spatial_data)
                
                # Update pipe with optimized path
                pipe['path'] = [p.to_list() for p in optimized_path]
            
            optimized_pipes.append(pipe)
        
        optimized_design['plumbing']['pipes'] = optimized_pipes
    
    return optimized_design

def optimize_duct_path(path, spatial_data):
    """
    Optimize a duct path to follow orthogonal routing
    
    Args:
        path: List of Point objects representing the path
        spatial_data: Dictionary containing spatial data
        
    Returns:
        list: Optimized list of Point objects
    """
    # For ducts, we want to simplify the path and make it more orthogonal
    # This helps with fabrication and installation
    
    if len(path) <= 2:
        return path
    
    # Start with beginning and end points
    optimized = [path[0]]
    
    # Generate orthogonal path using Manhattan routing
    current = path[0]
    end = path[-1]
    
    # First move horizontally, then vertically
    if abs(end.x - current.x) > 0.1:
        middle_x = Point(end.x, current.y)
        optimized.append(middle_x)
    
    # Add end point
    optimized.append(end)
    
    return optimized

def optimize_conduit_path(path, spatial_data):
    """
    Optimize an electrical conduit path
    
    Args:
        path: List of Point objects representing the path
        spatial_data: Dictionary containing spatial data
        
    Returns:
        list: Optimized list of Point objects
    """
    # For electrical conduits, we prefer orthogonal routing with minimal bends
    
    if len(path) <= 2:
        return path
    
    # Start with beginning and end points
    optimized = [path[0]]
    
    # Generate orthogonal path using Manhattan routing
    current = path[0]
    end = path[-1]
    
    # First move horizontally, then vertically
    if abs(end.x - current.x) > 0.1:
        middle_x = Point(end.x, current.y)
        optimized.append(middle_x)
    
    # Add end point
    optimized.append(end)
    
    return optimized

def optimize_pipe_path(path, spatial_data):
    """
    Optimize a plumbing pipe path
    
    Args:
        path: List of Point objects representing the path
        spatial_data: Dictionary containing spatial data
        
    Returns:
        list: Optimized list of Point objects
    """
    # For plumbing pipes, we need to ensure proper slopes for drainage
    
    if len(path) <= 2:
        return path
    
    # Start with beginning and end points
    optimized = [path[0]]
    
    # Generate path with proper slope
    start = path[0]
    end = path[-1]
    
    # For drain pipes, make sure they slope downward
    is_drain = any(p in ['drain_pipe', 'waste_pipe', 'vent_pipe'] for p in path[0].to_list())
    
    if is_drain:
        # Ensure end is lower than start for drainage
        # Add midpoint if needed
        if start.y < end.y:  # End is higher than start, which is bad for drainage
            # Move horizontally first
            if abs(end.x - start.x) > 0.1:
                mid_x = Point(end.x, start.y)
                optimized.append(mid_x)
        else:
            # End is lower, good for drainage
            # Move horizontally, then down
            if abs(end.x - start.x) > 0.1:
                mid_x = Point(end.x, start.y)
                optimized.append(mid_x)
    else:
        # For water supply, we prefer orthogonal routing
        if abs(end.x - start.x) > 0.1:
            mid_x = Point(end.x, start.y)
            optimized.append(mid_x)
    
    # Add end point
    optimized.append(end)
    
    return optimized
