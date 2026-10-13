"""
MoCaX sliding example for Python

"""

from __future__ import print_function

import math
import os
import sys
from ctypes import *

import mocaxpy


# Example pre-existing function.
def example_3d_function(x1, x2, x3):
    return math.sin(x1) + math.sin(x2) + math.sin(x3)


# Original function wrapper (adapts the original function signature to the signature expected by MoCaX).
def wrapped_example_3d_function(x, additionalData):
    return example_3d_function(x[0], x[1], x[2])

try:
    # Number of dimensions for each partial function. They all should add to exactly numDimensions 
    # (the number of dimensions used by the original function).
    num_dimensions_per_partial = [
        1, 
        1, 
        1
    ]
        
    # Function domain for X1, X2 and X3
    domainValues = [
        [-1.0, 1.0],
        [-1.0, 1.0],
        [1.0, 3.0]
    ]

    domain = mocaxpy.MocaxDomain(domainValues)

    # MoCaX accuracy parameters
    n_values3 = [10, 8, 4]
    ns3 = mocaxpy.MocaxNs(n_values3)

    # Reference point (must be inside the domain of the function).
    reference_point = [0.0, 0.0, 2.0]

    # Example of point to be evaluated (Note it is within the range specified in function domain).
    x = [0.1, 0.3, 1.7]

    # Construct a MoCaX sliding function object for our wrapped example function using the number of partial functions, their dimensionalities, domain, accuracy parameters and reference point.
    example_mocax3D = mocaxpy.MocaxSliding(wrapped_example_3d_function, num_dimensions_per_partial, domain, ns3, reference_point)

    # Evaluate the MoCaX sliding function object.
    print("Value of MoCaX sliding function object at (" + str(x[0]) + "," + str(x[1]) + "," + str(x[2]) + "): " +
          str(example_mocax3D.eval(x)))

    # Serialize the object to a file.
    example_mocax3D.serialize("serializedMocaxSliding3D.mcx")

    # Deserialize the function from a file.
    deserialized_mocax3d = mocaxpy.MocaxSliding.deserialize("serializedMocaxSliding3D.mcx")
    os.remove("serializedMocaxSliding3D.mcx")

    # Evaluating deserialized object
    print("Value of the deserialized MoCaX sliding function at (" + str(x[0]) + "," + str(x[1]) + "," + str(x[2]) + "): " +
          str(deserialized_mocax3d.eval(x)))


    # Destroy MoCaX objects to free memory.
    del example_mocax3D
    del deserialized_mocax3d

except Exception as e:
    sys.stderr.write("ERROR: " + type(e).__name__ + " - " + str(e) + "\n")
    sys.exit(1)

sys.exit(0)
