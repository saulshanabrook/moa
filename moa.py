import matchpy as mp
from functools import partial

r = mp.ManyToOneReplacer()

# Shorcuts
new = mp.Operation.new

unary = lambda n, c: new(n, mp.Arity.unary, c)
binary = lambda n, c: new(n, mp.Arity.binary, c, infix=True)

def add(*args):
    expresions, *constraints, replacement = args
    r.add(mp.ReplacementRule(
        mp.Pattern(expresions, *constraints),
        replacement
    ))


class Array(mp.Symbol):
    def __init__(self, shape, index_fn=None, name=None):
        super().__init__(name)
        self.shape = tuple(shape)
        self.index_fn = index_fn
    
    def __str__(self):
        if self.is_sca:
            if self.index_fn:
                return str(self.as_python)
            if self.name:
                return 'σ_{self.name}'
            return 'σ'

        if self.is_vec:
            if self.index_fn:
                return f'<{" ".join(map(str, self.as_python))}>'
            if self.name:
                return f'{self.name}'
            return 'v'
        
        if self.name:
            return self.name
        return 'a'

    @property
    def is_sca(self):
        return len(self.shape) == 0


    @property
    def is_vec(self):
        return len(self.shape) == 1

    @property
    def as_python(self):
        if not self.index_fn:
            raise NotImplementedError()
        if self.is_sca:
            return self.index_fn()
        return [
            Array(self.shape[1:], partial(self.index_fn, i)).as_python
            for i in range(self.shape[0])
        ]
        

def sca(content):
    return Array([], lambda: content)


def vec(*contents):
    return Array([len(contents)], lambda i: contents[i])

Shape = unary('ρ', 'Shape')
Dimension = unary('δ', 'Dimension')
Take = binary('△', 'Take')
Drop = binary('▽', 'Drop')
Cat = new('++', mp.Arity.variadic, 'Cat', infix=True, one_identity=True, associative=True)
Psi = binary('ψ', 'Psi')
Plus = new('+', mp.Arity.variadic, 'Plus', infix=True, one_identity=True, associative=True, commutative=True)

_ = mp.Wildcard.dot()
e = mp.Wildcard.dot('e')
f = mp.Wildcard.dot('f')
a = mp.Wildcard.symbol('a', Array)
b = mp.Wildcard.symbol('b', Array)

a_is_vec = mp.CustomConstraint(lambda a: a.is_vec)
b_is_vec = mp.CustomConstraint(lambda b: b.is_vec)

add(Shape(a),
    lambda a: vec(*a.shape))
add(Dimension(e),
    lambda e: Psi(vec(0), Shape(Shape(e))))
add(Psi(b, Psi(a, e)),
    a_is_vec,
    b_is_vec,
    lambda a, b, e: Psi(Cat(a, b), e))
add(Psi(a, b),
    a_is_vec,
    mp.CustomConstraint(lambda a, b: len(b.shape) == a.shape[0]),
    lambda a, b: sca(b.index_fn(*a.as_python)))

# add(Shape(Drop(a, f)),
#     a_is_vec,
#     lambda a, f: Minus(Shape(f))

# add(Shape(Cat(Array(a, ), f)),
#     mp.CustomConstraint(
#         lambda e, f: print(r.replace(Drop(sca(1), Shape(f))))
#     ),
#     lambda e, f: Cat(Plus(Take(sca(1), Shape(e)), Take(sca(1), Shape(f))),
#                      Drop(sca(1), Shape(e))))


add(
    Cat(
        Array(Array(Array(d_l), s_l), i_l),
        Array(Array(d_r), s_r), i_r))
    )
)
B = Array([2, 4], name='B')
C = Array([4, 6], name='C')
A = Cat(B, Drop(vec(1, 2), C))
print(A)
print(r.replace(Dimension(A)))


# class Dimension(mp.Operation):
#     name = 'δ'
#     arity = mp.Arity.unary

# class Take(mp.Operation):
#     name = '△'
#     arity = mp.Arity.binary
#     infix = True

# class Drop(mp.Operation):
#     name = '△'
#     arity = mp.Arity.binary
#     infix = True


# class Cat(mp.Operation):
#     name = '++'
#     arity = mp.Arity.binary
#     infix = True

# class Index(mp.Operation):
#     name = 'ψ'
#     arity = mp.Arity.binary
#     infix = True



# # Array = mp.Operation.new('A', mp.Arity.binary, 'Array')




# # class Array(mp.Operation):
# #     name = 'Array'

# #     # def __init__(self, shape, content, gamma, variable_name=None):
# #     #     super()(shape, content, gamma, variable_name=variable_name)
# #     #     self.shape = shape
# #     #     self.content = content
# #     #     self.gamma = gamma
# #     # shape, content, gamma
# #     arity = mp.Arity(min_count=3, fixed_size=True)

# #     def __str__(self):
# #         return self.variable_name or f'A({self.operands[0]})'

#     # @classmethod
#     # def empty(cls):
#     #     return cls('Θ', (0,), tuple())
    
#     # @classmethod
#     # def vector(cls, contents):
#     #     contents = tuple(contents)
#     #     return cls(f'<{" ".join(contents)}>', (len(contents),), contents)

# # class Scalar(mp.Operation):
# #     name = 'sca'
# #     arity = mp.Arity.unary


# # class Vector(mp.Operation):
# #     name = 'vec'
# #     arity = mp.Arity(min_count=1, fixed_size=False)

# #     def __str__(self):
# #         return f'<{" ".join(map(str, self.operands))}>'

# # class Empty(mp.Symbol):
# #     pass

# class Shape(mp.Operation):
#     name = 'ρ'
#     arity = mp.Arity.unary


# class Dimension(mp.Operation):
#     name = 'δ'
#     arity = mp.Arity.unary

# class Take(mp.Operation):
#     name = '△'
#     arity = mp.Arity.binary
#     infix = True

# class Drop(mp.Operation):
#     name = '△'
#     arity = mp.Arity.binary
#     infix = True


# class Cat(mp.Operation):
#     name = '++'
#     arity = mp.Arity.binary
#     infix = True

# class Index(mp.Operation):
#     name = 'ψ'
#     arity = mp.Arity.binary
#     infix = True



# _ = mp.Wildcard.dot()
# x = mp.Wildcard.dot('x')
# y = mp.Wildcard.dot('y')
# xs = mp.Wildcard.star('xs')

# r.add(mp.ReplacementRule(
#     mp.Pattern(Shape(Array(x, _, _))),
#     lambda x: Vector(*x)
# ))

# r.add(mp.ReplacementRule(
#     mp.Pattern(Shape(Vector(xs))),
#     lambda xs: Vector(len(xs))
# ))

# # r.add(mp.ReplacementRule(
# #     mp.Pattern(Dimension(x)),
# #     lambda x: Shape(Shape(x))
# # ))


# r.add(mp.ReplacementRule(
#     mp.Pattern(Shape(Index(x, y))),
#     lambda x, y: return Cat(Shape(y))
# ))

# # r.add(mp.ReplacementRule(
# #     mp.Pattern(Shape(Shape(ξ))),
# #     Vector(Dimension(ξ))
# # ))


# # r.add(mp.ReplacementRule(
# #     mp.Pattern(Shape(Shape(ξ))),
# #     Vector(Dimension(ξ))
# # ))


# # r.add(mp.ReplacementRule(
# #     mp.Pattern(Shape(Shape(ξ))),
# #     Vector(Dimension(ξ))
# # ))

# # cat
# r.add()



# # k = mp.Wildcard.dot('k')
# # A = mp.Wildcard.dot('A')

# # mp.ReplacementRule(
# #     mp.Pattern(
# #         Shape(Take(k, A)),
# #         lambda k, a: Cat(Vector(k), (Drop(1, Shape(A))))
# #     )
# # )



# # a = Array((2, 2), (1, 2, 3, 4), lambda i, j: i * 2 + j, variable_name='hi')
# # print(r.replace(a))
# # print(r.replace(Shape(a)))
# # print(r.replace(Shape(Shape(a))))
# # print(r.replace(Dimension(a)))
# # print(r.replace(Dimension(a)))

# A = Cat(mp.Wildcard.dot('B'), Drop(Array((2,), ))
