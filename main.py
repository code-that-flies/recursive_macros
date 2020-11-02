import re

dict_macros = {'print': print}
dict_simple_macros = {}

output = print

def interpret_get_macro(formatted_text):    # TODO: make it fully recursive
    results = re.search(r'(![A-Za-z])\w+', formatted_text)
    function = ""
    if results is not None:
        function = results.group(0)[1:]
    else:
        return  # TODO: add ability to guess the function name based on the parameters

    if function in dict_simple_macros.keys():
        output(dict_macros[function])

        return dict_simple_macros[function], {'function': function, 'args': []}

    raw_args = re.findall(r'({.+})|(~[\w-]+)', formatted_text)

    args = []
    for primary_result, secondary_result in raw_args:
        if primary_result != '':
            args.append('"' + primary_result[1:-1] + '"')
        else:
            secondary_result = secondary_result[1:]

            if secondary_result in dict_simple_macros.keys():
                secondary_result = dict_simple_macros[secondary_result]

            args.append(secondary_result)

    # Currently only targets C++ (WIP, will target many more hopefully!)
    output(function + '(' + ', '.join(args) + ');')

    dict_macros[function](*args)
    return dict_macros[function], {'function': function, 'args': args}

interpret_get_macro("!print {test}")


def interpret_set_macro(macro):
    macro


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pass
# See PyCharm help at https://www.jetbrains.com/help/pycharm/