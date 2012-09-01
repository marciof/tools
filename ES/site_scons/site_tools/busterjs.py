program = 'buster'


# TODO: Make the build aware of the configuration file.
def run_tests(env, target, config = None):
    env.AlwaysBuild(env.Alias(target, action = [[program, 'test']]))


def generate(env, **kwargs):
    env.AddMethod(run_tests, 'Buster')


def exists(env):
    return env.Detect(program)
