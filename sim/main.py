from sim.operations import grow, cut, do_nothing
from sim.runners import evaluate_sequence
from sim.generators import instruction_with_options, sequence, alternatives, compose

if __name__ == "__main__":
    rounds = 5
    initial_volume = 200

    tree = compose(
        lambda x: sequence(
            x,
            grow
        ),
        lambda x: alternatives(
            x,
            do_nothing,
            *instruction_with_options(cut, [25, 50, 75])
        ),
        lambda x: sequence(
            x,
            grow
        ),
        lambda x: alternatives(
            x,
            do_nothing,
            *instruction_with_options(cut, [25, 50, 75])
        ),
        lambda x: sequence(
            x,
            grow
        ),
        lambda x: alternatives(
            x,
            do_nothing,
            *instruction_with_options(cut, [25, 50, 75])
        )
    )

    chains = tree.operation_chains()

    iteration_counter = 1
    for chain in chains:
        try:
            print("running chain " + str(iteration_counter))
            iteration_counter = iteration_counter + 1
            result = evaluate_sequence(initial_volume, *chain)

            print(result)
        except Exception as e:
            print(e)
        print("\n")
