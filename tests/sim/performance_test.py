import copy
import time
import unittest

from lukefi.metsi.data.model import ForestStand, ReferenceTree, TreeStratum
from lukefi.metsi.sim.collected_data import CollectedData
from lukefi.metsi.sim.simulation_payload import SimulationPayload
from lukefi.metsi.sim.runners import run_full_tree_strategy, run_partial_tree_strategy, chain_evaluator, depth_first_evaluator
from lukefi.metsi.sim.sim_configuration import SimConfiguration

optime = 0
counter = 0


def nodecount(x, sleeptime):
    global optime
    global counter
    start = time.time_ns()
    time.sleep(sleeptime)
    end = time.time_ns()
    diff = round((end - start) / 1000000000, 3)
    optime += diff
    counter += 1
    return x


def create_sim_configs(workload_time):
    """Create 4 simulation configurations with roughly 400 total full strategy nodes each, with increasing width of the tree"""
    return [
        SimConfiguration(operation_lookup={'nodecount': lambda x: nodecount(x, workload_time)}, **{'simulation_instructions': [
            {'time_points': list(range(400)), 'generators': [{'sequence': ['nodecount']}]}
        ]}),
        SimConfiguration(operation_lookup={'nodecount': lambda x: nodecount(x, workload_time)}, **{'simulation_instructions': [
            {'time_points': [0], 'generators': [{'sequence': ['nodecount', 'nodecount', 'nodecount', 'nodecount']}]},
            {'time_points': list(range(6)), 'generators': [{'alternatives': ['nodecount', 'nodecount']}]}
        ]}),
        SimConfiguration(operation_lookup={'nodecount': lambda x: nodecount(x, workload_time)}, **{'simulation_instructions': [
            {'time_points': [0], 'generators': [{'sequence': ['nodecount', 'nodecount', 'nodecount', 'nodecount']}]},
            {'time_points': list(range(4)), 'generators': [{'alternatives': ['nodecount', 'nodecount', 'nodecount']}]}
        ]}),
        SimConfiguration(operation_lookup={'nodecount': lambda x: nodecount(x, workload_time)}, **{'simulation_instructions': [
            {'time_points': [0], 'generators': [{'sequence': ['nodecount', 'nodecount', 'nodecount', 'nodecount']}]},
            {'time_points': list(range(3)), 'generators': [{'alternatives': ['nodecount', 'nodecount', 'nodecount', 'nodecount']}]}
        ]}),
        SimConfiguration(operation_lookup={'nodecount': lambda x: nodecount(x, workload_time)}, **{'simulation_instructions': [
            {'time_points': [0], 'generators': [{'sequence': ['nodecount', 'nodecount', 'nodecount', 'nodecount']}]},
            {'time_points': list(range(3)), 'generators': [{'alternatives': ['nodecount', 'nodecount', 'nodecount', 'nodecount', 'nodecount']}]}
        ]})
    ]


strategies = [
    run_full_tree_strategy,
    run_partial_tree_strategy
]


evaluators = [
    chain_evaluator,
    depth_first_evaluator
]

@unittest.skip("Manual run only")
class PerformanceTest(unittest.TestCase):
    def test_constant_work_performance(self):
        """This is a manual test case created for observing the choice of run strategies related to the shape of the
        simulation events tree. Some details about execution times are printed out. Operation workload is simulated
        with a configured constant amount of system sleep time. This may not be totally accurate but should average out.
        """
        fixture = ForestStand()
        fixture.reference_trees_pre_vec = [
            ReferenceTree(),
            ReferenceTree(),
            ReferenceTree(),
            ReferenceTree(),
            ReferenceTree()
        ]
        global optime
        global counter
        workload_time = 0.002
        sims = create_sim_configs(workload_time)

        # run once to eliminate cold start effect
        run_full_tree_strategy(SimulationPayload(computational_unit=fixture, collected_data=CollectedData(initial_time_point=sims[0].time_points[0]), operation_history=[]), sims[0])
        optime = 0
        counter = 0

        for si_n, sim in enumerate(sims):
            print(f"sim {si_n}")
            for strategy in strategies:
                print(f"  strategy {strategy.__name__}")
                for evaluator in evaluators:
                    print(f"    evaluator {evaluator.__name__}")
                    payload = SimulationPayload(computational_unit=fixture, collected_data=CollectedData(initial_time_point=sim.time_points[0]), operation_history=[])
                    start = time.time_ns()
                    result = strategy(payload, sim, evaluator)
                    end = time.time_ns()
                    diff = round((end - start) / 1000000000, 3)
                    optime = round(optime, 3)
                    enginetime = round(diff - optime, 3)
                    print(f"      variants {len(result)}, operation calls {counter} ")
                    print(f"      total time {diff} s, operation time {optime} s, engine time {enginetime} s ({round(enginetime / diff * 100, 1)} % of total)")
                    optime = 0
                    counter = 0
            print("\n")

    def test_raw_copying_performance(self):
        """This is a manual test case for comparing the copying performance of the OperationPayload."""
        fixture = ForestStand()
        fixture.reference_trees_pre_vec = [
            ReferenceTree(),
            ReferenceTree(),
            ReferenceTree(),
            ReferenceTree(),
            ReferenceTree(),
            ReferenceTree(),
            ReferenceTree(),
            ReferenceTree(),
            ReferenceTree(),
            ReferenceTree()
        ]
        fixture.tree_strata_pre_vec = [
            TreeStratum(),
            TreeStratum(),
            TreeStratum(),
            TreeStratum(),
            TreeStratum(),
            TreeStratum(),
            TreeStratum(),
            TreeStratum(),
            TreeStratum(),
            TreeStratum(),
            TreeStratum()
        ]
        payload = SimulationPayload(computational_unit=fixture, collected_data=CollectedData(initial_time_point=0), operation_history=[])

        steps = 50000
        worktime = 0.00001
        operation = lambda x: nodecount(x, worktime)

        start = time.time_ns()
        result = payload
        for i in range(steps):
            result = operation(result)
        end = time.time_ns()
        no_copy_time = round((end - start) / 1000000000, 3)

        start = time.time_ns()
        for i in range(steps):
            result = copy.deepcopy(operation(result))
        end = time.time_ns()
        deepcopy_time = round((end - start) / 1000000000, 3)

        print("")
        print(f"No copy;  total {no_copy_time} seconds with {steps} steps")
        print(f"Deepcopy; total {deepcopy_time} seconds with {steps} steps")


