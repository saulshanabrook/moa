import moa
import math

add = moa.Kernel('add', 'float, float -> float')
multiply = moa.Kernel('multiply', 'float, float -> float')
sin = moa.Unary0DKernel(lambda a: math.sin(a))

isclose = moa.Kernel('isclose', 'float, float -> bool')
cat = moa.Kernel('cat', 'D * ')

def sin(a):
    return a

def exp(x):
    return x

class Array:
    def __add__(self, other):
        return moa.Omega(moa.Add, moa.Vec(0, 0), self, other)

    def __mul__(self, other):
        return moa.Omega(moa.Multiply, moa.Vec(0, 0), self, other)




def broacast(a, b):
