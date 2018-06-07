# Mathematics of Arrays (`moa`)

This repo is where I am starting to explore how the Mathematics of Arrays could be helpful
in Python. 

I see this as being a multiple level abstraction. At the bottom we have a concept of 
representing arrays and computations on them declaratively in an algebra.

## Example Lower API 

Here are some examples of how this API should work:

```python
B = Array([2, 4])
# B has shape (2, 4) but we don't know/care how it's represented in memory
C = Array([4, 6])

# below, vec(1, 2) still declares an array (of shape (2,)), but
# it is different than the above declerations because we want to be able to index
# it at "compile time" i.e. when we compose the expression. 
A = Cat(B, Drop(vec(1, 2), C))
# We can infer that A has shape (5, 4)
# We also know that to index (i, j) < (2, 4) we index into B
# and for index (i, j) > (2, 4) we index into A.
```

The `Omega` operator is higher order, and is a way to apply unary or binary
functions to any inner shape of a larger array:


```python
A = Array([2, 4, 6])

B = Omega(Increment, vec(0), A)
# Let's assume we know the Increment operator takes a 0D array (scalar)
# and returns another 0D array.
# Then we know B has shape (2, 4, 6). The `vec(0)` argument to omega
# is a vector with one element that corresponds to how many dimensions
# the function should oeprate on. 
# We also know that indexing into B with (i, j , k) gives inc(A[i, j, k]).

C = Omega(Sum, vec(1), A)
# Let's say this Sum operator takes some input of shape (N,) and return an output
# of shape (,), i.e. it takes in a vector and returns a scalar. Then we know
# C has shape (2, 4).
# We also know that indexing into C with (i, j) gives sum(A[i, j]).


D = Omega(Reverse, vec(1), A)
# Reverse takes in a shape (N,) and returns a shape (N,) so we know D has
# shape (2, 4, 6)
# To index (i, j, k) into D we do indexing A[i, j, (6-k-1)].
# We can get this by combining the indexing transformation of reverse with
# omega applying this to the last dimension.
# So what this means is we could then take the first two rows of the last dimension:
E = Omega(Drop, vec(0, 1), Vec(2), D)
# and we would know how to index into it, without actually creating any temporary reversed arrays
# this shows the binary form of Omega, because we define Drop here as a binary operation
# that takes in a scalar saying how many indices to drop and then the vector to drop them from.
```

Omega is also defined for binary operations:

```python
A = Array([2, 4, 6])
B = Array([2, 4, 6])
C = Omega(Add, vec(0, 0), A, B)
# The `vec(0, 0)` says to take 0D from the left array (A) and 0D from the right array (B)

# If one arrays is smaller, that works too:
A = Array([2, 4, 6])
B = Array([6])
C = Omega(Add, vec(0, 0), A, B)

# What if we wanna add the innermost scalar from the right array to each vector on the left array?
# we can do this too, as long as we can infer the output dimensions for Sum based on the input dimensions
A = Array([2, 4, 6])
B = Array([4, 6, 7])
D = Omega(Add, vec(0, 1), A, B)
# D has shape (2, 4, 6, 7)
```


### Implementation
I have been using matchpy (https://github.com/HPAC/matchpy/) to begin implementing something like this.
I am finding doing the shape inference pretty doable, but I am unsure how to represent the resulting
index math. I think I need to settle on something where I can say like "The index for these two 
arrays catted together indexes into the left array for indices < X and into the right for indices > X". And also for things that reverse that do math on the index pointer. So it seems like I need
to actually put this kind of index algebra, with conditionals in the actual representation. But that
seems complicated and I am not sure where I would need to stop with that, so I have held back till now.

