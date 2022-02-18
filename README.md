# Mela 2.0 simulator

Mela 2.0 simulator is a Python based forest growth and maintenance operation simulator developed in Natural Resources Institute Finland.
It is meant to be the modernized version of the older Fortran based MELA simulator program developed in  since the 1980s.

The simulator is a stepwise branching state simulator operating upon forest state data.
The state data is manipulated by **simulator operations**, which in turn rely upon scientific **model function chains**.
The branching model for simulator operations is declared in a human-readable YAML format or directly by functional declaration.
This declaration is used to generate a **step tree** describing the full branching possibilities for the simulation.
Prepared **operation chains** are generated from the step tree and are run with the simulator engine.

## Layout

This code project is divided into three python packages.

| package  | description                                                                |
|----------|----------------------------------------------------------------------------|
| app      | Development application entry point. Side-effectful program logic.         |
| sim      | Functionality for creating, preparing and executing a simulator run.       |
| forestry | Operations and computational models for the forest development simulation. |

## Requirements

Python 3.9 is the current target platform.
We aim to keep compatibility down to Python 3.7.
The `pip` utility is assumed for dependency management.

## Usage

Preliminarily, ensure that the project's library dependencies are installed and pytest is available for unit tests.

```
pip install --user -r requirements.txt
pip install --user pytest
```

To run the application, run in the project root

```
python -m app.main
```

In this phase of development, the program assumes files two files to exist in working directory.

* `input.json` is a forest data file used for forestry simulation. It is sourced from vmi-data-converter and adheres to MELA RSD specification for properties of forest stands and reference trees. 
* `control.yaml` is the declared structure for a simulation run.

To run unit test suites, run in the project root

```
python -m pytest
```

You can also use python internal module unittest

```
python -m unittest <test suite module.class path>
```

# Simulation control

A simulation run is declared in the YAML file `control.yaml`.
The file contains two significant structures for functionality.
The structure will be expanded to allow parameters and constraints declaration for specific operations.

1. Simulation time step parameters in the object `simulation_params`
   1. `initial_step_time` is the integer point of time for the simulation's first cycle
   2. `step_time_interval` is the integer amount of time between each simulation cycle
   3. `final_step_time` is the integer point of time for the simulations's last cycle
2. List of `simulation_events`, where each object represents a single set of operations and a set of time points for those operations to be run.
   1. `time_points` is a list of integers which assign this set of operations to simulation time points
   2. `generators` is a list of chained generator functions (see section on step generators)
      1. `sequence` a list of operations to be executed as a chain
      2. `alternatives` a list of operations which represent alternative branches

The following example declares a simulation, which runs four event cycles at time points 0, 5, 10 and 15.

* At time point 0, `reporting` of the simulation state is done.
* At time point 5, the `grow` operation is done on the simulation state and the simulation is branched by 2.
One branch does not modify the forest state data with `do_nothing`, the other performs a `thinning` operation on the forest state data.
* At time point 10, the 2 branches from time point 5 are extended both with a `grow` operation, then branched again with `do_nothing` and `thinning` operations, resulting in 4 branches.
* At time point 15, `reporting` is done on the 4 individual state branches.

```yaml
simulation_params:
  initial_step_time: 0
  step_time_interval: 5
  final_step_time: 15

simulation_events:
  # we describe here objects with schedule for which time points they are active
  - time_points: [5, 10]
    generators:
      - sequence:          
        - grow
      - alternatives:
        - do_nothing
        - thinning
  - time_points: [0, 15]
    generators:
      - sequence:
        - reporting
```

## Generators

The three important concepts in the `sim.generators` module are **operations**, **operation processor**, **step tree** and **generators**.

### Operation

An operation is a function whose only responsibility is the simulation state manipulation.
For the purposes of the simulator, the operation is a partially applied function from the domain package (forestry) such that it will take only one argument, the simulation state.
They are produced as lambda functions based on the `control.yaml` declaration.

As an example, a single operation such as `grow` would receive a single argument of type `ForestStand` upon which it operates and finally returns a `ForestStand` for the modified/new state. 

### Operation processor

A processor is a two parameter function which handles running prepared operations. 
The parameters are an `OperationPayload` instance and an operation function reference.
The `OperationPayload` is primarily the container for simulation state data, along with a record of simulation run history and operation run constraints.
Responsibilities of a processor function are as follows:

* Determine if run constraints apply to the operation to be run. Abort and raise an exception if so.
* Execute the operation function with simulation state data.
* Create a record of the run in simulation run history.
* Pack results as a new `OperationPayload` and return it.

Processor functions are produced as lambda functions based on the `control.yaml` declaration.

### The step tree

The step tree is a tree data structure where each individual node represents a prepared simulation processor.
It is generated based on the `control.yaml` declaration. Unique operation chains are generated based on the step tree.

### Generators

`sequence` and `alternatives` are functions which produce `Step` instances for given input functions and as successors of previous `Step` instances.
For the simulation purposes, these input functions are the prepared processors (see above), but the implementation literally does not care what these functions are.
Sequences are linear chains of steps.
Alternatives are branching steps.
The generators are chainable such that they can expand the step tree in formation based on the results of earlier generator results. 

Step instances are generated and bound to earlier steps (parents) as successors (children).
`compose` function executes the `sequence` and `alternatives` to build the complete simulation step tree.

The `generators_from_declaration` function prepares the generator functions from the `control.yaml` structure, preparing necessary processor and operation functions within.

## The domain

The `forestry` package contains the data structure and operations necessary to represent the simulation state data and operations acting upon that data.

### State data

The class `ForestStand` and the `ReferenceTree` it refers to.
A single `ForestStand` instance fully represents a simulation state.

### Operations

Operations are functions which take two arguments

* `ForestStand` instance
* Python `dict` containing parameters for this operation

By convention (since Python as a language does not allow us to properly enforce this), these functions must remain pure and not trigger side-effectful program logic.
As a design consideration, if it appears that a function needs parameters that can't be supplied by the `control.yaml` and parameters dict, this must be addressed by other development.

## The engine

`sim.runners` module has two functions of interest:

* `evaluate_sequence` executes a prepared chain of functions (from the step tree), returning the final simulated stated or raising an execption upon any failure.
* `run_chains_iteratively` is a simple iterator for given chain of prepared operations (from the step tree)

Note that this package is a simple run-testing implementation.
In the future we wish to expand upon this to allow for distributed run scenarios using Dask.

# Additional information

## Notes for domain developers

Your primary responsibility is to write the functionality that acts upon simulation state data based on parameters of your choosing.
For the forestry case, the state data is a single instance of a ForestStand, which always has a member list of ReferenceTree instances.

You write an operation function, which is an entry point to your work.

* It shall take in a single argument, a ForestStand instance.
* It shall return a ForestStand instance, or it shall raise an Exception when the operation can not complete its work for any reason.

The operation function can internally be whatever you require it to be.
Write out as many other functions you need for the underlying scientific models.

Keep your work functionally pure.
This means that the implementations must never access input and output (API calls, file access, etc.).
This also means that all data must be passed as function arguments, return values and exceptions.
Do not use shared memory outside of the scope of the functions you write.
Python does not allow us to be strict about this, so it is up to you!
**Being strict about it is crucial for producing safe, testable, provable and deterministic implementations.**

Implement unit tests for functions that you write.
Unit tests allow you to develop your functions completely independently from the rest of the system.
You do not need to run the simulation to test your work, but use a test to ensure that your function returns what is expected and behaves like it's intended.

* Coordinate with simulator developers when some need arises that you feel can not be addressed with the model described above.
A solution that doesn't require breaking functional purity can most certainly be found by developing the simulator and operations interface structure.
* Coordinate with other developers when the work you do and models you write can be shared with other operations.
* Coordinate with simulator creators about the parameters names and structures that can be passed from control.yaml file.

## Notes for simulation creators

Use the control.yaml structure declaration to control the simulation structure, domain operations and parameters that are to be used.
