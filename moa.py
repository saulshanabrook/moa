from typing import (
    TypeVar,
    Callable,
    Generic,
    List,
    Any,
    Tuple,
    Mapping,
    Iterable,
    NamedTuple,
    Type,
    MutableMapping,
    NoReturn,
)
from typing_extensions import Protocol
from itertools import product

T = TypeVar("T", covariant=True)


class Array(Protocol[T]):
    shape: "Array[int]"

    def __getitem__(self, ix: Tuple[int, ...]) -> T:
        ...


class _BaseShape:
    """
    Base <1> vector used for the shape of a shape of a shape, so that we don't infinitely recurse.
    """

    shape: Array[int]

    def __getitem__(self, ix: Tuple[int, ...]) -> int:
        return 1

    def __str__(self):
        return "<1>"

    def __repr__(self):
        return "_BaseShape()"


base_shape = _BaseShape()
base_shape.shape = base_shape


class PythonArray(Generic[T]):
    shape: Array[int]

    def __init__(self, x: Any, shape: Tuple[int, ...]) -> None:
        self.x = x
        if shape == (1,):
            self.shape = base_shape
        else:
            self.shape = PythonArray[int](shape, (len(shape),))

    def __getitem__(self, ix: Tuple[int, ...]) -> T:
        x = self.x
        for i in ix:
            x = x[i]
        return x

    def __str__(self):
        return f"({str(self.shape)} - {str(self.x)})"

    def __repr__(self):
        return f"PythonArray({repr(self.x)}, {repr(self.shape)})"


U = TypeVar("U")
V = TypeVar("V")


def sca(x: U) -> PythonArray[U]:
    return PythonArray[U](x, tuple())


def vec(*xs: U) -> PythonArray[U]:
    return PythonArray[U](list(xs), (len(xs),))


v = PythonArray[int]([0, 1, 2], (3,))

e_2 = PythonArray[int]([[0, 1], [2, 3], [4, 5]], (3, 2))

e_3 = PythonArray[int](
    [[[0, 1], [2, 3]], [[4, 5], [6, 7]], [[8, 9], [10, 11]]], (3, 2, 2)
)

e_4 = PythonArray[int](
    [
        [[[0, 1], [2, 3]], [[4, 5], [6, 7]]],
        [[[8, 9], [10, 11]], [[12, 13], [14, 15]]],
        [[[16, 17], [18, 19]], [[20, 21], [22, 23]]],
    ],
    (3, 2, 2, 2),
)


def equiv(a: Array[T], b: Array[T]) -> bool:
    if a is base_shape and b is base_shape:
        return True
    PointWiseRelation(lambda l, r: l == r, a, b)
    if not equiv(a.shape, b.shape):
        return False
    dims = a.shape.shape[0,]
    shape = tuple(a.shape[d,] for d in range(dims))

    if not shape:
        return a[tuple()] == b[tuple()]
    for xs in product(*map(range, shape)):
        if a[xs] != b[xs]:
            return False
    return True


class _Empty:
    shape: Array[int] = vec(0)

    def __getitem__(self, ix: Tuple[int, ...]) -> NoReturn:
        raise TypeError()


empty = _Empty()


class Scalar:
    shape: Array[int] = empty


class Dimension(Scalar):
    def __init__(self, x: Array[T]) -> None:
        self.x = x
        self.d = x.shape.shape[0,]

    def __getitem__(self, ix: Tuple[int, ...]) -> int:
        assert not ix
        return self.d

    def __str__(self):
        return f"δ{str(self.x)}"

    def __repr__(self):
        return f"Dimension({repr(self.x)})"


assert equiv(Dimension(sca("hi")), sca(0))

assert equiv(Dimension(v), sca(1))
assert not equiv(Dimension(v), sca(2))
assert equiv(Dimension(e_2), sca(2))
assert equiv(Dimension(e_3), sca(3))
assert equiv(Dimension(e_4), sca(4))

assert equiv(v.shape, vec(3))
assert equiv(e_2.shape, vec(3, 2))
assert equiv(e_3.shape, vec(3, 2, 2))
assert equiv(e_4.shape, vec(3, 2, 2, 2))


def is_scalar(a: Array[T]) -> bool:
    return equiv(Dimension(a), sca(0))


def is_vector(a: Array[T]) -> bool:
    return equiv(Dimension(a), sca(1))


class VectorOfScalar(Generic[T]):
    shape: Array[int] = base_shape

    def __init__(self, x: Array[T]) -> None:
        assert is_scalar(x)
        self.x = x

    def __getitem__(self, ix: Tuple[int, ...]) -> T:
        assert ix == (0,)
        return self.x[tuple()]


class Psi(Scalar, Generic[T]):
    def __init__(self, i: Array[int], e: Array[T]) -> None:
        assert is_vector(i)

        n = Dimension(e)
        assert equiv(i.shape, VectorOfScalar(n))

        # 2.00
        self.idx: List[int] = []
        for j in range(n[tuple()]):
            i_ = i[j,]
            assert 0 <= i_ and i_ <= e.shape[j,]
            self.idx.append(i_)

        self.i, self.e = i, e

    def __getitem__(self, ix: Tuple[int, ...]) -> T:
        assert not ix
        return self.e[tuple(self.idx)]

    def __str__(self):
        return f"{str(self.i)}ψ{str(self.e)}"


assert equiv(Psi(vec(0), v), sca(0))
assert equiv(Psi(vec(1), v), sca(1))

assert equiv(Psi(vec(), sca("hi")), sca("hi"))


class PointWiseRelation(Generic[T, U, V]):
    def __init__(self, rel: Callable[[T, U], V], l: Array[T], r: Array[U]) -> None:
        assert equiv(l.shape, r.shape)
        self.shape = l.shape
        self.rel = rel
        self.l = l
        self.r = r

    def __getitem__(self, ix: Tuple[int, ...]) -> V:
        return self.rel(self.l[ix], self.r[ix])


def plus(a, b):
    return a + b


assert equiv(PointWiseRelation(plus, v, v), PythonArray[int]([0, 2, 4], (3,)))


class ScalarLeftExtensionRelation(Generic[T, U, V]):
    def __init__(self, rel: Callable[[T, U], V], l: Array[T], r: Array[U]) -> None:
        assert is_scalar(l)
        self.shape = r.shape
        self.rel = rel
        self.l = l
        self.r = r

    def __getitem__(self, ix: Tuple[int, ...]) -> V:
        return self.rel(self.l[tuple()], self.r[ix])


assert equiv(
    ScalarLeftExtensionRelation(plus, sca(1), v), PythonArray[int]([1, 2, 3], (3,))
)
assert not equiv(
    ScalarLeftExtensionRelation(plus, sca(2), v), PythonArray[int]([1, 2, 3], (3,))
)

print(ScalarLeftExtensionRelation(plus, sca(2), v)[0,])


class ScalarRightExtensionRelation(Generic[T, U, V]):
    def __init__(self, rel: Callable[[T, U], V], l: Array[T], r: Array[U]) -> None:
        assert is_scalar(r)
        self.shape = l.shape
        self.rel = rel
        self.l = l
        self.r = r

    def __getitem__(self, ix: Tuple[int, ...]) -> V:
        return self.rel(self.l[ix], self.r[tuple()])


class Ravel(Generic[T]):
    shape: Array[int]

    def __init__(self, e: Array[T]) -> None:
        if is_scalar(e):
            self.x = x
            self.shape = base_shape
            return
        # if is_vector(e):

        # self.shape =


# class Cat(Generic[T]):
#     def __init__(self, a: Array[T], b: Array[T]) -> None:
#         a_first, *a_rest = a.shape
#         b_first, *b_rest = b.shape
#         assert a_rest == b_rest
#         self.shape = [a_first + b_first] + a_rest
#         self._a_first = a_first
#         self.a, self.b = a, b

#         def indexing(first, *rest):
#             if first < self._a_first:
#                 return a.indexing(first, *rest)
#             return b.indexing(first - self._a_first, *rest)

#     def __str__(self):
#         return f'{self.a} ++ {self.b}'


# a = PythonArray[int]([[1, 2], [2, 4], [3, 4]], [3])
# b = PythonArray[float]([[4, 2], [2, 3]], [2])

# # this will fail type checking :)
# #c = Cat(a, b)

# b = PythonArray[int]([[4, 2], [2, 3]], [2])
# c = Cat(a, b)

# class Take(Array):
#     def __init__(self, a: Array[T], b: Array[T]) -> None:
#         self.a, self.b = a, b
#         a_first, *a_rest = a.shape
#         b_first, *b_rest = b.shape
#         assert a_rest == b_rest
#         self.shape = [a_first + b_first] + a_rest
#         self._a_first = a_first

#         def indexing(first, *rest):
#             if first < self._a_first:
#                 return a.indexing(first, *rest)
#             return b.indexing(first - self._a_first, *rest)

#     def __str__(self):
#         return f'{self.a} ++ {self.b}'

# # def cat(a: Array[T], b: Array[T]) -> Array[T]:
# #     a_first, a_rest = a.shape
# #     b_first, b_rest = b.shape
# #     assert a_rest == b_rest

# #     def indexing(first, *rest):
# #         if first < a_first:
# #             return a.indexing(first, *rest)
# #         return b.indexing(first - a_first, *rest)

# #     return Array(indexing, [a_first + b_first] + a_rest)


# # Shape = unary('ρ', 'Shape')
# # Dimension = unary('δ', 'Dimension')
# # Take = binary('△', 'Take')
# # Drop = binary('▽', 'Drop')
# # Cat = new('++', mp.Arity.variadic, 'Cat', infix=True, one_identity=True, associative=True)
# # Psi = binary('ψ', 'Psi')
# # Plus = new('+', mp.Arity.variadic, 'Plus', infix=True, one_identity=True, associative=True, commutative=True)

# # _ = mp.Wildcard.dot()
# # e = mp.Wildcard.dot('e')
# # f = mp.Wildcard.dot('f')
# # a = mp.Wildcard.symbol('a', Array)
# # b = mp.Wildcard.symbol('b', Array)

# # a_is_vec = mp.CustomConstraint(lambda a: a.is_vec)
# # b_is_vec = mp.CustomConstraint(lambda b: b.is_vec)
