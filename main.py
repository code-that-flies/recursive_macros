import re
import hashlib


dict_macros = {'print': print, 'save': 'a{} b{}', 'query_testing': ['Query<char> query_{0};',
                                                           'query_{0}.OR_queries.'
                                                           'push_back(Query<char>::FromString("{0}"));',
                                                           'pattern.queries.push_back(query_{});'
                                                           # A real-life example of how something could be generated
                                                           ]
               }
dict_simple_macros = {}

output = print

def add_macro(macro_name, macro_function):
    dict_macros[macro_name] = macro_function

def remove_all_generated_code(raw):
    isFailed = False

    while not isFailed:
        try:
            f = re.search(r'\n\/\/ GENERATED CODE START \/\/\n(.|\s)*\n\/\/ GENERATED CODE END \/\/\n', raw)
            
            raw = raw.replace(f.group(0), "")

        except: # I am using this exception because both https://pythex.org/ and my local python interpreter fail to handle re.find_all() correctly in the case of r'\n\s*\w*[\s::]*\w+::(\w)+\([\w\:s<>,*&]*\).*:?w*{' and other cases, and I tried using different loops without the exception but they failed although I do not now why
            isFailed = True
            
    return raw

def interpret_submacro(formatted_text):
    regex = r'!\w+[\s~\w]+~\w+'
                    
    # regex algorithm for unfiltered function names
    storage = []

    try:
        f = re.search(regex, formatted_text)

        storage.append(f.group(0))
            
        formatted_text = formatted_text.replace(storage[-1], interpret_get_macro(storage[-1]))

    except: # I am using this exception because both https://pythex.org/ and my local python interpreter fail to handle re.findall() correctly in the case of r'\n\s*\w*[\s::]*\w+::(\w)+\([\w\:s<>,*&]*\).*:?w*{' and other cases, and I tried using different loops without the exception but they failed although I do not now why
        pass
            
    if len(storage) > 0:
        return interpret_submacro(formatted_text)
    else:
        return formatted_text
                
            

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
        value = ''
        
        if isinstance(dict_macros[function], str):
            value = dict_macros[function].format(*args)
        elif isinstance(dict_macros[function], list):
            value = '\n'.join([sub_function.format(*args) for sub_function in dict_macros[function]])
        else:
            value = dict_macros[function](*args)
        
        value = interpret_submacro(value)
        return value

    default_outputting(function, args)
    return None


# interpret_get_macro("!print ~test ")

def interpret_set_macro(macro, is_multiline_comment=False):
    name = re.search(r'^\w+(?=:)', macro)
    
    value = re.search(r'(?::).+$', macro).group(0)[1:].strip()
    
    if is_multiline_comment:
        value = value.split('\n')
    
    dict_macros[name] = value
    
def interpret(text, is_multiline_comment=False):
    text_copy = text.strip()
    
    command = text_copy[:3].upper()
    
    if command == 'GET':
        formatted_text = text[text.find('GET') + 3:]
        
        return interpret_get_macro(formatted_text)
    
    elif command == 'SET':
        macro = text[text.find('SET') + 3:]
        
        interpret_set_macro(macro, is_multiline_comment)
        
        return None
    else:
        return None

def generate_hash(str_value):
    return 'hash:' + hashlib.sha224(bytes(str_value, 'utf-8')).hexdigest()


class comment():
    def __init__(self, value, _hash, _type, interpretation, parent):
        self.value = value
        self.hash = _hash
        self.type = _type
        self.parent = parent
        
        self.interpretation = interpretation
        
    
    def restore(self):
        if self.interpretation:
            self.value += '\n// GENERATED CODE START //\n' + self.interpretation + '\n// GENERATED CODE END //\n'
            
        self.parent.value.replace(self.hash, self.value)
    
    @staticmethod
    def from_str(regex, parent, _type, language='c++'):
        value = re.search(regex, parent.value).group(0)
        
        if value is None:
            return None
        
        _hash = generate_hash(value)
        
        parent.value = parent.value.replace(value, _hash)
        
        temp_value = value
        is_multiline_comment = False
        if _type == 'line-comment' and language == 'c++':
            temp_value = value[2:]
        elif _type == 'block-comment' and language == 'c++':
            temp_value = value[2:-2]
            is_multiline_common = True
        interpretation = interpret(temp_value, is_multiline_comment)
        
        return comment(value, _hash, _type, interpretation, parent)
        

    
        
class code():
    
    def __init__(self, value, name, _hash, _type, parent_name='', parent=None):
        self.parent = parent
        self.value = value
        self.hash = _hash
        self._type = _type
        self.parent_name = parent_name
    
    def restore(self):
        self.parent.value.replace(self.hash, self.value)
        
    def update(self, new_value):
        self.value = new_value
        
    @staticmethod
    def from_str(regex, parent, _type, name='', parent_name='', language='c++'):
        value = re.search(regex, parent.value).group(0)
        
        if value is None:
            return None
        
        _hash = generate_hash(value)
        
        parent.value = parent.value.replace(value, _hash)
        
        if (_type == 'class-declaration' or _type == 'struct-declaration') and language == 'c++':
            name = value.split()[1]
            
        if _type == 'function-definition' and language == 'c++':
            results = re.search(r'\w*(::)*\w+::\w+(?=(\([\w<>&*:,\s]*\)))', value).split('::')
            
            name = results[-1]
            
            if parent_name == '' and len(results) > 1:
                parent_name = results[-2]
            if parent.parent_name == '' and len(results) > 2:
                parent.parent_name = results[-3]
                
        return code(value, name, _hash, _type, parent_name, parent)
    

if __name__ == '__main__':
    pass
