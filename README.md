# Mathematics of Arrays (`moa`)
This repo is where I am starting to explore how the Mathematics of Arrays could be helpful
in Python.

I see this as being a multiple level abstraction. At the bottom we have a concept of
representing arrays and computations on them declaratively in an algebra.


the `moa.py` file is implementing [Lenore Mullin's thesis](https://paperpile.com/app/p/5de098dd-606d-0124-a25d-db5309f99394).

If you follow allong with that, you should be able to follow the code better. I am trying to go linearly.

I am using some new Python typing features here, but they might all be not helpful in the end. They get me somewhere, but I am not sure
if it's far enough.

The goal with that file is that I should be able to create Tensorflor or TVM or Dask arrays that fulfill the `Array` protocol. Then I should
be able to use all the same function, like indexing, concat, etc on them. Obviously operations will have to be different since the inner elements are the same.
But the API should be designed in a way that is agnostic not only to memory layout but computational abstraction. So maybe the operations are building up a tensorflow graph
and maybe they are just calling native Python.


## Cherry Picked Quotes
*...from Python's MATRIX sig mailing list.*

As the early Python community started thinking about how to add arrays/matrices to the language, notions from APL/J were frequently referenced as inspiration.
But not all the early ideas were implemented as generally as they could be. Once the first C matrix library was implemented, the mailing list seemed to have focused on that.
I want to see what different approaches were articulated in these first posts, to see how they can help us today.

> **Mapping operations**
>
> Recent newsgroup discussions have offered some convincing arguments for
> treating a matrix as a mapping type where sequences of ints are used as
> the keys.  The sequence must be of length less than or equal to the numer
> of dimensions in the matrix.  Each element of the sequence is either an
> integer or a sequence.  If it is an integer, it returns the corresponding
> element for that dimension, if it is a sequence then it returns all of the
> elements given in the sequence.

- [Jim Hugunin](https://mail.python.org/pipermail/matrix-sig/1995-August/000002.html)


Can we simplify this? What if we don't allow sequences... Then we get MoA.


> In general, I have the impression that we get too much lost in
implementational details. Let's first define arrays as an abstract
data type in terms of the operations allowed on it from a
user's point of view and *then* worry about implementational
details.

- [Konrad Hinsen](https://mail.python.org/pipermail/matrix-sig/1995-September/000034.html)

Exactly! We have never nailed this down. Just this week a high level NEP on the numpy mailing list
explicitly punted on defining an explicit array interface, because it's just so huge at this point!

> Matter of fact, might be a good idea to make the
> matrix a general container like lists are now, so you can store, say, a
> tuple representing a complex number in there? As it stands, with these
> restrictions you can forget it. However, this makes it slightly more work
> for those wonderful Fortran library routines.

- [Graham Hughes](https://mail.python.org/pipermail/matrix-sig/1995-September/000004.html)

There are ABC/types for lists, iterables, etc. How do we get one for arrays?

> Before jumping into technical details, it might be a good idea to
define what we are aiming at. As it has already become clear from the
dicussion, matrices are used in two different (but not entirely
distinct) ways:
>
> 1) in linear algebra applications
> 2) as containers of values that are structured as tables
>
> In linear algebra, one needs mainly one- and two-dimensional matrices
> of real or complex numbers. Important operations are addition and
> multiplication, factorization, inversion, eigenvalues etc. There are
> efficient Fortran and C libraries for these operations, so what is
> needed is a suitable representation in Python that allows interfacing
> to these libraries and some convenient way of accessing them, i.e.
> operators (+ - *, maybe / for scalar division) and tons of operations
> that are best packaged into a matrix class.
>
> The second application is just as important (in my view) and much more
> complex. As APLers know, there are lots of useful operations on tables
> of values, which can be of any dimension and contain any data type,
> although the numerical are the most important ones (Python already
> provides good string handling). It makes sense to have all
> mathematical functions and operators acting by default elementwise,
> including of course multiplication, but also user-defined functions.
> Basically arrays would be extensions of numerical scalars, the
> latter becoming arrays of rank zero. The by far most elegant and
> powerful array concept I know of is the one implemented in J, a
> relatively new language that can be regarded as an improved version
> of APL. I certainly don't want to take over J's other features, but
> its concept of array and operator ranks is extremely useful. I'll
> give a short description below.
>
> But first let's see how the two applications can be reconciled in
> a single implementation. Many of the linear algebra operations
> make sense only for two-dimensional matrices, but the J approach
> of operator rank takes care of the nicely. And even without
> that approach, this would only mean some more error checking for
> such operations. The only point of conflict is the implementation
> of multiplication (there is no difference for addition and
> subtraction). Linear-algebra style matrix multiplication is
> regarded as an inner product with addition and multiplication
> operations from an APL/J point of view, so it is available,
> but arguably not in the most convenient form. On the other hand,
> once the * symbol means matrix multiplication, the total
> general structure of elementwise operations is ruined.

- [Konrad Hinsen](https://mail.python.org/pipermail/matrix-sig/1995-September/000008.html)

I guess the question of whether 2) can be represented effectively as a subset of 1), is still relevent,
especially if 1) includes other things based on fixed dimension arrays, but more like JSON/Parquet/nested data.

> Jim Fulton proposes an elegant indexing syntax for matrix objects
> which doesn't require any changes to the language:
>
> 	M[i][j]
>
> references the element at column i and row j (or was that column j and
> row i?  Never mind...).
>
> This nicely generalizes to slicing, so you can write:
>
> 	M[i][j1:j2]
>
> meaning the column vector at column i with row indices j1...j2-1.
>
> Unfortunately, the analogous expression for a row vector won't work:
>
> 	M[i1:i2][j]
>
> The reason for this is that it works by interpreting M as a sequence
> of columns (and it's all evaluated one thing at a time -- M[i][j]
> means (M[i])[j], and so on).  M[i] is column i, so M[i][j] is the
> element at row j thereof.  But slice semantics imply that of M is a
> sequence of X'es, then M[i1:j1] is still a sequence of X'es -- just
> shorter.  So M[p:q][r] is really the same as M[p+r] (assuming r<q-p).
>
>
> One way out of this is to adopt the syntax
>
> 	M[i, j]
>
> for simple indexing.  This would require only a minor tweaking of the
> grammar I believe.  This could be extended to support
>
> 	M[i1:i2, j]
> 	M[i1:i2, j1:j2]
> 	M[i, j1:j2]
>
> (and of course higher-dimensional equivalents).
>
> [...]
>
> - Now we have multidimensional sequence types, should be have a
> multidimensional equivalent of len()?  Some ideas:
>
>   - len(a, i) would return a's length in dimension i; len(a, i) == len(a)
>
>   - dim(a) (or rank(a)?) would return the number of dimensions
>
>   - shape(a) would return a tuple giving a's dimensions, e.g. for a
>   3x4 matrix it would return (3, 4), and for a one-dimensional
>   sequence such as a string or list, it would return a singleton
>   tuple: (len(a),).

[Guido van Rossum](https://mail.python.org/pipermail/matrix-sig/1995-September/000042.html)



The range sequence multi indexing thing is still a bit odd today. By odd, I mean that, according to MoA `<a, b...> index C == <b> index (<a> index C)`. This makes sense to me. It's a nice fundamental rule about indexing. It is defined recursively, that indexing always traversing into the array in this manner. However, if we allow ranges for indexing, then this is no longer true. Because
`C[j:k, i] != C[j:k][i]`. Or if we do allow this syntax, then they SHOULD be equal. Otherwise,
let's now allow range indexing. Obviously, you have to be able to achieve what you can with range indexing, but it would be nice to do this in terms of the simpler indexing algebra.


> Actually, I feel that for a multidimensional sequence, len() should behave
> the same way it always had. Allowing for greater dimensions will give
> greater flexibility, yes, but it may also break `older' functions that
> assume that what's being passed to them is a 2D array. This is mainly
> because len() is defined to return an integer, sadly, and not one of our
> magic sequences; if it did return the magic sequence, we would be able to
> totally ignore how many dimensions we have.


i.e. the array interface should have a shape that returns a an array.

> I like the general idea of going with APL/J style multidimensional
objects.
>
> [...]
>
> I have one idea I would like to float by this group.  How about
separating out the representation and the structure?
>
> I believe I've seen C/Fortran matrix packages that made quite good use
of this.  The representation would be a simple 1-dimensional sequence.
You'd normally not see or use this, but it would be there if you
needed access to it (e.g. for passing to C/Fortran code).
>
> There's a simple way to map an index in an N-dim array into an index
in the 1-dim representation array (Fortran compilers use it all the
time :-).
>
> To make efficient use of this, I propose that slicing and indexing, as
long as they return an object of rank >= 1, return an object that
points into the same representation sequence.
>
> [...]
>
> If we do things just right, it may be possible to pass in the sequence
to be used as the representation -- it could be a Python list, tuple
or array (from the array module).

- [Guido van Rossum](https://mail.python.org/pipermail/matrix-sig/1995-September/000068.html)

Yes! We should be able to use any sequence/structure as the array object!

> If we extend this rule to N-dimensional indexing, a[sequence], for
> some sequence of integers whose elements are i, j, k, ..., should be
> equivalent to a[i][j][k]..., and we can't make a[(1,2,3)] mean
> a[1][2][3] while at the same time interpreting a[[1,2,3]] as a[1:4].
> (Sooner or later, you'll be passing a vector to the index.  Then the
> question will arise, should this have the same meaning as a tuple or
> as a list.  It's better if they all three mean the same.)
>
> Instead of supporting a[[2,3,5]] to select elements 2, 3 and 5 from a,
> I would propose to use filter() or a multi-dimensional extension
> thereof if you want to access selected subarrays.  Or perhaps just a
> method a.select() where each argument is either an index (meaning a
> reduction of dimensionality in this dimension by picking just the
> sub-array with this index) or a sequence of indices (meaning selecting
> the set of sub-arrays with the indices in the sequence).

Yep, this is what I said above. I concur.

> I like this idea because the list or array containing the
> representation may already be available in memory -- so why copy it?
> Also by using an immutable underlying sequence (e.g. a tuple) it is
> easy to create immutable N-dimensional arrays without the need for a
> read-only flag.   Finally it makes it possible to use a representation
> where the actual values are stored in disk and only fetched into
> memory when needed, using a cache -- this way you can implement your
> own virtual memory system, persistent matrices, etc.
>
> There could still be a "default" underlying representation that is
> highly optimized and that the indexing object knows about, for speedier
> access.

Exactly. We want to make the representation abstract, so it could be in dask, or anywhere else.

- [Guido van Rossum](https://mail.python.org/pipermail/matrix-sig/1995-September/000071.html)
