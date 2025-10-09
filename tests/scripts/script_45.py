# Game Development and Physics Simulation
import pygame
import numpy as np
import random
import math
from dataclasses import dataclass
from typing import List, Tuple
import pymunk
from OpenGL.GL import *
import arcade

@dataclass
class Vector2D:
    """2D Vector for physics calculations"""
    x: float
    y: float
    
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return Vector2D(self.x / mag, self.y / mag)
        return Vector2D(0, 0)

class GameObject:
    """Base game object with physics"""
    def __init__(self, position: Vector2D, velocity: Vector2D, mass: float = 1.0):
        self.position = position
        self.velocity = velocity
        self.acceleration = Vector2D(0, 0)
        self.mass = mass
        self.forces = []
    
    def apply_force(self, force: Vector2D):
        """Apply force to object"""
        self.forces.append(force)
    
    def update(self, dt: float):
        """Update physics simulation"""
        # Calculate net force
        net_force = Vector2D(0, 0)
        for force in self.forces:
            net_force = net_force + force
        
        # F = ma, so a = F/m
        if self.mass > 0:
            self.acceleration = net_force * (1.0 / self.mass)
        
        # Update velocity and position
        self.velocity = self.velocity + self.acceleration * dt
        self.position = self.position + self.velocity * dt
        
        # Clear forces
        self.forces.clear()

def physics_simulation():
    """2D physics simulation with collision detection"""
    try:
        # Create physics world
        gravity = Vector2D(0, -9.81)
        objects = []
        
        # Create falling balls
        for i in range(10):
            pos = Vector2D(random.uniform(-5, 5), random.uniform(5, 10))
            vel = Vector2D(random.uniform(-2, 2), 0)
            ball = GameObject(pos, vel, mass=1.0)
            objects.append(ball)
        
        # Simulation parameters
        dt = 0.016  # 60 FPS
        simulation_time = 5.0  # 5 seconds
        steps = int(simulation_time / dt)
        
        collisions = 0
        
        # Run simulation
        for step in range(steps):
            for obj in objects:
                # Apply gravity
                obj.apply_force(gravity * obj.mass)
                
                # Ground collision
                if obj.position.y < 0:
                    obj.position.y = 0
                    obj.velocity.y *= -0.8  # Bounce with energy loss
                    collisions += 1
                
                # Wall collisions
                if obj.position.x < -10:
                    obj.position.x = -10
                    obj.velocity.x *= -0.8
                    collisions += 1
                elif obj.position.x > 10:
                    obj.position.x = 10
                    obj.velocity.x *= -0.8
                    collisions += 1
                
                # Air resistance
                drag_force = obj.velocity * -0.01 * obj.velocity.magnitude()
                obj.apply_force(drag_force)
                
                obj.update(dt)
        
        # Calculate final statistics
        total_kinetic_energy = sum(0.5 * obj.mass * obj.velocity.magnitude()**2 for obj in objects)
        avg_height = sum(obj.position.y for obj in objects) / len(objects)
        
        return {
            'objects_simulated': len(objects),
            'simulation_steps': steps,
            'total_collisions': collisions,
            'final_kinetic_energy': total_kinetic_energy,
            'average_final_height': avg_height,
            'simulation_time': simulation_time
        }
        
    except Exception as e:
        return {'error': str(e)}

def game_ai_simulation():
    """Game AI algorithms and behaviors"""
    try:
        # Simple game world
        world_size = (20, 20)
        
        # A* pathfinding algorithm
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        def get_neighbors(pos, world_size, obstacles):
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                new_pos = (pos[0] + dx, pos[1] + dy)
                if (0 <= new_pos[0] < world_size[0] and 
                    0 <= new_pos[1] < world_size[1] and 
                    new_pos not in obstacles):
                    neighbors.append(new_pos)
            return neighbors
        
        def a_star(start, goal, world_size, obstacles):
            open_set = [start]
            came_from = {}
            g_score = {start: 0}
            f_score = {start: heuristic(start, goal)}
            
            while open_set:
                current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
                
                if current == goal:
                    # Reconstruct path
                    path = []
                    while current in came_from:
                        path.append(current)
                        current = came_from[current]
                    path.append(start)
                    return list(reversed(path))
                
                open_set.remove(current)
                
                for neighbor in get_neighbors(current, world_size, obstacles):
                    tentative_g = g_score[current] + 1
                    
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                        if neighbor not in open_set:
                            open_set.append(neighbor)
            
            return []  # No path found
        
        # Create obstacles
        obstacles = set()
        for _ in range(50):
            obstacles.add((random.randint(0, world_size[0]-1), random.randint(0, world_size[1]-1)))
        
        # Find paths for multiple agents
        agents = [
            {'start': (1, 1), 'goal': (18, 18)},
            {'start': (0, 19), 'goal': (19, 0)},
            {'start': (10, 1), 'goal': (10, 18)},
            {'start': (1, 10), 'goal': (18, 10)}
        ]
        
        paths = []
        for agent in agents:
            path = a_star(agent['start'], agent['goal'], world_size, obstacles)
            paths.append(path)
        
        # Behavior trees simulation
        class BehaviorNode:
            def execute(self):
                pass
        
        class SequenceNode(BehaviorNode):
            def __init__(self, children):
                self.children = children
            
            def execute(self):
                for child in self.children:
                    if not child.execute():
                        return False
                return True
        
        class SelectorNode(BehaviorNode):
            def __init__(self, children):
                self.children = children
            
            def execute(self):
                for child in self.children:
                    if child.execute():
                        return True
                return False
        
        class ActionNode(BehaviorNode):
            def __init__(self, action_func):
                self.action_func = action_func
            
            def execute(self):
                return self.action_func()
        
        # Enemy AI behavior tree
        def check_player_in_range():
            return random.random() < 0.3  # 30% chance player is in range
        
        def attack_player():
            return random.random() < 0.8  # 80% attack success rate
        
        def patrol():
            return True  # Always successful
        
        # Build behavior tree
        attack_sequence = SequenceNode([
            ActionNode(check_player_in_range),
            ActionNode(attack_player)
        ])
        
        enemy_behavior = SelectorNode([
            attack_sequence,
            ActionNode(patrol)
        ])
        
        # Simulate AI decisions
        ai_decisions = []
        for _ in range(100):
            decision = enemy_behavior.execute()
            ai_decisions.append(decision)
        
        # Flocking simulation (boids)
        def simulate_flocking():
            class Boid:
                def __init__(self, x, y):
                    self.position = Vector2D(x, y)
                    self.velocity = Vector2D(random.uniform(-1, 1), random.uniform(-1, 1))
                    self.max_speed = 2.0
                
                def separation(self, boids, radius=1.5):
                    steering = Vector2D(0, 0)
                    count = 0
                    for boid in boids:
                        distance = (self.position - boid.position).magnitude()
                        if 0 < distance < radius:
                            diff = self.position - boid.position
                            diff = diff.normalize()
                            steering = steering + diff
                            count += 1
                    
                    if count > 0:
                        steering = steering * (1.0 / count)
                        if steering.magnitude() > 0:
                            steering = steering.normalize() * self.max_speed
                            steering = steering - self.velocity
                    
                    return steering
                
                def alignment(self, boids, radius=2.0):
                    average_velocity = Vector2D(0, 0)
                    count = 0
                    
                    for boid in boids:
                        distance = (self.position - boid.position).magnitude()
                        if 0 < distance < radius:
                            average_velocity = average_velocity + boid.velocity
                            count += 1
                    
                    if count > 0:
                        average_velocity = average_velocity * (1.0 / count)
                        if average_velocity.magnitude() > 0:
                            average_velocity = average_velocity.normalize() * self.max_speed
                            return average_velocity - self.velocity
                    
                    return Vector2D(0, 0)
                
                def cohesion(self, boids, radius=2.0):
                    center_of_mass = Vector2D(0, 0)
                    count = 0
                    
                    for boid in boids:
                        distance = (self.position - boid.position).magnitude()
                        if 0 < distance < radius:
                            center_of_mass = center_of_mass + boid.position
                            count += 1
                    
                    if count > 0:
                        center_of_mass = center_of_mass * (1.0 / count)
                        desired = center_of_mass - self.position
                        if desired.magnitude() > 0:
                            desired = desired.normalize() * self.max_speed
                            return desired - self.velocity
                    
                    return Vector2D(0, 0)
            
            # Create flock
            boids = [Boid(random.uniform(-10, 10), random.uniform(-10, 10)) for _ in range(50)]
            
            # Simulate flocking behavior
            for _ in range(100):  # 100 simulation steps
                for boid in boids:
                    separation = boid.separation(boids)
                    alignment = boid.alignment(boids)
                    cohesion = boid.cohesion(boids)
                    
                    # Apply forces
                    acceleration = separation * 1.5 + alignment * 1.0 + cohesion * 1.0
                    boid.velocity = boid.velocity + acceleration * 0.02
                    
                    # Limit speed
                    if boid.velocity.magnitude() > boid.max_speed:
                        boid.velocity = boid.velocity.normalize() * boid.max_speed
                    
                    boid.position = boid.position + boid.velocity * 0.02
            
            return boids
        
        flock = simulate_flocking()
        
        return {
            'pathfinding_agents': len(agents),
            'successful_paths': len([p for p in paths if p]),
            'obstacles': len(obstacles),
            'average_path_length': sum(len(p) for p in paths if p) / len([p for p in paths if p]) if [p for p in paths if p] else 0,
            'ai_behavior_decisions': len(ai_decisions),
            'ai_success_rate': sum(ai_decisions) / len(ai_decisions),
            'flock_size': len(flock),
            'behavior_tree_nodes': 3,
            'algorithms_implemented': ['A*', 'Behavior Trees', 'Flocking']
        }
        
    except Exception as e:
        return {'error': str(e)}

def procedural_generation():
    """Procedural content generation for games"""
    try:
        # Perlin noise-like function (simplified)
        def noise_2d(x, y, scale=10.0):
            # Simple pseudo-random noise
            return math.sin(x * scale) * math.cos(y * scale) + 0.5 * math.sin(x * scale * 2) * math.cos(y * scale * 2)
        
        # Generate terrain heightmap
        terrain_size = 50
        heightmap = []
        
        for y in range(terrain_size):
            row = []
            for x in range(terrain_size):
                height = (
                    noise_2d(x / 10.0, y / 10.0) * 0.5 +  # Large features
                    noise_2d(x / 5.0, y / 5.0) * 0.3 +    # Medium features
                    noise_2d(x / 2.0, y / 2.0) * 0.2      # Small details
                )
                height = max(0, min(1, height))  # Clamp to [0, 1]
                row.append(height)
            heightmap.append(row)
        
        # Generate dungeon layout
        def generate_dungeon(width=30, height=30):
            # Initialize with walls
            dungeon = [['#' for _ in range(width)] for _ in range(height)]
            
            # Create rooms
            rooms = []
            for _ in range(8):  # Try to place 8 rooms
                room_w = random.randint(3, 8)
                room_h = random.randint(3, 8)
                room_x = random.randint(1, width - room_w - 1)
                room_y = random.randint(1, height - room_h - 1)
                
                # Check if room overlaps with existing rooms
                overlap = False
                for existing_room in rooms:
                    if (room_x < existing_room[0] + existing_room[2] and
                        room_x + room_w > existing_room[0] and
                        room_y < existing_room[1] + existing_room[3] and
                        room_y + room_h > existing_room[1]):
                        overlap = True
                        break
                
                if not overlap:
                    rooms.append((room_x, room_y, room_w, room_h))
                    
                    # Carve out the room
                    for y in range(room_y, room_y + room_h):
                        for x in range(room_x, room_x + room_w):
                            dungeon[y][x] = '.'
            
            # Connect rooms with corridors
            for i in range(len(rooms) - 1):
                room1 = rooms[i]
                room2 = rooms[i + 1]
                
                # Find centers
                center1 = (room1[0] + room1[2] // 2, room1[1] + room1[3] // 2)
                center2 = (room2[0] + room2[2] // 2, room2[1] + room2[3] // 2)
                
                # Create L-shaped corridor
                x1, y1 = center1
                x2, y2 = center2
                
                # Horizontal corridor
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    if 0 <= y1 < height and 0 <= x < width:
                        dungeon[y1][x] = '.'
                
                # Vertical corridor
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    if 0 <= y < height and 0 <= x2 < width:
                        dungeon[y][x2] = '.'
            
            return dungeon, rooms
        
        dungeon, rooms = generate_dungeon()
        
        # Generate maze using recursive backtracking
        def generate_maze(width=25, height=25):
            # Initialize maze (odd dimensions for proper maze structure)
            maze = [['#' for _ in range(width)] for _ in range(height)]
            
            # Starting position
            start_x, start_y = 1, 1
            maze[start_y][start_x] = '.'
            
            # Stack for backtracking
            stack = [(start_x, start_y)]
            
            def get_unvisited_neighbors(x, y):
                neighbors = []
                directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # Up, Right, Down, Left
                
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 1 <= nx < width - 1 and 1 <= ny < height - 1:
                        if maze[ny][nx] == '#':
                            neighbors.append((nx, ny, x + dx // 2, y + dy // 2))
                
                return neighbors
            
            while stack:
                current_x, current_y = stack[-1]
                neighbors = get_unvisited_neighbors(current_x, current_y)
                
                if neighbors:
                    # Choose random neighbor
                    next_x, next_y, wall_x, wall_y = random.choice(neighbors)
                    
                    # Remove wall and mark as visited
                    maze[wall_y][wall_x] = '.'
                    maze[next_y][next_x] = '.'
                    
                    stack.append((next_x, next_y))
                else:
                    # Backtrack
                    stack.pop()
            
            return maze
        
        maze = generate_maze()
        
        # Generate random items/enemies placement
        def place_entities(game_map, entity_type='item', count=10):
            entities = []
            attempts = 0
            max_attempts = count * 10
            
            while len(entities) < count and attempts < max_attempts:
                x = random.randint(0, len(game_map[0]) - 1)
                y = random.randint(0, len(game_map) - 1)
                
                if game_map[y][x] == '.':
                    entities.append({'type': entity_type, 'x': x, 'y': y})
                
                attempts += 1
            
            return entities
        
        dungeon_items = place_entities(dungeon, 'item', 15)
        dungeon_enemies = place_entities(dungeon, 'enemy', 8)
        maze_items = place_entities(maze, 'treasure', 5)
        
        # Calculate statistics
        terrain_avg_height = sum(sum(row) for row in heightmap) / (terrain_size * terrain_size)
        dungeon_floor_tiles = sum(row.count('.') for row in dungeon)
        maze_floor_tiles = sum(row.count('.') for row in maze)
        
        return {
            'terrain_size': terrain_size,
            'terrain_average_height': terrain_avg_height,
            'dungeon_rooms': len(rooms),
            'dungeon_floor_tiles': dungeon_floor_tiles,
            'dungeon_items_placed': len(dungeon_items),
            'dungeon_enemies_placed': len(dungeon_enemies),
            'maze_floor_tiles': maze_floor_tiles,
            'maze_treasures_placed': len(maze_items),
            'generation_algorithms': ['Terrain', 'BSP Dungeon', 'Recursive Maze'],
            'total_generated_content': terrain_size**2 + len(dungeon)**2 + len(maze)**2
        }
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    print("Game development and physics simulation...")
    
    # Physics simulation
    physics_result = physics_simulation()
    if 'error' not in physics_result:
        print(f"Physics: {physics_result['objects_simulated']} objects, {physics_result['total_collisions']} collisions")
    
    # Game AI
    ai_result = game_ai_simulation()
    if 'error' not in ai_result:
        print(f"Game AI: {ai_result['successful_paths']}/{ai_result['pathfinding_agents']} paths found, {ai_result['ai_success_rate']:.1%} AI success")
    
    # Procedural generation
    procgen_result = procedural_generation()
    if 'error' not in procgen_result:
        print(f"Proc Gen: {len(procgen_result['generation_algorithms'])} algorithms, {procgen_result['dungeon_rooms']} rooms, {procgen_result['total_generated_content']} tiles")