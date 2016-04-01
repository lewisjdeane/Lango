import codecs
import configparser
import os.path
import random

lines = []
mode  = "LTF"
name = ""
path = ""


def main():
    print_intro_message()
    print_paths()
    load_path()
    load_file()
    load_mode()
    main_loop()


def print_paths():
    config = configparser.ConfigParser()
    config.read('names.ini')

    sections = config.sections()

    if len(sections) == 0:
        print("No paths set up yet!\n")
    else:
        pairs = [(name.capitalize(), config[name]['Path']) for name in sections]
        names = [x for (x, y) in pairs]
        mlen = len(max(names, key=len))

        out = ["  You currently have the following paths set up:\n"] + \
              [("  NAME") + (" " * (mlen - 2)) + "PATH"] + \
              [(" " * 2) + x + (" " * (mlen + 2 - len(x))) + y for (x, y) in pairs] + \
              [""]

        print("\n".join(out))


def load_path():
    global path
    global name

    config = configparser.ConfigParser()
    config.read('names.ini')

    if len(config.sections()) > 0:
        n = input("Enter name of path to load: ")

        try:
            p = config[n.upper()]['Path']
            path = p
            name = n
        except KeyError:
            print("ERROR: Invalid name. Trying again...\n")
            load_path()
    else:
        p = input("Enter the path of a file: ")

        if is_valid_path(p):
            n = input("Enter an alias for this path: ")
            config[n.upper()] = {}
            section = config[n.upper()]
            section['Path'] = p
            with open('names.ini', 'w') as configfile:
                config.write(configfile)
            print("INFO: Congratulations! '%s' points to '%s'.\n" % (n, p))
            path = p
            name = n
        else:
            print("ERROR: File does not exist. Trying again...\n")
            load_path()
    

def main_loop():
    (x, y)  = get_word()
    message = input("\nQ: %s\nA: " % x)
    parse(message, y)
    main_loop()


def parse(message, answer):
    if message == "lango exit":
        exit()
    elif message == "lango reload":
        load_file()
        print("INFO: File has been reloaded.")
    elif message == "lango paths":
        print_paths()
    elif message == "lango set mode":
        print("")
        mode = input("| Mode: ")

        if is_valid_mode(mode):
            set_mode(mode)
        else:
            print("\nERROR: Invalid mode, mode remains what it was.")
    elif message == "lango load path":
        print("")
        n = input("| Name: ")

        global name
        global path

        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            p = config[n.upper()]['Path']
        except KeyError:
            print("\nERROR: Invalid path name, path remains what it was.")
            return

        name = n
        path = p
        load_file()

    elif message == "lango add path":
        print("")
        n = input("| Name: ")

        if not name_already_taken(n):
            p = input("| Path: ")

            if is_valid_path(p):
                add_path(p, n)
                print("\nINFO: Success, Path added! '%s' now points to '%s'\n" % (n, p))
                load_file()
            else:
                print("\ERROR: Invalid path, path not added.")
        else:
            print("\ERROR: '%s' is already the name of a path." % (n))
    elif message == "lango help":
        h = ["",
             "  LANGO HELP",
             "  ==========",
             "",
             "> Valid Commands",
             "  --------------",
             "  lango exit      -> Exits the program.",
             "  lango help      -> Launch this help screen.",
             "  lango reload    -> Reload the current path.",
             "  lango paths     -> List all names and paths.",
             "  lango add path  -> Add a new path.",
             "  lango load path -> Load a new path.",
             "  lango set mode  -> Set the current mode.",
             "  lango get mode  -> Return the current mode.",
             "",
             "> Valid Modes",
             "  -----------",
             "  N2L -> Questions printed in native, answer in learning.",
             "  L2N -> Questions printed in learning, answer in native.",
             "  MIX -> Mixture of both the above modes.",
             "",
             "> Writing A Valid File",
             "  --------------------",
             "  All translations must be in the form: 'PHRASE = TRANSLATION'",
             "  E.g. If you were learning french you would write a file like:",
             "",
             "      Un homme = A man",
             "      Une femme = A woman",
             "      Le parc = The park",
             "      Je pense = I think",
             "      ...",
             ""]

        mlen = len(max(h, key=len))
        topbottom = "#" * (mlen + 4)

        newh = [""] + \
               [topbottom] + \
               ["# " + x + (" " * (mlen - len(x))) + " #" for x in h] + \
               [topbottom]
        
        print("\n".join(newh))
    elif message == "lango get mode":
        config = configparser.ConfigParser()
        config.read('config.ini')
        print("INFO: Current mode is '%s'.\n" % (config['GENERAL']['Mode']))
    elif message.lower() == answer.lower():
        print(">  Correct!")
    else:
        print(">  Incorrect, correct answer was '%s'." % (answer))


def name_already_taken(n):
    name = n.upper()

    config = configparser.ConfigParser()
    config.read('names.ini')

    try:
        p = config[name]['Path']
        return True
    except KeyError:
        return False


def is_valid_mode(mode):
    if mode == "MIX" or mode == "N2L" or mode == "L2N":
        return True
    return False

def is_valid_path(path):
    return os.path.isfile(path)

def load_file():
    global lines
    global path

    y = [line.rstrip('\n') for line in codecs.open(path, 'r', encoding='utf-8')]

    lines = [seperate(x) for x in y if " = " in x]

    print("INFO: File loaded successfully.")


def add_path(p, n):
    config = configparser.ConfigParser()
    config.read('names.ini')
    
    try:
        section = config[n.upper()]
        print("INFO: That name is already taken.")
    except KeyError:
        config[n.upper()] = {}
        section = config[n.upper()]
        section['Path'] = p

    with open('names.ini', 'w') as configfile:
        config.write(configfile)


def set_path(path, name):
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    try:
        section = config[name.upper()]
    except KeyError:
        config[name.upper()] = {}
        general = config[name.upper()]
    
    general['Path'] = path

    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def set_mode(mode1):
    global mode

    mode = mode1

    config = configparser.ConfigParser()
    config.read('config.ini')

    try:
        general = config['GENERAL']
    except KeyError:
        config['GENERAL'] = {}
        general = config['GENERAL']

    general['Mode'] = mode1

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    print("INFO: Set mode to %s\n" % (mode1))


def seperate(x):
    y = x.split(" = ", 1)
    return (y[0], y[1].strip('\r'))


def load_mode():
    global mode

    config = configparser.ConfigParser()
    config.read('config.ini')

    # This needs to be better, think whether to force user to enter a valid mode or just do it for them.
    try:
        mode = config['GENERAL']['Mode']
    except KeyError:
        mode = input("INFO: No mode set, please enter a valid mode " \
                   + "(MIX, F2L or L2F): ")
        if is_valid_mode(mode):
            set_mode(mode)
        else:
            print("ERROR: Invalid mode set, setting to 'N2L' for now.\n")
            mode = "N2L"
            set_mode("N2L")


def get_word():
    global lines
    global mode

    if len(lines) > 0:
        rand = random.randint(0, len(lines) - 1)
    else:
        # Needs to be better. Halt loop if no words.
        return ("No words found in file, exit or choose a new filepath.",
                "No words found in file, exit or choose a new filepath.")
    
    if mode == "L2N":
        index = 0
    elif mode == "N2L":
        index = 1
    else:
        index = random.randint(0, 1)

    line = lines[rand]

    return (line[index], line[index ^ 1])


def print_intro_message():
    print("\nWelcome to lango! Run 'lango help' to get show documentation" \
        + "on how to use lango.\n")


main()