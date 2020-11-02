import re

dict_macros = {}
dict_simple_macros = {}

output = print

def interpret_get_macro(formatted_text):
    results = re.search(r'(![A-Za-z])\w+', formatted_text)
    function = ""
    if results is not None:
        function = results.group(0)
    else:
        return  # TODO: add ability to guess the function name based on the parameters

    if function in dict_simple_macros.keys():
        output(dict_macros[function])

        return dict_simple_macros[function], []

    raw_args = re.findall(r'({.+})|(~[\w-]+)', formatted_text)

    args = []
    for primary_result, secondary_result in raw_args:
        if primary_result == '':
            args.append(primary_result)
         else:
             args.append(secondary_result)

    dict_macros[function](*args)
    return dict_macros[function], args




def interpret_set_macro(macro):
    macro


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pass
# See PyCharm help at https://www.jetbrains.com/help/pycharm/