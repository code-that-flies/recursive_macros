import re

dict_functions = {}


def interpret_get_macro(formatted_text):
    results = re.search(r'(![A-Za-z])\w+', formatted_text)
    function = ""
    if results is not None:
        function = results.group(0)
    else:
        return  # TODO: add ability to guess the function name based on the parameters

    raw_args = re.findall(r'({.+})|(~[\w-]+)', formatted_text)

    args = []
    for primary_result, secondary_result in raw_args:
        if primary_result == '':
            args.append(primary_result)
        else:
            args.append(secondary_result)

    if function in dict_functions.keys():
        dict_functions[function](*args)


def interpret_set_macro(macro):
    macro


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pass
# See PyCharm help at https://www.jetbrains.com/help/pycharm/