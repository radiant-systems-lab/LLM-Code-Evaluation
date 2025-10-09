# Robotics and Control Systems
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from scipy.optimize import minimize
from scipy.integrate import odeint
import control
import sympy as sp
from sympy import symbols, Matrix, simplify

def robotic_kinematics():
    """Forward and inverse kinematics for robotic arms"""
    # Define a 3-DOF robotic arm
    class RoboticArm3DOF:
        def __init__(self, link_lengths):
            self.L1, self.L2, self.L3 = link_lengths
        
        def forward_kinematics(self, joint_angles):
            """Calculate end-effector position from joint angles"""
            theta1, theta2, theta3 = joint_angles
            
            # Transformation matrices
            T01 = np.array([
                [np.cos(theta1), -np.sin(theta1), 0, 0],
                [np.sin(theta1), np.cos(theta1), 0, 0],
                [0, 0, 1, self.L1],
                [0, 0, 0, 1]
            ])
            
            T12 = np.array([
                [np.cos(theta2), -np.sin(theta2), 0, self.L2 * np.cos(theta2)],
                [np.sin(theta2), np.cos(theta2), 0, self.L2 * np.sin(theta2)],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ])
            
            T23 = np.array([
                [np.cos(theta3), -np.sin(theta3), 0, self.L3 * np.cos(theta3)],
                [np.sin(theta3), np.cos(theta3), 0, self.L3 * np.sin(theta3)],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ])
            
            # Calculate end-effector transformation
            T03 = T01 @ T12 @ T23
            
            # Extract position
            position = T03[:3, 3]
            
            # Extract rotation matrix
            rotation = T03[:3, :3]
            
            return position, rotation
        
        def inverse_kinematics(self, target_position):
            """Calculate joint angles for target end-effector position"""
            x, y, z = target_position
            
            # Analytical solution for 3-DOF arm (simplified)
            # This is a simplified version - real IK can be much more complex
            
            # Calculate base rotation
            theta1 = np.arctan2(y, x)
            
            # Project to 2D plane
            r = np.sqrt(x**2 + y**2)
            h = z - self.L1
            
            # Use law of cosines
            d = np.sqrt(r**2 + h**2)
            
            # Check if target is reachable
            if d > (self.L2 + self.L3) or d < abs(self.L2 - self.L3):
                return None  # Unreachable
            
            # Calculate angles using law of cosines
            alpha = np.arctan2(h, r)
            beta = np.arccos((self.L2**2 + d**2 - self.L3**2) / (2 * self.L2 * d))
            gamma = np.arccos((self.L2**2 + self.L3**2 - d**2) / (2 * self.L2 * self.L3))
            
            theta2 = alpha + beta
            theta3 = np.pi - gamma
            
            return [theta1, theta2, theta3]
        
        def jacobian(self, joint_angles):
            """Calculate Jacobian matrix"""
            theta1, theta2, theta3 = joint_angles
            
            # Partial derivatives (simplified for 3-DOF)
            J = np.zeros((3, 3))
            
            # dX/dtheta
            J[0, 0] = -self.L2*np.sin(theta1)*np.cos(theta2) - self.L3*np.sin(theta1)*np.cos(theta2+theta3)
            J[0, 1] = -self.L2*np.cos(theta1)*np.sin(theta2) - self.L3*np.cos(theta1)*np.sin(theta2+theta3)
            J[0, 2] = -self.L3*np.cos(theta1)*np.sin(theta2+theta3)
            
            # dY/dtheta
            J[1, 0] = self.L2*np.cos(theta1)*np.cos(theta2) + self.L3*np.cos(theta1)*np.cos(theta2+theta3)
            J[1, 1] = -self.L2*np.sin(theta1)*np.sin(theta2) - self.L3*np.sin(theta1)*np.sin(theta2+theta3)
            J[1, 2] = -self.L3*np.sin(theta1)*np.sin(theta2+theta3)
            
            # dZ/dtheta (constant for this simplified model)
            J[2, 0] = 0
            J[2, 1] = self.L2*np.cos(theta2) + self.L3*np.cos(theta2+theta3)
            J[2, 2] = self.L3*np.cos(theta2+theta3)
            
            return J
    
    # Test the robotic arm
    arm = RoboticArm3DOF([1.0, 1.0, 0.5])  # Link lengths
    
    # Test forward kinematics
    joint_angles = [np.pi/4, np.pi/6, np.pi/3]
    position, rotation = arm.forward_kinematics(joint_angles)
    
    # Test inverse kinematics
    target = [1.5, 1.0, 1.2]
    ik_solution = arm.inverse_kinematics(target)
    
    # Test Jacobian
    jacobian = arm.jacobian(joint_angles)
    
    return {
        'link_lengths': [1.0, 1.0, 0.5],
        'joint_angles': joint_angles,
        'end_effector_position': position.tolist(),
        'ik_solution_exists': ik_solution is not None,
        'jacobian_determinant': np.linalg.det(jacobian) if jacobian.shape[0] == jacobian.shape[1] else 'non_square',
        'workspace_reachable': np.linalg.norm(position) <= 2.5
    }

def path_planning():
    """Robot path planning algorithms"""
    # Grid-based environment
    grid_size = 20
    obstacles = [
        (5, 5), (5, 6), (5, 7), (6, 5), (7, 5),
        (10, 10), (10, 11), (11, 10), (11, 11),
        (15, 3), (15, 4), (16, 3), (16, 4)
    ]
    
    # A* pathfinding algorithm (simplified)
    class AStar:
        def __init__(self, grid_size, obstacles):
            self.grid_size = grid_size
            self.obstacles = set(obstacles)
        
        def heuristic(self, a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance
        
        def get_neighbors(self, node):
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                x, y = node[0] + dx, node[1] + dy
                if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                    if (x, y) not in self.obstacles:
                        neighbors.append((x, y))
            return neighbors
        
        def find_path(self, start, goal):
            open_set = {start}
            came_from = {}
            g_score = {start: 0}
            f_score = {start: self.heuristic(start, goal)}
            
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
                
                for neighbor in self.get_neighbors(current):
                    tentative_g = g_score[current] + 1
                    
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                        open_set.add(neighbor)
            
            return None  # No path found
    
    # RRT (Rapidly-exploring Random Tree) algorithm (simplified)
    class RRT:
        def __init__(self, start, goal, obstacles, bounds, max_iter=1000):
            self.start = start
            self.goal = goal
            self.obstacles = obstacles
            self.bounds = bounds
            self.max_iter = max_iter
            self.nodes = [start]
            self.edges = []
        
        def random_point(self):
            return (
                np.random.uniform(0, self.bounds[0]),
                np.random.uniform(0, self.bounds[1])
            )
        
        def nearest_node(self, point):
            distances = [np.linalg.norm(np.array(node) - np.array(point)) for node in self.nodes]
            return self.nodes[np.argmin(distances)]
        
        def is_collision_free(self, p1, p2):
            # Simple collision checking
            steps = int(np.linalg.norm(np.array(p2) - np.array(p1)) * 10)
            if steps == 0:
                return True
            
            for i in range(steps + 1):
                t = i / max(steps, 1)
                point = (
                    p1[0] + t * (p2[0] - p1[0]),
                    p1[1] + t * (p2[1] - p1[1])
                )
                
                # Check if point is in obstacle
                for obs in self.obstacles:
                    if np.linalg.norm(np.array(point) - np.array(obs)) < 1.0:
                        return False
            return True
        
        def build_tree(self):
            for _ in range(self.max_iter):
                # Generate random point (with goal bias)
                if np.random.random() < 0.1:
                    rand_point = self.goal
                else:
                    rand_point = self.random_point()
                
                # Find nearest node
                nearest = self.nearest_node(rand_point)
                
                # Create new node in direction of random point
                direction = np.array(rand_point) - np.array(nearest)
                distance = np.linalg.norm(direction)
                if distance > 0:
                    direction = direction / distance
                    new_point = tuple(np.array(nearest) + direction * min(distance, 1.0))
                    
                    # Check collision
                    if self.is_collision_free(nearest, new_point):
                        self.nodes.append(new_point)
                        self.edges.append((nearest, new_point))
                        
                        # Check if we reached the goal
                        if np.linalg.norm(np.array(new_point) - np.array(self.goal)) < 0.5:
                            return True
            return False
    
    # Test A* algorithm
    astar = AStar(grid_size, obstacles)
    start = (1, 1)
    goal = (18, 18)
    astar_path = astar.find_path(start, goal)
    
    # Test RRT algorithm
    rrt = RRT((1.0, 1.0), (18.0, 18.0), obstacles, (grid_size, grid_size))
    rrt_success = rrt.build_tree()
    
    return {
        'grid_size': grid_size,
        'obstacles_count': len(obstacles),
        'astar_path_found': astar_path is not None,
        'astar_path_length': len(astar_path) if astar_path else 0,
        'rrt_nodes_generated': len(rrt.nodes),
        'rrt_goal_reached': rrt_success,
        'path_planning_algorithms': ['A*', 'RRT']
    }

def control_systems():
    """Control system design and analysis"""
    # PID Controller
    class PIDController:
        def __init__(self, kp, ki, kd, dt=0.01):
            self.kp = kp
            self.ki = ki
            self.kd = kd
            self.dt = dt
            self.integral = 0
            self.previous_error = 0
        
        def update(self, setpoint, measurement):
            error = setpoint - measurement
            self.integral += error * self.dt
            derivative = (error - self.previous_error) / self.dt
            
            output = self.kp * error + self.ki * self.integral + self.kd * derivative
            self.previous_error = error
            
            return output
    
    # System identification and control design
    # Second-order system: G(s) = 1 / (s^2 + 2s + 1)
    num = [1]
    den = [1, 2, 1]
    
    try:
        # Create transfer function
        G = control.TransferFunction(num, den)
        
        # System analysis
        poles = control.pole(G)
        zeros = control.zero(G)
        
        # Step response
        t = np.linspace(0, 10, 1000)
        y, t_out = control.step_response(G, t)
        
        # Calculate performance metrics
        step_info = control.step_info(G)
        
        # Controller design
        # Root locus method
        K = np.logspace(-2, 2, 100)
        rlist, klist = control.root_locus(G, K, plot=False)
        
        # Lead compensator design
        # Gc(s) = K * (s + z) / (s + p) where p > z
        z = 0.5  # Zero location
        p = 5.0  # Pole location
        K_comp = 10  # Gain
        
        Gc_num = [K_comp, K_comp * z]
        Gc_den = [1, p]
        Gc = control.TransferFunction(Gc_num, Gc_den)
        
        # Closed-loop system
        T = control.feedback(G * Gc, 1)
        
        # Closed-loop analysis
        cl_poles = control.pole(T)
        cl_step_info = control.step_info(T)
        
        control_analysis = {
            'open_loop_poles': poles.tolist(),
            'open_loop_zeros': zeros.tolist(),
            'step_response_samples': len(y),
            'rise_time': step_info['RiseTime'] if 'RiseTime' in step_info else None,
            'settling_time': step_info['SettlingTime'] if 'SettlingTime' in step_info else None,
            'overshoot': step_info['Overshoot'] if 'Overshoot' in step_info else None,
            'closed_loop_stable': all(np.real(cl_poles) < 0),
            'compensator_type': 'Lead',
            'root_locus_points': len(rlist)
        }
        
    except Exception as e:
        control_analysis = {'error': str(e), 'simulation': True}
    
    # PID controller simulation
    pid = PIDController(kp=1.0, ki=0.1, kd=0.05)
    
    # Simulate system response
    time_steps = 1000
    setpoint = 1.0
    plant_state = 0.0
    plant_velocity = 0.0
    
    pid_response = []
    for i in range(time_steps):
        # PID controller
        control_output = pid.update(setpoint, plant_state)
        
        # Simple plant model (second-order system)
        acceleration = control_output - 2 * plant_velocity - plant_state
        plant_velocity += acceleration * pid.dt
        plant_state += plant_velocity * pid.dt
        
        pid_response.append({
            'time': i * pid.dt,
            'setpoint': setpoint,
            'output': plant_state,
            'control_signal': control_output
        })
    
    return {
        'control_algorithms': ['PID', 'Lead Compensator', 'Root Locus'],
        'pid_simulation_steps': len(pid_response),
        'final_error': abs(setpoint - pid_response[-1]['output']),
        'system_analysis': control_analysis,
        'controller_parameters': {'kp': pid.kp, 'ki': pid.ki, 'kd': pid.kd}
    }

def robot_dynamics():
    """Robot dynamics and motion control"""
    # Define robot dynamics using Lagrangian mechanics
    def robot_dynamics_2dof():
        # Symbolic variables
        q1, q2 = symbols('q1 q2')  # Joint angles
        dq1, dq2 = symbols('dq1 dq2')  # Joint velocities
        ddq1, ddq2 = symbols('ddq1 ddq2')  # Joint accelerations
        tau1, tau2 = symbols('tau1 tau2')  # Joint torques
        
        # Robot parameters
        m1, m2 = 1.0, 0.5  # Link masses
        l1, l2 = 1.0, 0.8   # Link lengths
        lc1, lc2 = 0.5, 0.4 # Center of mass locations
        I1, I2 = 0.1, 0.05  # Moments of inertia
        g = 9.81            # Gravity
        
        # Mass matrix M(q)
        M11 = I1 + I2 + m1*lc1**2 + m2*(l1**2 + lc2**2 + 2*l1*lc2*sp.cos(q2))
        M12 = I2 + m2*(lc2**2 + l1*lc2*sp.cos(q2))
        M21 = M12
        M22 = I2 + m2*lc2**2
        
        M = Matrix([[M11, M12], [M21, M22]])
        
        # Coriolis and centrifugal terms C(q,dq)
        h = -m2*l1*lc2*sp.sin(q2)
        C11 = h*dq2
        C12 = h*(dq1 + dq2)
        C21 = -h*dq1
        C22 = 0
        
        C = Matrix([[C11, C12], [C21, C22]])
        
        # Gravity terms G(q)
        G1 = (m1*lc1 + m2*l1)*g*sp.cos(q1) + m2*lc2*g*sp.cos(q1 + q2)
        G2 = m2*lc2*g*sp.cos(q1 + q2)
        
        G = Matrix([G1, G2])
        
        return {
            'mass_matrix_elements': 4,
            'coriolis_terms': 4,
            'gravity_terms': 2,
            'degrees_of_freedom': 2,
            'mass_matrix_determinant': simplify(M.det()),
            'system_parameters': {'m1': m1, 'm2': m2, 'l1': l1, 'l2': l2}
        }
    
    # Forward dynamics simulation
    def simulate_robot_motion():
        # Simplified 2-DOF robot simulation
        dt = 0.01
        t_final = 5.0
        t = np.arange(0, t_final, dt)
        
        # Initial conditions
        q1_0, q2_0 = 0.0, 0.0      # Initial angles
        dq1_0, dq2_0 = 0.0, 0.0    # Initial velocities
        
        # Control inputs (sinusoidal torques)
        def control_torques(time):
            tau1 = 2.0 * np.sin(0.5 * time)
            tau2 = 1.0 * np.cos(0.8 * time)
            return tau1, tau2
        
        # Simplified dynamics (linear approximation)
        def robot_ode(state, time):
            q1, q2, dq1, dq2 = state
            
            # Get control torques
            tau1, tau2 = control_torques(time)
            
            # Simplified mass matrix (constant approximation)
            M = np.array([[2.0, 0.5], [0.5, 1.0]])
            
            # Simplified dynamics: M * ddq = tau - C*dq - G
            C = np.array([[0.1, 0.05], [0.05, 0.1]])  # Damping
            G = np.array([9.81 * np.sin(q1), 4.9 * np.sin(q1 + q2)])  # Gravity
            
            tau = np.array([tau1, tau2])
            dq = np.array([dq1, dq2])
            
            # Solve for accelerations
            ddq = np.linalg.solve(M, tau - C @ dq - G)
            
            return [dq1, dq2, ddq[0], ddq[1]]
        
        # Integrate the ODE
        initial_state = [q1_0, q2_0, dq1_0, dq2_0]
        solution = odeint(robot_ode, initial_state, t)
        
        # Extract results
        q1_traj = solution[:, 0]
        q2_traj = solution[:, 1]
        dq1_traj = solution[:, 2]
        dq2_traj = solution[:, 3]
        
        # Calculate energy
        kinetic_energy = 0.5 * (dq1_traj**2 + dq2_traj**2)  # Simplified
        potential_energy = 9.81 * (np.sin(q1_traj) + 0.5 * np.sin(q1_traj + q2_traj))  # Simplified
        total_energy = kinetic_energy + potential_energy
        
        return {
            'simulation_time': t_final,
            'time_steps': len(t),
            'final_joint_angles': [float(q1_traj[-1]), float(q2_traj[-1])],
            'max_joint_velocities': [float(np.max(np.abs(dq1_traj))), float(np.max(np.abs(dq2_traj)))],
            'energy_conservation': float(np.std(total_energy) / np.mean(total_energy)),
            'trajectory_length': len(solution)
        }
    
    dynamics_model = robot_dynamics_2dof()
    simulation_results = simulate_robot_motion()
    
    return {
        'dynamics_model': dynamics_model,
        'simulation': simulation_results,
        'motion_planning_complete': True
    }

def sensor_fusion():
    """Multi-sensor data fusion for robotics"""
    # Kalman Filter for sensor fusion
    class KalmanFilter:
        def __init__(self, F, H, Q, R, P, x):
            self.F = F  # State transition model
            self.H = H  # Observation model
            self.Q = Q  # Process noise covariance
            self.R = R  # Measurement noise covariance
            self.P = P  # Error covariance
            self.x = x  # Initial state
        
        def predict(self):
            self.x = self.F @ self.x
            self.P = self.F @ self.P @ self.F.T + self.Q
        
        def update(self, z):
            y = z - self.H @ self.x  # Innovation
            S = self.H @ self.P @ self.H.T + self.R  # Innovation covariance
            K = self.P @ self.H.T @ np.linalg.inv(S)  # Kalman gain
            
            self.x = self.x + K @ y
            self.P = (np.eye(len(self.x)) - K @ self.H) @ self.P
    
    # Simulate multi-sensor robot localization
    dt = 0.1  # Time step
    n_steps = 500
    
    # State: [x, y, vx, vy] (position and velocity)
    F = np.array([[1, 0, dt, 0],
                  [0, 1, 0, dt],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1]])
    
    # Observation model (we observe position only)
    H = np.array([[1, 0, 0, 0],
                  [0, 1, 0, 0]])
    
    # Process and measurement noise
    Q = np.eye(4) * 0.1  # Process noise
    R = np.eye(2) * 0.5  # Measurement noise
    
    # Initial conditions
    P = np.eye(4) * 10   # Initial uncertainty
    x = np.array([0, 0, 1, 1])  # Initial state
    
    kf = KalmanFilter(F, H, Q, R, P, x)
    
    # Simulate sensors
    true_positions = []
    gps_measurements = []
    camera_measurements = []
    fused_estimates = []
    
    for i in range(n_steps):
        # True robot motion (circular path)
        t = i * dt
        true_x = 10 * np.cos(0.1 * t)
        true_y = 10 * np.sin(0.1 * t)
        true_positions.append([true_x, true_y])
        
        # GPS measurement (lower frequency, higher noise)
        if i % 5 == 0:  # GPS updates every 0.5 seconds
            gps_x = true_x + np.random.normal(0, 1.0)
            gps_y = true_y + np.random.normal(0, 1.0)
            gps_measurements.append([gps_x, gps_y])
            
            # Kalman filter update with GPS
            kf.predict()
            kf.update(np.array([gps_x, gps_y]))
        
        # Camera measurement (higher frequency, moderate noise)
        if i % 2 == 0:  # Camera updates every 0.2 seconds
            cam_x = true_x + np.random.normal(0, 0.3)
            cam_y = true_y + np.random.normal(0, 0.3)
            camera_measurements.append([cam_x, cam_y])
            
            # Kalman filter update with camera
            kf.predict()
            kf.update(np.array([cam_x, cam_y]))
        
        # Store fused estimate
        fused_estimates.append(kf.x[:2].copy())
    
    # Calculate performance metrics
    position_errors = []
    for i, (true_pos, fused_pos) in enumerate(zip(true_positions, fused_estimates)):
        error = np.linalg.norm(np.array(true_pos) - np.array(fused_pos))
        position_errors.append(error)
    
    return {
        'simulation_steps': n_steps,
        'gps_measurements': len(gps_measurements),
        'camera_measurements': len(camera_measurements),
        'average_position_error': np.mean(position_errors),
        'max_position_error': np.max(position_errors),
        'sensor_types': ['GPS', 'Camera'],
        'fusion_algorithm': 'Kalman Filter'
    }

if __name__ == "__main__":
    print("Robotics and control systems operations...")
    
    # Robot kinematics
    kinematics_result = robotic_kinematics()
    print(f"Kinematics: 3-DOF arm, end-effector at {np.linalg.norm(kinematics_result['end_effector_position']):.2f}m, IK solution: {kinematics_result['ik_solution_exists']}")
    
    # Path planning
    planning_result = path_planning()
    print(f"Path Planning: A* path length {planning_result['astar_path_length']}, RRT nodes {planning_result['rrt_nodes_generated']}")
    
    # Control systems
    control_result = control_systems()
    print(f"Control: {len(control_result['control_algorithms'])} algorithms, PID final error {control_result['final_error']:.4f}")
    
    # Robot dynamics
    dynamics_result = robot_dynamics()
    print(f"Dynamics: 2-DOF robot, {dynamics_result['simulation']['time_steps']} simulation steps, energy conservation {dynamics_result['simulation']['energy_conservation']:.6f}")
    
    # Sensor fusion
    fusion_result = sensor_fusion()
    print(f"Sensor Fusion: {len(fusion_result['sensor_types'])} sensor types, average error {fusion_result['average_position_error']:.3f}m")