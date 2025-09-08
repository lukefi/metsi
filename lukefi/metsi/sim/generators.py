from typing import Any, Optional
from collections.abc import Callable
from lukefi.metsi.sim.core_types import (
    EventTree,
    ProcessedGenerator,
    ProcessedOperation,
    SimConfiguration,
    DeclaredEvents,
    GeneratorFn)
from lukefi.metsi.sim.event import Generator, GeneratorBase, Sequence, Treatment
from lukefi.metsi.sim.operations import prepared_processor, prepared_operation
from lukefi.metsi.sim.util import get_treatment_file_params, merge_operation_params
from lukefi.metsi.app.utils import MetsiException


class NestableGenerator[T]:
    """
    NestableGenerator represents a tree for nested event generators in the simulation tree. Construction of this class
    creates a tree structure where leaf nodes represent actual GeneratorFn instances to populate an Event tree. The
    tree organization represents the nested sequences and alternatives structure in simulation events declaration.
    """
    prepared_generator: Optional[ProcessedGenerator[T]] = None
    time_point: int = 0
    nested_generators: list['NestableGenerator[T]']
    free_treatments: list[Treatment[T]]
    config: SimConfiguration

    def __init__(self,
                 config: SimConfiguration,
                 generator_declaration: Generator[T],
                 time_point: int):
        """Construct a NestableGenerator for a given generator block within the SimConfiguration and for the given
        time point."""
        self.config = config
        self.generator = generator_declaration
        self.time_point = time_point
        self.nested_generators = []
        self.free_treatments = []
        # children_tags = generator_declaration[self.generator_type]
        children_tags = generator_declaration.treatments

        for child in children_tags:
            self.wrap_generator_candidate(child)

        if self.free_treatments:
            if len(self.nested_generators) == 0:
                # leaf node, prepare the actual GeneratorFn
                prepared_operations: list[ProcessedOperation[T]] = []
                for treatment in self.free_treatments:
                    ops: list[ProcessedOperation[T]] = prepare_parametrized_treatments(treatment, time_point)
                    prepared_operations.extend(ops)
                self.prepared_generator = generator_function(self.generator.generator_fn, *prepared_operations)
            else:
                self.wrap_free_treatments()

    def wrap_generator_candidate(self, candidate: GeneratorBase):
        """Create NestableGenerators for nested generator declarations within current generator block. Separate
        individual operations as free operations into self state."""
        if isinstance(candidate, Generator):
            # Encountered a nested generator.
            self.wrap_free_treatments()
            self.nested_generators.append(NestableGenerator(self.config, candidate, self.time_point))
        elif isinstance(candidate, Treatment):
            # Encountered a treatment.
            self.free_treatments.append(candidate)

    def wrap_free_treatments(self):
        """Create NestableGenerators for individual operations collected into self state. Clear the list of operations
        afterwards."""
        if self.free_treatments:
            # decl = {self.generator_type: self.free_treatments}
            decl = self.generator
            self.nested_generators.append(NestableGenerator(self.config, decl, self.time_point))
            self.free_treatments = []

    def unwrap(self, previous: list[EventTree[T]]) -> list[EventTree[T]]:
        """
        Recursive depth-first walkthrough of NestableGenerator tree starting from self to generate a list of EventTrees.
        These denote the leaves of the given EventTrees as expanded by self.

        Sequence type NestableGenerators generate their tree of children EventTrees to follow up each of the given
        previous nodes in order. Idea is like "previous + next1,next2 => [previous, next1, next2]".

        Alternatives type NestableGenerators generate their tree of children EventTrees attaching a copy to each given
        previous node. Idea is like "previous + next1,next2 => [previous, next1], [previous, next2]".

        Recursion end condition 1 is that self is a leaf that has a GeneratorFn that ultimately extends upon
        the previous EventTrees and returns the resulting list of EventTrees.

        Recursion end condition 2 is that a leaf that has no GeneratorFn or child NestableGenerators. Returns the
        previous EventTrees unaltered.

        :param previous: list of EventTree nodes denoting the node at parent NestableGenerator or another EventTree root
        :return: list of EventTree nodes resulting from attempting to attach self's EventTree into previous nodes
        """
        if self.prepared_generator is not None:
            return self.prepared_generator(previous)
        if self.generator.generator_fn == sequence:  # pylint: disable=comparison-with-callable
            current: list[EventTree[T]] = previous
            for child in self.nested_generators:
                current = child.unwrap(current)
            return current
        if self.generator.generator_fn == alternatives:  # pylint: disable=comparison-with-callable
            current = []
            for child in self.nested_generators:
                current.extend(child.unwrap(previous))
            return current
        return previous


def sequence[T](parents: Optional[list[EventTree[T]]] = None, /, *operations: ProcessedOperation) -> list[EventTree[T]]:
    """
    Generate a linear sequence of EventTree nodes, optionally extending each node in the given list of nodes with it.
    :param parents: optional
    :param operations:
    :return:
    """
    result: list[EventTree[T]] = []
    if parents is None or len(parents) == 0:
        parents = [EventTree()]
    for root_event in parents:
        parent_node = root_event
        for operation in operations:
            branch = EventTree(operation, parent_node)
            parent_node.add_branch(branch)
            parent_node = branch
        result.append(parent_node)
    return result


def alternatives[T](parents: Optional[list[EventTree[T]]] = None, /,
                    *operations: ProcessedOperation[T]) -> list[EventTree[T]]:
    """
    Generate branches for an optional list of EventTree nodes, out of an *args list of given operations
    :param parents:
    :param operations:
    :return: a list of leaf nodes now under the given parent node
    """
    result: list[EventTree[T]] = []
    if parents is None or len(parents) == 0:
        parents = [EventTree()]
    for parent_node in parents:
        for operation in operations:
            branch = EventTree(operation, parent_node)
            parent_node.add_branch(branch)
            result.append(branch)
    return result


def compose_nested[T](nestable_generator: NestableGenerator[T]) -> EventTree[T]:
    """
    Generate a simulation EventTree using the given NestableGenerator.

    :param nestable_generator: NestableGenerator tree for generating a EventTree.
    :return: The root node of the generated EventTree
    """
    root: EventTree[T] = EventTree()
    nestable_generator.unwrap([root])
    return root


def simple_processable_chain[T](operation_tags: list[Callable[[T], T]],
                                operation_params: dict[Callable[[T], T], Any]) -> list[Callable[[T], T]]:
    """Prepare a list of partially applied (parametrized) operation functions based on given declaration of operation
    tags and operation parameters"""
    result: list[Callable[[T], T]] = []
    for tag in operation_tags if operation_tags is not None else []:
        params = operation_params.get(tag, [{}])
        if len(params) > 1:
            raise MetsiException(f"Trying to apply multiple parameter set for preprocessing operation \'{tag}\'. "
                                 "Defining multiple parameter sets is only supported for alternative clause "
                                 "generators.")
        result.append(prepared_operation(tag, **params[0]))
    return result


def generator_declarations_for_time_point[T](events: list[DeclaredEvents[T]],
                                             time: int) -> list[Generator[T]]:
    """
    From events declarations, find the EventTree generators declared for the given time point.

    :param events: list of DeclaredEvents objects for generator declarations and time points
    :param time: point of simulation time for selecting matching generators
    :return: list of generator declarations for the desired point of time
    """
    generator_declarations: list[Generator[T]] = []
    for generator_candidate in events:
        if time in generator_candidate.time_points:
            generator_declarations.append(generator_candidate.treatment_generator)
    return generator_declarations


def generator_function[T](key: GeneratorFn[T],
                          *fns: ProcessedOperation[T]) -> ProcessedGenerator[T]:
    """Crate a generator function wrapper for function by the key. Binds the
    argument list of functions with the generator."""
    return lambda parent_nodes: key(parent_nodes, *fns)


def prepare_parametrized_treatments[T](treatment: Treatment[T],
                                       time_point: int) -> list[ProcessedOperation[T]]:
    this_operation_file_params = get_treatment_file_params(treatment)
    combined_params = merge_operation_params(treatment.parameters, this_operation_file_params)
    return [prepared_processor(treatment.treatment_fn, time_point, treatment.run_constraints, **combined_params)]


def full_tree_generators[T](config: SimConfiguration[T]) -> NestableGenerator[T]:
    """
    Create a NestableGenerator describing a single simulator run.

    :param config: a prepared SimConfiguration object
    :return: a list of prepared generator functions
    """
    wrapper: NestableGenerator[T] = NestableGenerator(config, Sequence([]), 0)
    for time_point in config.time_points:
        generator_declarations = generator_declarations_for_time_point(config.events, time_point)
        time_point_wrapper_declaration: Sequence[T] = Sequence(generator_declarations)
        wrapper.nested_generators.append(NestableGenerator(config, time_point_wrapper_declaration, time_point))
    return wrapper


def partial_tree_generators_by_time_point[T](config: SimConfiguration[T]) -> dict[int, NestableGenerator[T]]:
    """
    Create a dict of NestableGenerators keyed by their time_point in the simulation. Used for generating
    partial EventTrees of the simulation.

    :param config: a prepared SimConfiguration object
    :return: a list of prepared generator functions
    """

    generators_by_time_point = {}

    for time_point in config.time_points:
        generator_declarations = generator_declarations_for_time_point(config.events, time_point)
        sequence_wrapper_declaration: Sequence[T] = Sequence(generator_declarations)
        wrapper_generator: NestableGenerator = NestableGenerator(config, sequence_wrapper_declaration, time_point)
        generators_by_time_point[time_point] = wrapper_generator
    return generators_by_time_point


__all__ = ['sequence', 'alternatives']
