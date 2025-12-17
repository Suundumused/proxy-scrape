import argparse


def str_bool_switcher_type(arg:str):
    try:
        arg2 = arg.lower()
        return eval(arg2) if arg2 == 'true' or arg2 == 'false' else arg
              
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid type. Must be str/bool")


def tuple_type(arg):
    try:
        return tuple([int(item) if item.isdigit() else item for item in arg.split(',')])
    
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid tuple format. Must be comma-separated integers/strings without spaces.")