# Mela 2.0 Simulator workbench in Python

This project attempts to implement the ideas for Mela 2.0 simulator obtained from the [m2-intro](https://github.com/menu-hanke/m2-intro)
training project, which uses the [m2](https://github.com/menu-hanke/m2) engine for simulator development.

Key points:
* Allow simulation run instructions to be developed in a declarative fashion, utilizing primitives and constraints exposed by a core engine implementation
* Allow calculation models of the simulation to be developed separately from the simulator engine

# Components

## Engine

Execution engine for generated computation tree. To be specified further. Should become dask distributable.

## Operations

A set of forest data manipulation operations. To be specified further. May become aggregated from the _model function library_ project.

## Computation tree generator

A collection of functions which can be considered control flow primitives, and generatives.

### Primitives (runners.py)

#### sequence

A function which evaluates a list of functions in sequence for a single input data item.
Each function should be composable as a chain such that they take a single input argument, which is the return value of the previous function.
How to adhere to this rule is left as a decision for the implementer of the functions perform.

Definining a sequence works as follows:

```python
seq = lambda x: sequence(
    x,  # input data
    operation1,  # x is argument for operation1
    operation2   # return value of operation1 is argument for operation2
)

result = seq(input)  # return value of operation2
```

#### alternatives

A function which evaluates a list of functions separately for a single input data item.
This is the branching primitive allowing to perform different operations on input data.
Each function must operate with argument value of type A, and return a value of type B.
A may equal B.

```python
branch = lambda x: alternatives(
    x,  # input data
    lambda y: operation3(y, 10),  # x is passed the argument y
    lambda z: operation3(z, 20)   # x is passed the argument z
)

result = branch(input)  # array of two result values from operation3 calls above
```

#### follow

A function which evaluates a single function for each given input data item.
This is a branch follow-up primitive for applying one operation for multiple input data items.

```python
input = [10, 20, 30]
follow_up = lambda x: follow(
    x,
    operation4  # called separately for each item in array x
)

result = follow_up(input)  # 3-item array with return values of operation4 as items
```

### Generatives

#### instruction_with_options

Curry a given instruction (function) of interest with a list of alternative call parameters, producing a list of functions readily usable with the alternatives primitive.

```python
def multiply(x, y):
    return x * y

instructions = instruction_with_options(
    multiply, 
    [1, 2, 3]
)
# instructions becomes a list of 1-argument curried functions

branch_example = lambda x: alternatives(
    x,
    *instructions  # pass function references as python *args
)

result = branch_example(10)  # likewise [10, 20, 30]
```
