# Optimization and Operations Research
import numpy as np
from scipy.optimize import minimize, linprog, differential_evolution
from scipy.sparse import csr_matrix
from sklearn.cluster import KMeans
import cvxpy as cp
import pulp
from ortools.linear_solver import pywraplp
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

def linear_programming():
    """Linear programming and optimization"""
    try:
        # Classic LP problem: Maximize 3x + 4y subject to constraints
        # 2x + 3y <= 6
        # -3x + 2y <= 3
        # 2x + y <= 4
        # x, y >= 0
        
        # Coefficient matrix and bounds
        A_ub = np.array([[2, 3], [-3, 2], [2, 1]])
        b_ub = np.array([6, 3, 4])
        c = np.array([-3, -4])  # Negative for maximization
        bounds = [(0, None), (0, None)]
        
        # Solve using scipy
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        
        # Portfolio optimization problem
        # Minimize risk while achieving target return
        n_assets = 5
        np.random.seed(42)
        
        # Generate random covariance matrix
        A = np.random.randn(n_assets, n_assets)
        cov_matrix = A @ A.T  # Ensure positive semidefinite
        
        # Expected returns
        expected_returns = np.random.uniform(0.05, 0.15, n_assets)
        target_return = 0.10
        
        # Variables: portfolio weights
        weights = cp.Variable(n_assets)
        
        # Objective: minimize portfolio variance
        portfolio_variance = cp.quad_form(weights, cov_matrix)
        
        # Constraints
        constraints = [
            cp.sum(weights) == 1,  # Weights sum to 1
            weights @ expected_returns >= target_return,  # Target return
            weights >= 0  # No short selling
        ]
        
        # Solve
        problem = cp.Problem(cp.Minimize(portfolio_variance), constraints)
        problem.solve()
        
        optimal_weights = weights.value if weights.value is not None else np.zeros(n_assets)
        optimal_return = optimal_weights @ expected_returns
        optimal_risk = np.sqrt(optimal_weights @ cov_matrix @ optimal_weights)
        
        # Transportation problem
        # Supply and demand problem
        supply = [20, 30, 25]
        demand = [30, 20, 25]
        
        # Cost matrix (cost of shipping from supply[i] to demand[j])
        costs = np.array([
            [8, 6, 10],
            [9, 12, 13],
            [14, 9, 16]
        ])
        
        # Create PuLP problem
        prob = pulp.LpProblem("Transportation", pulp.LpMinimize)
        
        # Decision variables
        x = {}
        for i in range(len(supply)):
            for j in range(len(demand)):
                x[i, j] = pulp.LpVariable(f"x_{i}_{j}", lowBound=0, cat='Continuous')
        
        # Objective function
        prob += pulp.lpSum(costs[i][j] * x[i, j] for i in range(len(supply)) for j in range(len(demand)))
        
        # Supply constraints
        for i in range(len(supply)):
            prob += pulp.lpSum(x[i, j] for j in range(len(demand))) <= supply[i]
        
        # Demand constraints
        for j in range(len(demand)):
            prob += pulp.lpSum(x[i, j] for i in range(len(supply))) >= demand[j]
        
        # Solve
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
        
        transport_cost = pulp.value(prob.objective)
        
        return {
            'lp_status': result.success,
            'lp_optimal_value': -result.fun if result.success else 0,  # Convert back from minimization
            'lp_solution': result.x.tolist() if result.success else [0, 0],
            'portfolio_assets': n_assets,
            'portfolio_target_return': target_return,
            'portfolio_optimal_return': optimal_return,
            'portfolio_risk': optimal_risk,
            'portfolio_weights': optimal_weights.tolist() if optimal_weights is not None else [],
            'transportation_cost': transport_cost if transport_cost else 0,
            'supply_points': len(supply),
            'demand_points': len(demand)
        }
        
    except Exception as e:
        return {'error': str(e)}

def nonlinear_optimization():
    """Nonlinear optimization problems"""
    try:
        # Rosenbrock function optimization
        def rosenbrock(x):
            return sum(100.0 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)
        
        # Starting point
        x0 = np.array([1.3, 0.7, 0.8, 1.9, 1.2])
        
        # Unconstrained optimization
        result_unconstrained = minimize(rosenbrock, x0, method='BFGS')
        
        # Constrained optimization
        # Constraint: sum of variables = 3
        constraint = {'type': 'eq', 'fun': lambda x: np.sum(x) - 3}
        bounds = [(-2, 2) for _ in range(len(x0))]
        
        result_constrained = minimize(rosenbrock, x0, method='SLSQP', 
                                    constraints=constraint, bounds=bounds)
        
        # Multi-objective optimization (scalarization)
        def multi_objective(x):
            # Objective 1: Minimize sum of squares
            obj1 = np.sum(x**2)
            # Objective 2: Minimize sum of absolute values
            obj2 = np.sum(np.abs(x))
            # Weighted sum
            return 0.7 * obj1 + 0.3 * obj2
        
        result_multi = minimize(multi_objective, x0, method='L-BFGS-B')
        
        # Global optimization with Differential Evolution
        bounds_global = [(-5, 5) for _ in range(3)]  # Smaller problem for speed
        result_global = differential_evolution(lambda x: rosenbrock(x), bounds_global, seed=42)
        
        # Optimization with constraints using penalty method
        def penalized_objective(x, penalty=1000):
            obj = rosenbrock(x)
            # Penalty for constraint violation
            constraint_violation = max(0, abs(np.sum(x) - 3) - 0.01)
            return obj + penalty * constraint_violation**2
        
        result_penalty = minimize(lambda x: penalized_objective(x), x0, method='Nelder-Mead')
        
        # Least squares optimization
        def residuals(x, t, y):
            # Fit exponential decay: y = a * exp(-b * t) + c
            a, b, c = x
            return y - (a * np.exp(-b * t) + c)
        
        # Generate synthetic data
        t_data = np.linspace(0, 5, 50)
        true_params = [2.0, 0.5, 0.1]
        y_data = true_params[0] * np.exp(-true_params[1] * t_data) + true_params[2] + 0.1 * np.random.randn(50)
        
        # Fit parameters
        from scipy.optimize import least_squares
        result_lsq = least_squares(residuals, [1.0, 1.0, 0.0], args=(t_data, y_data))
        
        return {
            'unconstrained_success': result_unconstrained.success,
            'unconstrained_value': result_unconstrained.fun,
            'unconstrained_iterations': result_unconstrained.nit,
            'constrained_success': result_constrained.success,
            'constrained_value': result_constrained.fun,
            'multi_objective_value': result_multi.fun,
            'global_optimization_value': result_global.fun,
            'penalty_method_value': result_penalty.fun,
            'curve_fitting_success': result_lsq.success,
            'curve_fitting_residual': result_lsq.cost,
            'fitted_parameters': result_lsq.x.tolist()
        }
        
    except Exception as e:
        return {'error': str(e)}

def combinatorial_optimization():
    """Combinatorial optimization problems"""
    try:
        # Traveling Salesman Problem (TSP)
        n_cities = 10
        np.random.seed(42)
        
        # Generate random city coordinates
        cities = np.random.rand(n_cities, 2) * 100
        
        # Calculate distance matrix
        distance_matrix = np.zeros((n_cities, n_cities))
        for i in range(n_cities):
            for j in range(n_cities):
                if i != j:
                    distance_matrix[i][j] = np.linalg.norm(cities[i] - cities[j])
                else:
                    distance_matrix[i][j] = 0
        
        # Nearest neighbor heuristic for TSP
        def nearest_neighbor_tsp(distance_matrix):
            n = len(distance_matrix)
            unvisited = set(range(1, n))
            current_city = 0
            tour = [current_city]
            total_distance = 0
            
            while unvisited:
                nearest_city = min(unvisited, key=lambda city: distance_matrix[current_city][city])
                total_distance += distance_matrix[current_city][nearest_city]
                tour.append(nearest_city)
                unvisited.remove(nearest_city)
                current_city = nearest_city
            
            # Return to start
            total_distance += distance_matrix[current_city][0]
            tour.append(0)
            
            return tour, total_distance
        
        tsp_tour, tsp_distance = nearest_neighbor_tsp(distance_matrix)
        
        # Knapsack problem
        def knapsack_01(weights, values, capacity):
            n = len(weights)
            # Dynamic programming table
            dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
            
            # Fill the table
            for i in range(1, n + 1):
                for w in range(1, capacity + 1):
                    # Don't include item i-1
                    dp[i][w] = dp[i-1][w]
                    
                    # Include item i-1 if it fits and improves value
                    if weights[i-1] <= w:
                        dp[i][w] = max(dp[i][w], dp[i-1][w-weights[i-1]] + values[i-1])
            
            # Backtrack to find selected items
            selected = []
            w = capacity
            for i in range(n, 0, -1):
                if dp[i][w] != dp[i-1][w]:
                    selected.append(i-1)
                    w -= weights[i-1]
            
            return dp[n][capacity], selected
        
        # Knapsack instance
        weights = [10, 20, 30]
        values = [60, 100, 120]
        capacity = 50
        
        knapsack_value, knapsack_items = knapsack_01(weights, values, capacity)
        
        # Assignment problem (Hungarian algorithm simulation)
        def assignment_problem(cost_matrix):
            # Simplified assignment using greedy approach
            n = len(cost_matrix)
            assigned = [False] * n
            assignment = [-1] * n
            total_cost = 0
            
            # Greedy assignment (not optimal but simple)
            for i in range(n):
                best_j = -1
                best_cost = float('inf')
                for j in range(n):
                    if not assigned[j] and cost_matrix[i][j] < best_cost:
                        best_cost = cost_matrix[i][j]
                        best_j = j
                
                if best_j != -1:
                    assignment[i] = best_j
                    assigned[best_j] = True
                    total_cost += best_cost
            
            return assignment, total_cost
        
        # Assignment cost matrix
        assignment_costs = np.array([
            [9, 2, 7, 8],
            [6, 4, 3, 7],
            [5, 8, 1, 8],
            [7, 6, 9, 4]
        ])
        
        assignment_solution, assignment_cost = assignment_problem(assignment_costs)
        
        # Graph coloring problem (greedy)
        def graph_coloring(adjacency_matrix):
            n = len(adjacency_matrix)
            colors = [-1] * n
            colors[0] = 0  # Color first vertex with color 0
            
            for v in range(1, n):
                # Find available colors
                available_colors = [True] * n
                
                # Check colors of adjacent vertices
                for u in range(n):
                    if adjacency_matrix[v][u] == 1 and colors[u] != -1:
                        available_colors[colors[u]] = False
                
                # Assign first available color
                for color in range(n):
                    if available_colors[color]:
                        colors[v] = color
                        break
            
            return colors, max(colors) + 1
        
        # Create random graph
        n_vertices = 8
        adjacency = np.random.choice([0, 1], size=(n_vertices, n_vertices), p=[0.7, 0.3])
        # Make symmetric and remove self-loops
        adjacency = (adjacency + adjacency.T) // 2
        np.fill_diagonal(adjacency, 0)
        
        coloring, num_colors = graph_coloring(adjacency)
        
        return {
            'tsp_cities': n_cities,
            'tsp_tour_length': tsp_distance,
            'tsp_tour': tsp_tour,
            'knapsack_capacity': capacity,
            'knapsack_max_value': knapsack_value,
            'knapsack_selected_items': knapsack_items,
            'assignment_workers': len(assignment_costs),
            'assignment_cost': assignment_cost,
            'graph_vertices': n_vertices,
            'graph_chromatic_number': num_colors,
            'combinatorial_problems_solved': 4
        }
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    print("Optimization and operations research...")
    
    # Linear programming
    lp_result = linear_programming()
    if 'error' not in lp_result:
        print(f"LP: Optimal value {lp_result['lp_optimal_value']:.3f}, Portfolio risk {lp_result['portfolio_risk']:.3f}")
    
    # Nonlinear optimization
    nlp_result = nonlinear_optimization()
    if 'error' not in nlp_result:
        print(f"NLP: Unconstrained {nlp_result['unconstrained_value']:.3f}, Global {nlp_result['global_optimization_value']:.3f}")
    
    # Combinatorial optimization
    comb_result = combinatorial_optimization()
    if 'error' not in comb_result:
        print(f"Combinatorial: TSP distance {comb_result['tsp_tour_length']:.2f}, {comb_result['combinatorial_problems_solved']} problems solved")