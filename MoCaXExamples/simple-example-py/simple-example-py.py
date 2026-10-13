"""
MoCaX simple example for Python

"""

from __future__ import print_function

import math
import os
import sys
from ctypes import *

"""
STEP 0: Project configuration:
- The library mocaxc.dll (on Windows) or libmocaxc.so (on Linux) has to be "findable" by Python
            (placing it in a system libraries path is a good solution).
- If MoCaX isn't in PYTHONPATH, add its location using sys.path.append. For instance,
            if mocaxpy is installed in /opt/lib/mocaxpy: sys.path.append("/opt/lib")

"""

# sys.path.append("/opt/lib")

"""
STEP 1: Import MoCaX

"""

import mocaxpy


# Example pre-existing function.
def example_3d_function(x1, x2, x3):
    return math.sin(x1) + math.sin(x2) + math.sin(x3)


"""
 STEP 2: Wrap the pre-existing function so it can be passed to Mocax constructor.
         This simply "maps" each value passed in a list/tuple to its corresponding parameter in the original function,
         and forwards the result of that function.

"""


def wrapped_example_3d_function(x, additionalData):
    return example_3d_function(x[0], x[1], x[2])

# Example pre-existing member function in a class.
# Class to wrap
class ExampleWrapperClass(Structure):
    _fields_ = [
        ("exampleContextData", c_double)
    ]

    def example_3d_function(self, x):
        return math.sin(x[0]) + math.cos(x[1]) + 0.5 * x[2] + self.exampleContextData


# Wrapped class
def mocax_wrapper(x, instancePtr):
    return cast(instancePtr, POINTER(ExampleWrapperClass)).contents.example_3d_function(x)

"""
STEP 3: Specify MoCaX parameters to pass to constructor
"""

try:
    # Number of dimensions
    num_dimensions = 3

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
    n_values2 = [8, 4]
    ns2 = mocaxpy.MocaxNs(n_values2)
    error_threshold = 1e-4

    # Maximum derivative order.
    max_derivative_order = 2

    # Example of point to be evaluated (Note it is within the range specified in function domain).
    x = [0.1, 0.3, 1.7]

    # Example class instance with a context value.
    example_class_instance = ExampleWrapperClass()
    example_class_instance.exampleContextData = 5.0

    """
    STEP 4: Construct a MoCaX object for our wrapped example function using the domain, max. derivative order
                        and accuracy parameters. Below we present different ways of building them.
    """

    example_mocax3D = mocaxpy.Mocax(wrapped_example_3d_function, num_dimensions, domain,
                                       None, ns3, max_derivative_order=max_derivative_order)

    ## Other examples

    #example_mocax3D = mocaxpy.Mocax(wrapped_example_3d_function, num_dimensions, domain,
    #                                  error_threshold, ns2, max_derivative_order=max_derivative_order)
    #example_mocax3D = mocaxpy.Mocax(wrapped_example_3d_function, num_dimensions, domain,
    #                                  error_threshold, None, max_derivative_order=max_derivative_order)

    """
    STEP 4b: It's possible to pass the member function using a wrapper and passing
             an instance through the additional data parameter:
    """

    #example_mocax3D = mocaxpy.Mocax(mocax_wrapper, num_dimensions, domain,
    #                                  None, ns3, max_derivative_order=max_derivative_order,
    #                                  additional_data=cast(pointer(example_class_instance), c_void_p))
    #example_mocax3D = mocaxpy.Mocax(mocax_wrapper, num_dimensions, domain,
    #                                  error_threshold, ns2, max_derivative_order=max_derivative_order,
    #                                  additional_data=cast(pointer(example_class_instance), c_void_p))
    #example_mocax3D = mocaxpy.Mocax(mocax_wrapper, num_dimensions, domain, error_threshold, None,
    #                                  max_derivative_order=max_derivative_order,
    #                                  additional_data=cast(pointer(example_class_instance), c_void_p))

    """
    STEP 4c: For the deferred construction, pass a null function as an argument, retrieve the evaluation points, 
             evaluate them, and pass their values to the function to complete its construction.
    """

    #example_mocax3D = mocaxpy.Mocax(None, num_dimensions, domain, None, ns3, max_derivative_order=max_derivative_order)
    #points = example_mocax3D.get_evaluation_points()
    #values = [];
    #for point in points:
    #    values.append(wrapped_example_3d_function(point, None))
    #example_mocax3D.set_original_function_values(values)


    """
    STEP 5: Evaluate the MoCaX object. Obtain the derivative id corresponding to the order to evaluate.
    """

    derivativeId = example_mocax3D.get_derivative_id([0, 0, 0])
    print("Value of MoCaX object at (" + str(x[0]) + "," + str(x[1]) + "," + str(x[2]) + "): " +
          str(example_mocax3D.eval(x, derivativeId)))

    derivativeId = example_mocax3D.get_derivative_id([0, 1, 0])
    print("Value of the derivative df/dy at (" + str(x[0]) + "," + str(x[1]) + "," + str(x[2]) + "): " +
          str(example_mocax3D.eval(x, derivativeId)))

    derivativeId = example_mocax3D.get_derivative_id([1, 0, 1])
    print("Value of the derivative d^2f/dxdz at (" + str(x[0]) + "," + str(x[1]) + "," + str(x[2]) + "): " +
          str(example_mocax3D.eval(x, derivativeId)))

    # Serialize the object to a file.
    example_mocax3D.serialize("serializedMocax3D.mcx")

    # Deserialize the function from a file.
    deserialized_mocax3d = mocaxpy.Mocax.deserialize("serializedMocax3D.mcx")
    os.remove("serializedMocax3D.mcx")

    # Evaluating deserialized object
    derivativeId = deserialized_mocax3d.get_derivative_id([0, 0, 0])
    print("Value of the deserialized function at (" + str(x[0]) + "," + str(x[1]) + "," + str(x[2]) + "): " +
          str(deserialized_mocax3d.eval(x, derivativeId)))

    derivativeId = deserialized_mocax3d.get_derivative_id([0, 1, 0])
    print("Value of the deserialized derivative df/dy at (" + str(x[0]) + "," + str(x[1]) + "," + str(x[2]) + "): " +
          str(deserialized_mocax3d.eval(x, derivativeId)))

    derivativeId = deserialized_mocax3d.get_derivative_id([1, 0, 1])
    print("Value of the deserialized derivative d^2f/dxdz at (" + str(x[0]) + "," + str(x[1]) + "," + str(x[2]) + "): "+
          str(deserialized_mocax3d.eval(x, derivativeId)))

    # Example of MoCaX arithmetics
    example_class_instance.exampleContextData = 2.3
    example_mocax3d_context_a = mocaxpy.Mocax(mocax_wrapper, num_dimensions, domain, None, ns3,
                                                max_derivative_order=max_derivative_order,
                                                additional_data=cast(pointer(example_class_instance), c_void_p))
    example_class_instance.exampleContextData = 5.7
    example_mocax3d_context_b = mocaxpy.Mocax(mocax_wrapper, num_dimensions, domain, None, ns3,
                                                max_derivative_order=max_derivative_order,
                                                additional_data=cast(pointer(example_class_instance), c_void_p))
    example_mocax3d_sum = example_mocax3d_context_a + example_mocax3d_context_b

    derivativeId = example_mocax3d_context_a.get_derivative_id([0, 0, 0])
    print("Value of MoCaX object (context 2.3) at (" + str(x[0]) + "," + str(x[1]) + "," + str(x[2]) + "): " +
        str(example_mocax3d_context_a.eval(x, derivativeId)))

    derivativeId = example_mocax3d_context_b.get_derivative_id([0, 0, 0])
    print("Value of MoCaX object (context 5.7) at (" + str(x[0]) + "," + str(x[1]) + "," + str(x[2]) + "): " +
          str(example_mocax3d_context_b.eval(x, derivativeId)))

    derivativeId = example_mocax3d_sum.get_derivative_id([0, 0, 0])
    print("Value of the sum of MoCaX objects (contexts 2.3 and 5.7) at (" + str(x[0]) + "," + str(x[1]) + "," +
        str(x[2]) + "): " + str(example_mocax3d_sum.eval(x, derivativeId)))

    """
    STEP 6: Destroy MoCaX objects to free memory.
    """
    del example_mocax3d_context_a
    del example_mocax3d_context_b
    del example_mocax3d_sum
    del example_mocax3D
    del deserialized_mocax3d

except Exception as e:
    sys.stderr.write("ERROR: " + type(e).__name__ + " - " + str(e) + "\n")
    sys.exit(1)

sys.exit(0)
