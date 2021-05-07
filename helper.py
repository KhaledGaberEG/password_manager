RED = "\033[1;31;40m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
PROMPT = "\033[1;37m"
END = "\033[1;0m"


class Error(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return "{}{}{}".format(RED, self.message, END)


def print_colour(colour: str, string: str, end='\n'):
    # this function print passed arguments in specified supported colors
    # which are red, green, blue, yellow
    if colour == "RED":
        print("{}{}{}".format(RED, string, END), end=end)
        return
    elif colour == "BLUE":
        print("{}{}{}".format(BLUE, string, END), end=end)
        return
    elif colour == "GREEN":
        print("{}{}{}".format(GREEN, string, END), end=end)
        return
    elif colour == "YELLOW":
        print("{}{}{}".format(YELLOW, string, END), end=end)
        return
    elif colour == "PROMPT":
        print("{}{}{}".format(PROMPT, string, END), end=end)
        return
    else:
        raise Error("{}[+]colour is not supported{}".format(RED, END))
