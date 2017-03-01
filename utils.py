def func_wrap(func, params=0, error_msg=None):

    def return_func(error, data=None):
        if error and error_msg:
            print(error_msg, error)
        elif error:
            print(error)
        elif params == 0:
            func()
        elif params == 1:
            func(data)

    return return_func

def replace_localhost(string):
    i = string.find('localhost')
    replace_with = '127.0.0.1'
    if i > -1:
        return string[:i] + replace_with + string[i + len('localhost'):]
    else:
        return string

