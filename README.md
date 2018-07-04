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
