# Scientific Computing with NumPy and SciPy
import numpy as np
from scipy import optimize, integrate, stats, linalg
from scipy.special import gamma, beta
import sympy as sp
from sympy import symbols, diff, integrate as sym_integrate

def numerical_analysis():
    """Numerical analysis operations"""
    # Create arrays
    x = np.linspace(0, 10, 100)
    y = np.sin(x) * np.exp(-x/5)
    
    # Statistical operations
    mean_val = np.mean(y)
    std_val = np.std(y)
    
    # Linear algebra
    A = np.random.random((5, 5))
    eigenvals, eigenvecs = linalg.eig(A)
    
    return {'mean': mean_val, 'std': std_val, 'eigenvals': len(eigenvals)}

def optimization_example():
    """Optimization using SciPy"""
    def objective(x):
        return x[0]**2 + x[1]**2 + 2*x[0]*x[1]
    
    result = optimize.minimize(objective, [1, 1])
    return result.x

def symbolic_math():
    """Symbolic mathematics with SymPy"""
    x = symbols('x')
    f = x**3 + 2*x**2 + x + 1
    
    derivative = diff(f, x)
    integral = sym_integrate(f, x)
    
    return str(derivative), str(integral)

if __name__ == "__main__":
    print("Scientific computing operations...")
    result = numerical_analysis()
    print(f"Mean: {result['mean']:.4f}")
    
    opt_result = optimization_example()
    print(f"Optimization result: {opt_result}")
    
    deriv, integ = symbolic_math()
    print(f"Derivative: {deriv}")
