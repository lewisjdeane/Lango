import codecs
import configparser
import os.path
import random

lines = []
mode  = "LTF"
name = ""
path = ""
target = 5


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    print_intro_message()
    print_paths()
    load_path()
    load_file()
    load_mode()
    load_target()
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


def load_target():
    global target

    config = configparser.ConfigParser()
    config.read("config.ini")

    try:
        section = config["GENERAL"]
        t = section["Target"]
        target = int(t)
    except KeyError:
        section = config["GENERAL"]
        section["Target"] = str(5)
        target = 5

    with open('config.ini', 'w') as configfile:
        config.write(configfile)


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
    (x1, y1) = modify(x, y)
    message = input("\nQ: %s\nA: " % x1)
    parse(message, y1, x)
    main_loop()


def parse(message, answer, x):
    global target

    if message == "lango exit":
        exit()
    elif message == "lango reload":
        load_file()
        print("INFO: File has been reloaded.")
    elif message == "lango paths":
        print_paths()
    elif message == "lango set target":
        print("")
        t = int(input("| Target: "))

        if t > 0:
            set_target(t)
        else:
            print("\nERROR: Invalid target, target remains what it was.")
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
            config.read('names.ini')
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
             "  lango exit       -> Exits the program.",
             "  lango help       -> Launch this help screen.",
             "  lango reload     -> Reload the current path.",
             "  lango paths      -> List all names and paths.",
             "  lango add path   -> Add a new path.",
             "  lango load path  -> Load a new path.",
             "  lango set mode   -> Set the current mode.",
             "  lango get mode   -> Return the current mode.",
             "  lango set target -> Set the current target.",
             "  lango get target -> Return the current target.",
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
    elif message == "lango get target":
        config = configparser.ConfigParser()
        config.read('config.ini')
        print("INFO: Current target is '%s'.\n" % (config['GENERAL']['Target']))
    elif message.lower() == answer.lower():
        score = update_word_stats(x, True)
        print(">  Correct! [%d/%d]" % (score, target))

        if score == target:
            remove_word(x)
    else:
        score = update_word_stats(x, False)
        print(">  Incorrect, correct answer was '%s'. [%d/%d]" % (answer, score, target))


def remove_word(word):
    global lines

    y = [line.rstrip('\n').rstrip('\r') for line in codecs.open(path, 'r', encoding='utf-8')]

    sd = [x for x in y if not x.startswith(word + " = ")]
    fd = [x for x in y if x.startswith(word + " = ")]

    try:
        k = sd.index("# Learnt")
        p = sd[0:k]
        z = p + ["# Learnt"] + fd + y[k+2:]
    except ValueError:
        z = sd + ["# Learnt"] + fd

    f = codecs.open(path, "w", "utf-8")
    f.write("\n".join(z))
    f.close()

    load_file()


def update_word_stats(word, correct):
    global name
    config = configparser.ConfigParser()
    config.read(name.lower() + ".ini")

    try:
        section = config['WORDS']
        try:
            x = int(section[word])
            if correct:
                x += 1
            else:
                x -= 1
            score = max(x, 0)
            section[word] = str(score)
        except KeyError:
            if correct:
                score = 1
            else:
                score = 0
            section[word] = str(score)
    except KeyError:
        config['WORDS'] = {}
        section = config['WORDS']
        if correct:
            score = 1
        else:
            score = 0
        section[word] = str(score)

    with open(name.lower() + ".ini", 'w') as configfile:
        config.write(configfile)

    return score


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

    try:
        k = y.index("# Learnt")
        z = y[:k]
    except ValueError:
        z = y

    lines = [seperate(x) for x in z if " = " in x]

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


def set_target(t):
    global target

    target = t

    config = configparser.ConfigParser()
    config.read('config.ini')

    try:
        general = config['GENERAL']
    except KeyError:
        config['GENERAL'] = {}
        general = config['GENERAL']

    general['Target'] = str(t)

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    print("INFO: Set target to %d\n" % (t))


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
                   + "(MIX, N2L or L2N): ")
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
    
    line = lines[rand]

    return (line[0], line[1])

def modify(x, y):
    if mode == "L2N":
        return (x, y)
    elif mode == "N2L":
        return (y, x)
    else:
        index = random.randint(0, 1)
        if index == 0:
            return (x, y)
        else:
            return (y, x)



def print_intro_message():
    print("\nWelcome to lango! Run 'lango help' to get show documentation" \
        + "on how to use lango.\n")


main()