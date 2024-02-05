import argparse


def str_bool_switcher_type(arg):
    try:
        if arg.lower() == 'true' or arg.lower() == 'false':
            return eval(arg)
        else:
            return arg
              
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid type. Must be str/bool")


def tuple_type(arg):
    try:
        values = [int(item) if item.isdigit() else item for item in arg.split(',')]
        return tuple(values)
    
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid tuple format. Must be comma-separated integers/strings without spaces.")