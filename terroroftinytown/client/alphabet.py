# encoding=utf-8
'''Shortcode arbitrary integer base alphabet conversion'''
# http://stackoverflow.com/a/1119769/1524507


def int_to_str(num, alphabet):
    '''Convert integer to string.'''
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def str_to_int(string, alphabet):
    '''Convert string to integer.'''
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1

    return num
