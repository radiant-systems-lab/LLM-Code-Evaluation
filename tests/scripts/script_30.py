# Scientific Computing and Simulation
import numpy as np
import scipy.optimize
import scipy.integrate
import scipy.linalg
import scipy.stats
import sympy
from sympy import symbols, diff, integrate, solve
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import numba
from numba import jit

def numerical_optimization():
    """Numerical optimization problems"""
    # Define objective function
    def rosenbrock(x):
        """Rosenbrock function - classic optimization test"""
        return sum(100.0 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)
    
    def rastrigin(x):
        """Rastrigin function - multimodal optimization"""
        A = 10
        n = len(x)
        return A * n + sum(xi**2 - A * np.cos(2 * np.pi * xi) for xi in x)
    
    # Initial guess
    x0 = np.array([1.3, 0.7, 0.8, 1.9, 1.2])
    
    # Optimization results
    optimization_results = []
    
    # Nelder-Mead
    result_nm = scipy.optimize.minimize(rosenbrock, x0, method='Nelder-Mead')
    optimization_results.append({
        'method': 'Nelder-Mead',
        'success': result_nm.success,
        'function_value': result_nm.fun,
        'iterations': result_nm.nit
    })
    
    # BFGS
    result_bfgs = scipy.optimize.minimize(rosenbrock, x0, method='BFGS')
    optimization_results.append({
        'method': 'BFGS',
        'success': result_bfgs.success,
        'function_value': result_bfgs.fun,
        'iterations': result_bfgs.nit
    })
    
    # Constrained optimization
    constraints = {'type': 'eq', 'fun': lambda x: x[0] + x[1] - 1}
    bounds = [(0, None), (0, None), (0, None), (0, None), (0, None)]
    
    result_constrained = scipy.optimize.minimize(
        rosenbrock, x0, method='SLSQP', 
        bounds=bounds, constraints=constraints
    )
    
    optimization_results.append({
        'method': 'SLSQP (constrained)',
        'success': result_constrained.success,
        'function_value': result_constrained.fun,
        'iterations': result_constrained.nit
    })
    
    # Global optimization
    result_global = scipy.optimize.differential_evolution(
        rastrigin, [(-5, 5)] * 3
    )
    
    optimization_results.append({
        'method': 'Differential Evolution',
        'success': result_global.success,
        'function_value': result_global.fun,
        'iterations': result_global.nit
    })
    
    return {
        'optimization_methods': len(optimization_results),
        'successful_optimizations': len([r for r in optimization_results if r['success']]),
        'results': optimization_results
    }

def numerical_integration():
    """Numerical integration examples"""
    # Single integral
    def integrand1(x):
        return np.exp(-x**2)
    
    result1, error1 = scipy.integrate.quad(integrand1, 0, np.inf)
    
    # Double integral
    def integrand2(y, x):
        return x * y**2
    
    result2, error2 = scipy.integrate.dblquad(
        integrand2, 0, 2, lambda x: 0, lambda x: 1
    )
    
    # Triple integral
    def integrand3(z, y, x):
        return x + y + z
    
    result3, error3 = scipy.integrate.tplquad(
        integrand3, 0, 1, lambda x: 0, lambda x: 1, 
        lambda x, y: 0, lambda x, y: 1
    )
    
    # Ordinary Differential Equation
    def dydt(t, y):
        return -2 * y + 1
    
    t_span = (0, 5)
    y0 = [0]
    t_eval = np.linspace(0, 5, 50)
    
    sol = scipy.integrate.solve_ivp(dydt, t_span, y0, t_eval=t_eval)
    
    # Monte Carlo integration
    def monte_carlo_pi(n_samples):
        x = np.random.uniform(-1, 1, n_samples)
        y = np.random.uniform(-1, 1, n_samples)
        inside_circle = (x**2 + y**2) <= 1
        pi_estimate = 4 * np.sum(inside_circle) / n_samples
        return pi_estimate
    
    pi_estimate = monte_carlo_pi(100000)
    
    integration_results = {
        'gaussian_integral': {'result': result1, 'error': error1},
        'double_integral': {'result': result2, 'error': error2},
        'triple_integral': {'result': result3, 'error': error3},
        'ode_solution_points': len(sol.t),
        'monte_carlo_pi': pi_estimate,
        'pi_error': abs(pi_estimate - np.pi)
    }
    
    return {
        'integration_methods': 5,
        'ode_successful': sol.success,
        'results': integration_results
    }

def linear_algebra_operations():
    """Linear algebra computations"""
    # Create test matrices
    A = np.random.rand(5, 5)
    A = A + A.T  # Make symmetric
    b = np.random.rand(5)
    
    # Eigenvalue decomposition
    eigenvalues, eigenvectors = scipy.linalg.eigh(A)
    
    # Singular Value Decomposition
    U, s, Vt = scipy.linalg.svd(A)
    
    # LU decomposition
    P, L, U_lu = scipy.linalg.lu(A)
    
    # Cholesky decomposition (for positive definite matrix)
    A_pd = A.T @ A + np.eye(5)  # Make positive definite
    L_chol = scipy.linalg.cholesky(A_pd, lower=True)
    
    # QR decomposition
    Q, R = scipy.linalg.qr(A)
    
    # Solve linear system
    x = scipy.linalg.solve(A, b)
    residual = np.linalg.norm(A @ x - b)
    
    # Matrix properties
    condition_number = np.linalg.cond(A)
    determinant = np.linalg.det(A)
    rank = np.linalg.matrix_rank(A)
    
    # Pseudoinverse
    A_rect = np.random.rand(7, 5)
    A_pinv = scipy.linalg.pinv(A_rect)
    
    return {
        'matrix_size': A.shape,
        'eigenvalues_count': len(eigenvalues),
        'singular_values_count': len(s),
        'condition_number': condition_number,
        'determinant': determinant,
        'rank': rank,
        'residual_norm': residual,
        'decompositions': ['LU', 'Cholesky', 'QR', 'SVD', 'Eigenvalue']
    }

def symbolic_mathematics():
    """Symbolic mathematics with SymPy"""
    # Define symbols
    x, y, z = symbols('x y z')
    t = symbols('t')
    
    # Define expressions
    expr1 = x**2 + 2*x + 1
    expr2 = sympy.sin(x) * sympy.cos(y)
    expr3 = sympy.exp(x) * sympy.log(x)
    
    # Calculus operations
    # Derivatives
    derivative1 = diff(expr1, x)
    derivative2 = diff(expr2, x)
    derivative3 = diff(expr3, x)
    
    # Integrals
    integral1 = integrate(expr1, x)
    integral2 = integrate(sympy.sin(x), (x, 0, sympy.pi))
    integral3 = integrate(x * sympy.exp(-x**2), (x, -sympy.oo, sympy.oo))
    
    # Equation solving
    equation1 = sympy.Eq(x**2 - 4, 0)
    solutions1 = solve(equation1, x)
    
    equation2 = [x + y - 5, x - y - 1]
    solutions2 = solve(equation2, [x, y])
    
    # Series expansion
    series1 = sympy.series(sympy.sin(x), x, 0, n=6)
    series2 = sympy.series(sympy.exp(x), x, 0, n=5)
    
    # Limits
    limit1 = sympy.limit(sympy.sin(x)/x, x, 0)
    limit2 = sympy.limit((1 + 1/x)**x, x, sympy.oo)
    
    # Matrix operations
    M = sympy.Matrix([[1, 2], [3, 4]])
    M_inv = M.inv()
    M_det = M.det()
    M_eigenvals = M.eigenvals()
    
    return {
        'expressions_defined': 3,
        'derivatives_computed': 3,
        'integrals_computed': 3,
        'equations_solved': 2,
        'series_expansions': 2,
        'limits_computed': 2,
        'matrix_operations': 4,
        'solutions': {
            'quadratic': solutions1,
            'linear_system': solutions2
        }
    }

@jit(nopython=True)
def monte_carlo_simulation_numba(n_simulations):
    """Monte Carlo simulation with Numba acceleration"""
    results = np.zeros(n_simulations)
    
    for i in range(n_simulations):
        # Simulate random walk
        steps = 1000
        position = 0.0
        
        for j in range(steps):
            step = np.random.randn()
            position += step
        
        results[i] = position
    
    return results

def statistical_analysis():
    """Statistical analysis and hypothesis testing"""
    # Generate sample data
    np.random.seed(42)
    sample1 = np.random.normal(100, 15, 1000)
    sample2 = np.random.normal(105, 12, 1000)
    sample3 = np.random.exponential(2, 1000)
    
    # Descriptive statistics
    stats_sample1 = {
        'mean': np.mean(sample1),
        'std': np.std(sample1),
        'skewness': scipy.stats.skew(sample1),
        'kurtosis': scipy.stats.kurtosis(sample1)
    }
    
    # Normality tests
    shapiro_stat, shapiro_p = scipy.stats.shapiro(sample1[:1000])
    ks_stat, ks_p = scipy.stats.kstest(sample1, 'norm', 
                                       args=(np.mean(sample1), np.std(sample1)))
    
    # Two-sample tests
    ttest_stat, ttest_p = scipy.stats.ttest_ind(sample1, sample2)
    mannwhitney_stat, mannwhitney_p = scipy.stats.mannwhitneyu(sample1, sample2)
    
    # ANOVA
    f_stat, f_p = scipy.stats.f_oneway(sample1, sample2, sample3)
    
    # Correlation analysis
    correlation_matrix = np.corrcoef([sample1, sample2])
    correlation_coeff = correlation_matrix[0, 1]
    
    # Regression analysis
    x = np.random.rand(100)
    y = 2 * x + 1 + np.random.normal(0, 0.1, 100)
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    
    return {
        'samples': 3,
        'sample_size': len(sample1),
        'descriptive_stats': stats_sample1,
        'normality_tests': 2,
        'hypothesis_tests': 3,
        'correlation_coefficient': correlation_coeff,
        'regression': {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_value**2,
            'p_value': p_value
        }
    }

def differential_equations():
    """Solve differential equations"""
    # First-order ODE: dy/dt = -y + sin(t)
    def ode1(t, y):
        return -y + np.sin(t)
    
    # Second-order ODE: d2y/dt2 + dy/dt + y = 0
    def ode2(t, y):
        dydt = y[1]
        d2ydt2 = -y[1] - y[0]
        return [dydt, d2ydt2]
    
    # System of ODEs: Lotka-Volterra equations
    def lotka_volterra(t, y):
        x, y_pred = y
        dxdt = x * (1 - 0.1 * y_pred)
        dydt = -0.75 * y_pred * (1 - 0.05 * x)
        return [dxdt, dydt]
    
    # Solve ODEs
    t_span = (0, 10)
    t_eval = np.linspace(0, 10, 100)
    
    # First-order ODE
    sol1 = scipy.integrate.solve_ivp(ode1, t_span, [1], t_eval=t_eval)
    
    # Second-order ODE
    sol2 = scipy.integrate.solve_ivp(ode2, t_span, [1, 0], t_eval=t_eval)
    
    # Lotka-Volterra system
    sol3 = scipy.integrate.solve_ivp(lotka_volterra, t_span, [4, 2], t_eval=t_eval)
    
    # Boundary value problem (simplified)
    def bvp_ode(x, y):
        return np.vstack((y[1], -y[0]))
    
    def boundary_conditions(ya, yb):
        return np.array([ya[0], yb[0] - 1])
    
    x = np.linspace(0, np.pi, 11)
    y_guess = np.zeros((2, x.size))
    y_guess[0] = np.sin(x)
    
    try:
        bvp_sol = scipy.integrate.solve_bvp(bvp_ode, boundary_conditions, x, y_guess)
        bvp_success = bvp_sol.success
    except:
        bvp_success = False
    
    return {
        'ode_systems_solved': 3,
        'first_order_success': sol1.success,
        'second_order_success': sol2.success,
        'lotka_volterra_success': sol3.success,
        'bvp_success': bvp_success,
        'solution_points': len(t_eval),
        'time_span': t_span
    }

if __name__ == "__main__":
    print("Scientific computing and simulation operations...")
    
    # Numerical optimization
    opt_result = numerical_optimization()
    print(f"Optimization: {opt_result['successful_optimizations']}/{opt_result['optimization_methods']} methods successful")
    
    # Numerical integration
    integration_result = numerical_integration()
    print(f"Integration: {integration_result['integration_methods']} methods, ODE success: {integration_result['ode_successful']}")
    
    # Linear algebra
    linalg_result = linear_algebra_operations()
    print(f"Linear Algebra: {len(linalg_result['decompositions'])} decompositions, condition number: {linalg_result['condition_number']:.2f}")
    
    # Symbolic mathematics
    symbolic_result = symbolic_mathematics()
    print(f"Symbolic: {symbolic_result['expressions_defined']} expressions, {symbolic_result['equations_solved']} equation systems solved")
    
    # Monte Carlo simulation
    mc_results = monte_carlo_simulation_numba(1000)
    print(f"Monte Carlo: {len(mc_results)} simulations, mean position: {np.mean(mc_results):.3f}")
    
    # Statistical analysis
    stats_result = statistical_analysis()
    print(f"Statistics: {stats_result['samples']} samples, R²: {stats_result['regression']['r_squared']:.4f}")
    
    # Differential equations
    ode_result = differential_equations()
    print(f"ODEs: {ode_result['ode_systems_solved']} systems solved, {ode_result['solution_points']} solution points")