from sim.operations import grow, cut, plant, do_nothing
from sim.runners import sequence, alternatives, follow
from sim.generators import instruction_with_options

if __name__ == "__main__":
    rounds = 5
    initial_volume = 40000

    actions = lambda x: alternatives(
        x,
        do_nothing,
        *instruction_with_options(cut, [25, 50, 75])
    )

    cycle = lambda y: sequence(
        y,
        grow,
        actions
    )

    payload = [initial_volume]
    print(payload)
    for i in range(1, rounds):
        generated = []
        for j in payload:
            if j is not None:
                result = cycle(j)
                print("Branch with " + str(j) + "->" + str(result))
                for k in result:
                    generated.append(k)
        payload = generated
