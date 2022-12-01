from string import ascii_letters, digits
from random import randint


def generate_serial(length):
    all_chars = ascii_letters + digits
    serial_list = list()
    while length > 0:
        serial_list.append(all_chars[randint(0, len(all_chars) - 1)])
        length -= 1
    return 'serial_' + "".join(serial_list)
