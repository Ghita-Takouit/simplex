from django.shortcuts import render
from django.http import HttpResponse
import numpy as np
from fractions import Fraction
import pandas as pd

# Import the functions and code from the provided Python file
from .simplex_cal import maximization, minimization, stdz_rows, stdz_rows2

# Define the view function for the index page
def index(request):
    # Handle POST request (form submission)
    if request.method == 'POST':
        try:
            # Retrieve form data
            prob_type = int(request.POST.get('prob_type'))
            const_num = int(request.POST.get('const_num'))
            prod_nums = int(request.POST.get('prod_nums'))
            decimals = int(request.POST.get('decimals'))
            
            # Get list of product names and constraint names
            product_names = request.POST.getlist('product_names')
            const_names = [f'X{i}' for i in range(1, const_num + 1)]
            
            # Retrieve values for Z equation and convert to floats
            z_equation = []
            for i in range(const_num):
                value = request.POST.get(f'z_value_{i}')
                if value:
                    z_equation.append(float(Fraction(value)))
                else:
                    raise ValueError(f"Missing input for z_value_{i}")
            z_equation.append(0)
            
            # Retrieve values for the constraints and convert to floats
            col_values = []
            for prod in product_names:
                for const in const_names:
                    value = request.POST.get(f'{const}_{prod}')
                    if value:
                        col_values.append(float(Fraction(value)))
                    else:
                        raise ValueError(f"Missing input for {const}_{prod}")
                equate_prod = request.POST.get(f'equate_{prod}')
                if equate_prod:
                    col_values.append(float(Fraction(equate_prod)))
                else:
                    raise ValueError(f"Missing input for equate_{prod}")
            
            # Calculate and standardize rows based on the problem type
            if prob_type == 1:  # Maximization
                final_cols = stdz_rows(col_values)
                final_cols.append(z_equation)
                final_rows = np.array(final_cols).T.tolist()
                maximization(final_cols, final_rows)
            elif prob_type == 2:  # Minimization
                final_cols = stdz_rows2(col_values)
                final_cols.append(z_equation)
                final_rows = np.array(final_cols).T.tolist()
                minimization(final_cols, final_rows)
            else:
                return HttpResponse("Invalid problem type selected.")
            
            # Render results in a template
            return render(request, 'app/result.html', {'final_cols': final_cols, 'final_rows': final_rows})
        
        except ValueError as e:
            # Return an error message if input validation fails
            return HttpResponse(f"Error: {e}")
    
    # Render the input form on GET request
    return render(request, 'app/index.html')
