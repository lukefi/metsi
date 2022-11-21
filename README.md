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
* Ensure that the commands `python`, `pip` and `git` are available in your command line interface (CLI). We assume a UNIX-like shell CLI such as Git Bash for Windows users.
* Initialize the project with the commands below.

```
git clone https://github.com/menu-hanke/sim-workbench
cd sim-workbench
pip install -r requirements.txt
```

To obtain latest changes use the command `git pull`.

### Notes about proxy configuration for Luke users

Both git and pip use a separate configuration for WWW proxy.
Proxy is manadatory for Luke internal network.
Software Center presets this for pip, but not for git.
Depending on whether you are using Luke internal network (Ethernet, Reitti or FortiClient VPN) or another network, you need to adjust proxy configuration manually to be able to run internet-facing commands with these tools.

In the following subsections, `~` denotes your home directory.
This is your home directory in windows format is a path such as `C:\Users\12345678`.
You can always re-enter your home directory by running the command `cd`, or explicitly `cd ~`.

#### pip

The pip configuration file can be found in `~/AppData/Roaming/pip/pip.ini`.
It may be overridden with `~/pip/pip.ini`.
To enable the proxy usage, the file should have a proxy configuration line in the global section such as

```
[global]
proxy = http://suoja-proxy.vyv.fi:8080
```

To disable the proxy, insert a `#` character in front of the proxy line to comment it out.

#### git

The git configuration file can be found in `~/.gitconfig`.
By default this file does not exist.
To enable the proxy usage, the file should have a proxy configuration line in the http section such as

```
[http]
proxy = http://suoja-proxy.vyv.fi:8080
```

To disable the proxy, insert a `#` character in front of the proxy line to comment it out.

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

1. A source data file which contains forest stand, reference tree and tree stratum information
   1. a .json file or .pickle file containing Forest Data Model type source data.
   2. a .dat file containing VMI12 or VMI13 type source data
   3. a .xml file containing Forest Centre type source data
2. A YAML file which is used as a configuration for a simulator run. See `control.yaml` for an example. See section about Simulation control for further information.

There are several example input files in the project `data` directory.
These are data files with a list of ForestStand objects containing a list of RefenceTree objects generated from TreeStratum objects with Weibull distribution.

See table below for a quick reference of forestry operations usable in control.yaml.

| operation                 | description                                                                                    | source                      | model library             |
|---------------------------|------------------------------------------------------------------------------------------------|-----------------------------|---------------------------|
| do_nothing                | This operation is no-op utility operation to simulate rest                                     |                             | native                    |
| grow_acta                 | A simple ReferenceTree diameter and height growth operation                                    | Acta Forestalia Fennica 163 | forestry-function-library |
| grow_motti                | A ReferenceTree growth operation with death and birth models. Requires `pymotti`.              | Luke Motti group            | pymotti                   |
| first_thinning            | An operation reducing the stem count of ReferenceTrees as a first thinning for a forest        | Reijo Mykkänen              | forestry-function-library |
| thinning_from_below       | An operation reducing the stem count of ReferenceTrees weighing small trees before large trees | Reijo Mykkänen              | forestry-function-library |
| thinning_from_above       | An operation reducing the stem count of ReferenceTrees weighing large trees before small trees | Reijo Mykkänen              | forestry-function-library |
| even_thinning             | An operation reducing the stem count of ReferenceTrees evenly regardless of tree size          | Reijo Mykkänen              | forestry-function-library |
| report_volume             | Collect tree volume data from ForestStand state                                                |                             | native                    |
| report_thinning           | Collect thinning operation details from data accrued from thinning operations                  |                             | native                    |
| report_collectives        | Save the values of [collective variables](#collective-variables)                               |                             | native                    |
| cross_cut_felled_trees | Perform cross cut operation to results of previous thinning operations                         | Annika Kangas               | forestry-function-library |
| cross_cut_whole_stand     | Perform cross cut operation to all standing trees on a stand                                   | Annika Kangas               | forestry-function-library |

To run the simulator application, run the following command in the project root.
The created output diretory contains all generated variants for all computation units (ForestStand) along with derived data.
The output directory container output is usable as input for the `app/post_processing.py` application.

```
python -m app.simulator --state-input-container pickle data/VMI12_data.pickle control.yaml outdir
```

In case you want to use JSON as the input and/or output file format, run:
```
python -m app.simulator --state-input-container json --state-output-container json data/VMI12_data.json control.yaml outdir
```

To only run the preprocessor, run:
```
python -m app.simulator -s skip ...
```

Use the following command to output simulator application help menu.
```
python -m app.simulator --help
```

## Usage of the post processing application

To run the post processing application, run in the project root

```
python -m app.post_processing -o json input.pickle pp_control.yaml outdir
```

This produces `outdir/pp_result.json` file.

* `input.pickle` The result file of a simulator run.
* `pp_control.yaml` is the declaration of post processing function chain.
* `outdir` is the output directory for post processed results

To learn more about the available post processing commands (and how to input/output a JSON file), run:
```
python -m app.post_processing --help
```
## Usage of the data export application

Run
```
python -m app.export input.pickle export_control.yaml
```
where
* `input.pickle` is simulator or post-processor output,
* `export_control.yaml` is the export declaration file.

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

1. Application file IO configuration in `io_configuration` object. These may be overridden by equivalent command line arguments. Note that e.g. `state_format` with `fdm` below is written as `--state-format fdm` when given as a command line argument.
   1. `state_format` specifies the data format of the input computational units
      1. `fdm` is the standard Forest Data Model.
      2. `vmi12` and `vmi13` denote the VMI data format and container.
      3. `forest_centre` denotes the Forest Centre XML data format and container.
   2. `state_input_container` is the file type for `fdm` data format. This may be `csv`, `pickle` or `json`.
   3. `preprocessing_output_container` is the file type for outputting the `fdm` formatted state of computational units after preprocessing operations. This may be `csv`, `pickle` or `json` or commented out for no output.
   4. `state_output_container` is the file type for outputting the `fdm` formatted state of individual computational units during and after the simulation. This may be `csv`, `pickle` or `json` or commented out for no output.
   5. `derived_data_output_container` is the file type for outputting derived data during and after the simulation. This may be `pickle` or `json` or commented out for no output.
2. Operaton run constrains in the object `run_constraints`
3. Operation parameters in the object `operation_params`. Operation parameters may be declared as a list of 1 or more parameter sets (objects). Operations within an `alternatives` block are expanded as further alternatives for each parameter set. Multiple parameter sets may not be declared for operations within any `sequence` block.
4. List of `simulation_events`, where each object represents a single set of operations and a set of time points for those operations to be run.
   1. `time_points` is a list of integers which assign this set of operations to simulation time points
   2. `generators` is a list of chained generator functions (see section on step generators)
      1. `sequence` a list of operations to be executed as a chain
      2. `alternatives` a list of operations which represent alternative branches
5. Preprocessing operations can be passed as a list of strings under `preprocessing_operations`, and their (optional) arguments under `preprocessing_params` as key-value pairs. 
6. Operation parameters that **exist in files** can be passed in `operation_file_params` as demonstated below: 
   ```yaml 
   operation_file_params:
     first_thinning:
       thinning_limits: /path/to/file/thinning-limits.txt
     cross_cut_felled_trees:
       timber_price_table: /path/to/file/timber-prices.csv
   ```
   Note however, that it is the user's responsibility to provide the file in a valid format. 


The following example declares a simulation, which runs four event cycles at time points 0, 5, 10 and 15.
Images below describe the simulation as a step tree, and further as the computation chains that are generated from the tree.

* At time point 0, `reporting` of the simulation state is done.
* At time point 5, the `grow` operation is done on the simulation state and the simulation is branched by 3. One branch does not modify the forest state data with `do_nothing`, another performs a `thinning` operation on the forest state data with parameter set 1, and another `thinning` operation with parameter set 2.
* At time point 10, the 3 branches from time point 5 are extended separately with a `grow` operation, then branched again with `do_nothing` and `thinning` operations with two parameter sets, resulting in 9 branches.
* At time point 15, `reporting` is done on the 9 individual state branches.

```yaml
# example of operation run constrains
# minimum time interval constrain between thinnings is 10 years
run_constraints:
  thinning:
    minimum_time_interval: 10

# example of operation parameters
# reporting operation gets one parameter set
# thinning operation gets two parameter sets
operation_params:
  reporting:
    - level: 1
  thinning:
    - thinning_factor: 0.7
      e: 0.2
    - thinning_factor: 0.9
      e: 0.1

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

![Step tree](doc/drawio/20220221_sim-tree.drawio.png)

Operation chains from step tree above, as produced by the __full tree strategy__ (see below for partial tree strategy)

![Operation chains](doc/drawio/20220221_sim-chains.drawio.png)

## Collective variables

The `report_collectives` operation and data export make use of *collective variables*.
A collective variable is a python expression that is evaluated on a `ForestStand`.
For example the expression `year` will collect `ForestStand.year`.
You can collect tree variables by typing `reference_trees.variable_name`.
You can also slice the variable, eg. `reference_trees.volume[reference_trees.species==1]`
will collect the total volume of pine.
The collective arrays are just numpy arrays, so all numpy slicing operations are supported.

For export data collection you can index the collection array by collection **year**,
so `Vpine` would export the collective `Vpine` from all periods, and `Vpine[0,5]` would
export it from **years** 0 and 5.

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

## Strategies
The simulator strategies determine how the program traverses down the simulation tree. The _full_ strategy executes `run_full_tree_strategy`, whereas the _partial_ strategy executes `run_partial_tree_strategy`.

It should be noted that while the full strategy is simpler to understand conceptually, it carries a significant memory and runtime overhead for large simulation trees, and therefore the `partial` strategy should be focused on as the performant solution.


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

### A Thought exercise on the partial tree strategy

To understand the partial tree strategy better, consider a simulator instruction such as:

```yaml
simulation_events:
  - time_points: [0,5]
    generators:
      - sequence:
        - grow
      - alternatives:
        - do_nothing
        - thinning
```
 which will produce a simulator tree as below:

![Simple simulation tree](doc/drawio/simple-sim-tree.drawio.png)

the `full` strategy would create operation chains (one for each possible path in the tree) and run them independently from one another. In this case, we would have four separate chains, each chain having four operations.

On the other hand, the `partial` strategy would proceed as follows:

1. create operation chains from the nodes in the first time point, and run them:

![Partial strategy first period example](doc/drawio/partial_strat_first_period.drawio.png)

Here you'll notice that the first period's `grow` operation is executed twice, whereas the ``full`` tree strategy would have executed it four times.

2. For all successful results from the first period, create operation chains from the nodes in the second period:

![Partial strategy second period example](doc/drawio/partial_strat_second_period.drawio.png)

Now, let's assume that the second chain from time point 0 would not complete successfully, e.g. due to a constraint set on the thinning operation. At time point 5, The partial tree strategy would then only create operation chains for `output 1`, i.e. the two chains on the left in the above diagram. This logic reduces the unnecessary computation the simulator has to make, compared to the full strategy, and this is true especially for large simulation trees.

"Partial" in the strategy name refers to the fact that the strategy creates trees from only the nodes (`Step`s) in one time point at a time (i.e. partial trees/subtrees) and traverses those partial trees (with the same post-order traversal algorithm) to create partial (or sub-) chains of operations. __Therefore, the strategy can be thought to operate depth-first within time points, but breadth-first across time points.__
## Notes for simulation creators

Use the control.yaml structure declaration to control the simulation structure, domain operations and parameters that are to be used.
