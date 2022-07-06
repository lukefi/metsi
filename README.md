# Mela 2.0 simulator

Mela 2.0 simulator is a Python based forest growth and maintenance operation simulator developed in Natural Resources Institute Finland.
It is a part of a software collection replacing the older Fortran based MELA simulator program developed since the 1980s.

The simulator is a stepwise branching state simulator operating upon forest state data.
The state data is manipulated by **simulator operations**, which in turn rely upon scientific **model function chains**.
The branching model for simulator operations is declared in a human-readable YAML format or directly by functional declaration.
This declaration is used to generate a **step tree** describing the full branching possibilities for the simulation.
Prepared **operation chains** are generated from the step tree and are run with the simulator engine.

## Getting started

To get started:

* Install Python 3.10 for your platform. 
* Install git for your platform.
* Ensure that the commands `python`, `pip` and `git` are available in CLI.
* Initialize the project with the commands below.

```
git clone https://github.com/menu-hanke/sim-workbench
cd sim-workbench
pip install -r requirements.txt
```

### Development

To partake in development and to get access to closed source projects of `menu-hanke`, create a GitHub account and request access. 

### R (optional)

To be able to use forestry operations depending on R modules

* Install R runtime version >=4.1 for your platform.
* Ensure that the `R` command is available in CLI.
* Install the `rpy2` Python module with the commands below.

```
pip install rpy2
```

### Motti (optional)

To be able to use forestry operations depending on the `pymotti` library

* Obtain GitHub access to https://github.com/menu-hanke/pymotti repository from menu-hanke organisation. Motti is not an open source implementation.
* Clone and install the `pymotti` Python module as a locally sourced package with the commands below 

```
git clone https://github.com/menu-hanke/pymotti
pip install -e ./pymotti
```

## Project layout

This code project is divided into following python packages.

| package  | description                                             |
|----------|---------------------------------------------------------|
| app      | Application entry points. Side-effectful program logic. |
| sim      | Simulator engine.                                       |
| forestry | Operations for the forest development simulation.       |
| tests    | Unit test suites for above packages.                    |

The `forestry` package depends on external libraries maintained by this project. These are

| package                                                 | description                                                               |
|---------------------------------------------------------|---------------------------------------------------------------------------|
| https://github.com/menu-hanke/forest-data-model         | Main data classes and related utilities for forestry domain operations    |
| https://github.com/menu-hanke/forestry-function-library | Implementations of forest data state manipulation and related computation |
| https://github.com/menu-hanke/pymotti (private)         | Python implementation of the Motti forest growth models                   |

Other mandatory dependencies for this project are listed in `requirements.txt`.
Optional dependencies are listed in `requirements-optional.txt`.
The `requirements-test.txt` may list dependencies needed by the unit testing scope in `tests`
Dependencies may be installed with the `pip` utility as follows

```
pip install -r requirements.txt
```

## Applications

The project contains two application entry points. These are the `app/simulator.py` and the `app/post_processing.py`.
The operational details about these applications are documented separately.

## Usage of the simulator application

The simulator application depends upon

1. A source data file which contains a list of `ForestStand` entities according to the `forest-data-model` package. The file may currently be a JSON file or a Python native serialization file (pickle).
These source files are typically produced from VMI or SMK (Finnish Forest Center) source data files with the [vmi-data-converter](https://github.com/menu-hanke/vmi-data-converter) application.
2. A YAML file which is used as a configuration for a simulator run. See `control.yaml` for an example. See section about Simulation control for further information.

There are several example input files in the project `data` directory.
These are data files with a list of ForestStand objects containing a list of RefenceTree objects generated from TreeStratum objects with Weibull distribution.

! Note that the JSON file input is currently unusable for enumeration types in the data model due to https://github.com/menu-hanke/forest-data-model/issues/30 so use the pickle file for the time being.

See table below for a quick reference of forestry operations usable in control.yaml.

| operation           | description                                                                                    | source                      | model library             |
|---------------------|------------------------------------------------------------------------------------------------|-----------------------------|---------------------------|
| do_nothing          | This operation is no-op utility operation to simulate rest                                     |                             | native                    |
| grow_acta           | A simple ReferenceTree diameter and height growth operation                                    | Acta Forestalia Fennica 163 | forestry-function-library |
| grow_motti          | A ReferenceTree growth operation with death and birth models. Requires `pymotti`.              | Luke Motti group            | pymotti                   |
| first_thinning      | An operation reducing the stem count of ReferenceTrees as a first thinning for a forest        | Reijo Mykkänen              | native                    |
| thinning_from_below | An operation reducing the stem count of ReferenceTrees weighing small trees before large trees | Reijo Mykkänen              | native                    |
| thinning_from_above | An operation reducing the stem count of ReferenceTrees weighing large trees before small trees | Reijo Mykkänen              | native                    |
| even_thinning       | An operation reducing the stem count of ReferenceTrees evenly regardless of tree size          | Reijo Mykkänen              | native                    |
| report_volume       | Collect tree volume data from ForestStand state                                                |                             | native                    |
| report_thinning     | Collect thinning operation details from data accrued from thinning operations                  |                             | native                    |
| cross_cut           | Perform cross cut operation to compute aggregated details                                      | Annika Kangas               | native (R)                |

To run the simulator application, run the following command in the project root.
The created output file contains all generated variants for all computation units (ForestStand) along with aggregated data.
The output file is usable as input for the `app/post_processing.py` application.

```
python -m app.simulator data/VMI12_data.pickle control.yaml VMI12_simulated.pickle
```

Use the following command to output simulator application help menu
```
python -m app.simulator --help
```

## Usage of the post processing application

To run the post processing application, run in the project root

```
python -m app.post_processing input.pickle pp_control.yaml output.pickle
```

* `input.pickle` The result file of a simulator run.
* `pp_control.yaml` is the declaration of post processing function chain.
* `output.pickle` is the output file for post processed results

## Testing

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
2. Operaton run constrains in the object `run_constraints`
3. Operation parameters in the object `operation_params`
4. List of `simulation_events`, where each object represents a single set of operations and a set of time points for those operations to be run.
   1. `time_points` is a list of integers which assign this set of operations to simulation time points
   2. `generators` is a list of chained generator functions (see section on step generators)
      1. `sequence` a list of operations to be executed as a chain
      2. `alternatives` a list of operations which represent alternative branches
5. Preprocessing operations can be passed as a list of strings under `preprocessing_operations`, and their (optional) arguments under `preprocessing_params` as key-value pairs. 

The following example declares a simulation, which runs four event cycles at time points 0, 5, 10 and 15.
Images below describe the simulation as a step tree, and further as the computation chains that are generated from the tree.

* At time point 0, `reporting` of the simulation state is done.
* At time point 5, the `grow` operation is done on the simulation state and the simulation is branched by 2.
One branch does not modify the forest state data with `do_nothing`, the other performs a `thinning` operation on the forest state data.
* At time point 10, the 2 branches from time point 5 are extended both with a `grow` operation, then branched again with `do_nothing` and `thinning` operations, resulting in 4 branches.
* At time point 15, `reporting` is done on the 4 individual state branches.

```yaml
# simulation run control parameters
# simulation epoch at intial_step_time 0
# simulation progresses in step_time_interval of 5 units
# simulation end at final_step_time 15
simulation_params:
  initial_step_time: 0
  step_time_interval: 5
  final_step_time: 15

# example of operation run constrains
# minimum time interval constrain between thinnings is 10 years
run_constraints:
  thinning:
    minimum_time_interval: 10

# example of operation parameters
# reporting operation gets parameter level with value 1
operation_params:
   reporting:
      level: 1

# simulation_events are a collection of operations meant to be executed at
# the specified time_points
simulation_events:
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

Step tree from declaration above

![Step tree](doc/20220221_sim-tree.drawio.png)

Operation chains from step tree above

![Operation chains](doc/20220221_sim-chains.drawio.png)

## Simulator

The three important concepts in the `sim` package are **operations**, **processor**, **step tree** and **generators**.

### Operation

An operation is a function whose responsiblities are 1) to trigger manipulation of simulation state and 2) to compute derived data about simulation state before and/or after state manipulation.
For the purposes of the simulator, the operation is a partially applied function from the domain package (forestry) such that it will take only one argument.
They are produced as lambda functions based on the `control.yaml` declaration.

As an example, a single operation such as `grow` would receive a single argument of type `ForestStand` upon which it operates and finally returns a `ForestStand` for the modified/new state.

### Processor

The processor is a function wrapper which handles running a prepared operation (see above).
The parameter is an `OperationPayload` instance.
The `OperationPayload` object is the container for simulation state data, along with a record of simulation run history and operation run constraints.
Responsibilities of the processor function are as follows:

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
For the simulation purposes, these input functions are the prepared processors (see above), but the simulator implementation literally does not care what these functions are.
Sequences are linear chains of steps.
Alternatives are branching steps.
The generators are chainable such that they can expand the step tree in formation based on the results of earlier generator results.

Step instances are generated and bound to earlier steps (parents) as successors (children).
`compose` function executes the `sequence` and `alternatives` to build the complete simulation step tree.

The `generators_from_declaration` function prepares the generator functions from the `control.yaml` structure, preparing necessary processor and operation functions within.

## The domain

The `forestry` package contains the operations necessary to represent the simulation state data and operations acting upon that data.

### State data

The class `ForestStand` and the `ReferenceTree` and `TreeStratum` instances it refers to.
A single `ForestStand` instance fully represents a forestry simulation state.

### Operations

Operations are functions which take two arguments

* A tuple of a `ForestStand` instance and a `dict` containing aggregated data collected during the simulation run
* Python `dict` containing parameters for this operation

By convention (since Python as a language does not allow us to properly enforce this), these functions must remain pure and not trigger side-effectful program logic.
Operations may do in-place mutation of the argument tuple.
Operations may not mutate the operation parameter `dict`

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

### Using R functions

To run operations using the R functions you need R available in the local environment.
You must additionally install the Python `rpy2` package for the necessary API.
For convenience, this can be installed via the `optional-requirements.txt`.

```
pip install --user -r optional-requirements.txt
```


The forestry.r_utils.py module contains functions and examples of how to bind into R functions.
The `r` directory houses related R script and data files.

An example implementation `lmfor_volume` exists for forest stand volume calculation.
Currently, this can be taken into use with the `report_volume` operation function in the control.yaml, following the example below

```
operation_params:
  report_volume:
    lmfor_volume: true
```

The project contains a `DESCRIPTION` file which must be used to declare R library dependencies for R scripts.
This is not necessary for running the R scripts locally, but is required for dependency resolution in the GitHub Actions test runs pipeline.
Local dependencies are handled by the script files as exemplified by the beginning of the `lmfor_volume.R`.
It will install its dependencies on run if they are not found from the local environment R libraries.

```
library_requirements <- c("lmfor")
if(!all(library_requirements %in% installed.packages()[, "Package"]))
  install.packages(repos="https://cran.r-project.org", dependencies=TRUE, library_requirements)
library(lmfor)
```


## Notes for simulation creators

Use the control.yaml structure declaration to control the simulation structure, domain operations and parameters that are to be used.
