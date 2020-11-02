import re

dict_macros = {'print': print, 'save': 'a{} b{}', 'query_testing': ['Query<char> query_{0};',
                                                           'query_{0}.OR_queries.'
                                                           'push_back(Query<char>::FromString("{0}"));',
                                                           'pattern.queries.push_back(query_{});'
                                                           # A real-life example of how something could be generated
                                                           ]
               }
dict_simple_macros = {}

output = print


# Currently only targets C++ (WIP, will target many more hopefully!)
def default_outputting(function, args):
    to_output = function + '(' + ', '.join(args) + ');'

    output(to_output)


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

    if function in dict_macros.keys():
        if isinstance(dict_macros[function], str):
            output(dict_macros[function].format(*args))
        elif isinstance(dict_macros[function], list):
            output('\n'.join([sub_function.format(*args) for sub_function in dict_macros[function]]))
        else:
            default_outputting(function, args)

            dict_macros[function](*args)

        return dict_macros[function], {'function': function, 'args': args}

    default_outputting(function, args)


interpret_get_macro("!query_testing " + "~test " * 6)


def interpret_set_macro(macro):
    macro


if __name__ == '__main__':
    pass