# -*- coding: UTF-8 -*-


PROGRAM = 'cython'


def build(env, target, source, is_standalone = False):
    embed_option = ['--embed'] if is_standalone else []
    command = [PROGRAM, '--output-file', str(target)] + embed_option + map(str, source)
    
    return env.Command(target, source, env.Action([command]))


def exists(env):
    return env.Detect(PROGRAM)


def generate(env):
    env.AddMethod(build, PROGRAM.title())
