'''
Created by:     Donna Saban
                sabandonna@gmail.com
'''
import math as MATH
import os
import sys

tok_end, tok_begin, tok_add, tok_sub, tok_mul , tok_div, tok_mod, tok_varint, tok_with, tok_varstr, tok_input, tok_print, tok_println,  \
tok_store, tok_in, tok_raise, tok_root, tok_mean, tok_dist, tok_and, tok_eof, tok_eos, tok_string, tok_int, tok_identifier, tok_error = range(26)

display_node = [ "PROGRAM_END", "PROGRAM_BEGIN", "BASIC_OPERATOR_ADD", "BASIC_OPERATOR_SUB", "BASIC_OPERATOR_MUL",  "BASIC_OPERATOR_DIV", "BASIC_OPERATOR_MOD", 
                "DECLARATION_INT", "DECLARATION_ASSIGN_WITH_KEY", "DECLARATION_STRING", "INPUT", "OUTPUT", "OUTPUT_WITH_LINE", "ASSIGN_KEY", "ASSIGN_VAR_KEY",
                "ADVANCED_OPERATOR_EXP", "ADVANCED_OPERATOR_ROOT", "ADVANCED_OPERATOR_AVE", "ADVANCED_OPERATOR_DIST", "DISTANCE_SEPARATOR", "END_OF_FILE ", 
                "END_OF_STATEMENT", "STRING", "NUMBER", "IDENTIFIER", "DATA_ERROR" ]

keyword = {'END': tok_end,          'BEGIN': tok_begin,
            'ADD': tok_add,         'SUB': tok_sub,
            'MUL': tok_mul,         'DIV': tok_div,
            'MOD': tok_mod,         'VARINT': tok_varint,
            'WITH': tok_with,       'VARSTR': tok_varstr,
            'INPUT': tok_input,     'PRINT': tok_print,
            'PRINTLN': tok_println, 'STORE': tok_store,
            'IN': tok_in,           'RAISE': tok_raise,
            'ROOT': tok_root,       'MEAN': tok_mean,
            'DIST': tok_dist,       'AND': tok_and }

var_pool = []           # FORMAT: [type, name, value]
op_pool = []            # FORMAT: [type, value]
token_pool = []         # FORMAT: (type, name, line)
pool = []               # FORMAT: (type, name, line)
tokenizer = []
error_display = []
input_string = []
sub_list_op = []
end_stat = []
line = 1                # Initial Value of line number for lexer
pointer = " "           # Initial Value of reference character for lexer
output_strings = " "
begin_ctr = None
end_ctr = None
f_ptr = None
root = None
ctr = None
Name = None
Value  = None
Line = None


#-----------------------------------------------------------------------------------------MAIN_DRIVER
def main():
    global f_ptr, tokenizer, output_strings, pool
    print("=============================== INTERPOL INTERPRETER STARTED =============================")

    # Recieves the file and evaluate the extension. Open and Read File.
    input_file = input("Enter INTERPOL file (.ipol): ").strip()
    extract_extn = input_file.split(".")
    extension = extract_extn[-1].lower()

    if not  os.path.exists(input_file): 
        print("File does not exist") 
        sys.exit()
    elif extension != 'ipol': 
        print("Input file does not end with .ipol")
        sys.exit()
    elif os.stat(input_file).st_size == 0:
        print("File is empty")
        sys.exit()
    else:
        f = open(input_file, "r", 4096)
        f_ptr = f
        
    #COMBINATOR: Receives Token from Lexer and pass to PARSER, EVALUATOR, and TOKEN DISPLAY
    print("======================================== INTERPOL OUTPUT ===================================")
    print("----------------------------------------- OUTPUT START ------------------------------------>")

    while True:
        token = lexer()
        error_display.append(token[1])
        token_pool.append(token)
        
        input_string = error_display.copy()
        output_strings = " ".join([str(x) for x in input_string])

        # List for TOKEN DISPLAY
        tokenizer.append(token)

        if token[0] == tok_error: error(token[2], "Invalid syntax",  output_strings)
        #if token[0] == tok_end and token[0] == tok_eof: break
        # END EOF : statement without delimiter
        if token[0] == tok_eof:
            end_stat = token_pool.copy()
            if len(end_stat) == 2:
                if end_stat[0][0] == tok_end: break 
                elif end_stat[0][0] == tok_begin: error(token[2], "Invalid end of file", output_strings)
                else: error(token[2], "Invalid syntax",  output_strings)

        # END statement with delimiter
        if end_ctr:
            if token[0] == tok_eof: break
            elif token[0] == tok_eos: continue
            else: error(token[2], "Invalid end of file", output_strings) # Statement after END was declared
        else:
            if token[0] == tok_eof: error(token[2], "Invalid end of file", output_strings) # EOF without END

        # Display the result from parser line by line
        if token[0] == tok_eos:
            pool = token_pool.copy()
            result = parse()
            if result == None: pass
            if root == tok_print: print(result, end = " ")
            if root == tok_println: print(result, end = "")
            error_display.clear()
            token_pool.clear()
    print('\n' + "<------------------------------------------ OUTPUT END ----------------------------------")
    # TOKEN DISPLAY: Display all the token of valid expression
    print("===================================== INTERPOL LEXEMES/TOKENS TABLE ======================")
    print("LINE NO.                            TOKENS                      LEXEMES")
    for l in tokenizer:
        t = l[0]
        lexeme = l[1]
        t_l = l[2]
        print('{:<30}  {:<30}  {:<50}'.format(t_l, display_node[t], lexeme))
    # User Variables Display
    print("============================================ SYMBOLS TABLE ==================================")
    print("VARIABLE NAME                                        TYPE                VALUE")
    for i in var_pool:
        var_n = i[1]
        var_t = i[0]
        var_v = i[2]
        if  var_t == tok_string: node_t = 'STRING'
        if  var_t == tok_int: node_t = 'INTEGER'
        print('{:<50}  {:<20}  {:<50}'.format(var_n, str(node_t), str(var_v)))
    print("=============================== INTERPOL INTERPRETER TERMINATED ============================")
#------------------------------------------------------------------------------------------ERROR_DISPLAY
# Function to display all run time error 
def error(refline, msg, error_display):
    print( msg + " at line number [ %d ] " % refline )
    print("----> %s" % error_display)
    sys.exit()


#------------------------------------------------------------------------------------------PARSER
def parse():
    global begin_ctr, end_ctr, root, ctr, end_ctr, op_pool
    root = None
    ctr = 0
    op_pool = []

    LENGHT = len(pool)
    Name = pool[ctr][0]
    Line = pool[ctr][2]

    if LENGHT < 3:
        if Name == tok_begin:
            if not begin_ctr:
                begin_ctr = 1
            return None
        elif Name == tok_end: 
            if not end_ctr:
                end_ctr = 1
            return None
        elif Name == tok_eos: return None
        else: return error(Line, "Invalid syntax",  output_strings)
    else: 
        if not begin_ctr: return error(Line, "Invalid syntax", output_strings) 
        if Name == tok_varint:
            root = tok_varint
            return declaration()
        elif Name == tok_varstr:
            root = tok_varstr
            return declaration()
        elif Name == tok_print:
            root = tok_print
            return output()
        elif Name == tok_println:
            root = tok_println
            return output()
        elif Name == tok_input:
            root = tok_input
            return var_i()
        elif Name == tok_store:
            root = tok_store
            return store()
        else: return error(Line, "Invalid syntax", output_strings) 

# Iterate the Token Pool (pool) - (left derivation) 
def counter():
    global  ctr, Name, Value, Line
    ctr += 1
    Name = pool[ctr][0]
    Value = pool[ctr][1]
    Line = pool[ctr][2]

# Check if the value (ref) exist in Variable List (var_pool): return value index
def user_variables(ref):
    for x in var_pool:
        if ref == x[1]: return var_pool.index(x)

# Function for Validity of Statement Lenght per Operation Type
def statement_lenght_error(val):
    statement_len = len(pool)
    if statement_len > val: return error(Line, "Invalid syntax", output_strings)

# FORMAT: STORE <expression> IN <variable>
def store():
    val = None
    type_l = None
    var_key_pos = []
    in_key_pos  = []

    counter()
    if Name in [tok_int, tok_string, tok_identifier]:
        if Name in [tok_int, tok_string]:
            val = Value
            if Name == tok_int: type_l = tok_int
            if Name == tok_string: type_l = tok_string
        if Name == tok_identifier:
            ref_l = Value
            i = user_variables(ref_l)
            if i == None: return error(Line, "Variable is not declared ", output_strings)
            val = var_pool[i][2]
            type_l = var_pool[i][0]
        
        counter()
        if Name == tok_in: pass
        else: return error(Line, "Invalid syntax ", output_strings)

        counter()
        if Name == tok_identifier:
            ref_r = Value
            store_key_operation(ref_r, type_l, val)
        else: return error(Line, "Invalid syntax", output_strings)

        counter()
        if Name == tok_eos: return None
        else: return error(Line, "Invalid syntax ", output_strings)
        
    elif Name in [tok_add, tok_sub, tok_mul, tok_div, tok_mod, tok_raise, tok_root, tok_mean, tok_dist]:
        op_pool.append([Name, Value])
        math_op()
        op_pool.reverse()
        var_key_pos = op_pool.pop(0)
        in_key_pos = op_pool.pop(0)
        if in_key_pos[0] != tok_in: return error(Line, "Invalid syntax ", output_strings)
        if var_key_pos[0] != tok_identifier: return error(Line, "Invalid syntax ", output_strings)
        op_pool.reverse()
        val = iterate_pool()
        type_l = tok_int
        ref_r = var_key_pos[1]
        store_key_operation(ref_r, type_l, val)
    else: return error(Line, "Invalid syntax ", output_strings)
    
# Function to update variable pool(var_pool) 
def store_key_operation(ref_r, type_l, val):
    i = user_variables(ref_r)
    if i == None: return error(Line, "A variable must be declared before use", output_strings)
    # Check if user input type is the same with the chosen variable 
    if (var_pool[i][0] == tok_int and type_l == tok_int) or (var_pool[i][0] == tok_string and type_l == tok_string): r = val
    else: return error(Line, "Incompatible data type ", output_strings)
    # Update variable list (var_pool) with new value
    for id, (t, n, v) in enumerate(var_pool):
        if n == ref_r: var_pool[id][2] = r

# Funtion for User Input. FORMAT: INPUT <variable_name>
def var_i():
    global var_pool
    i = None
    ref = None
    val = None
    v = 3
    statement_lenght_error(v)

    counter()
    if Name == tok_identifier:
        ref = Value
    else: return error(Line, "Invalid syntax ", output_strings)
    ptr = user_variables(ref) 
    if ptr == None: return error(Line, "Variable is not declared ", output_strings)

    # Ask for user Input
    i = input()
    if not i: return error(Line, "Invalid data type input ", output_strings)
        
    if var_pool[ptr][0] == tok_int:
        try: val = int(i)
        except ValueError: return error(Line, "Incompatible data type ", output_strings)
    if var_pool[ptr][0] == tok_string:
        try: 
            val = str(i)
        except ValueError: return error(Line, "Incompatible data type ", output_strings)
        if val.isascii() == False: return error(Line, "Invalid data type input  ", output_strings)
    # Update variable list (var_pool) with new value
    for id, (t, n, v) in enumerate(var_pool):
        if n == ref: var_pool[id][2] = val
    

# Function for Variable Declaration
def declaration():
    global var_pool
    node = None
    ref = None
    n = None
    iden_ref = None
    v = 5
    
    counter()
    if Name == tok_identifier:
        ref = Value
        i = user_variables(ref)
        if i == None: 
            if root == tok_varint: n = tok_int
            if root == tok_varstr: n = tok_string
        else: return error(Line, "Duplicate variable declaration ", output_strings)
    else: return error(Line, "Invalid syntax", output_strings)

    counter()
    if Name == tok_eos:
        node = None
        var_pool.append([n, ref, None])
        return None
    elif Name == tok_with: pass
    else: return error(Line, "Invalid syntax", output_strings)

    counter()
    if root == tok_varstr:
        statement_lenght_error(v)
        if Name == tok_string:
            node = Value
            var_pool.append([n, ref, node])
            return None
        elif Name == tok_identifier:
            iden_ref = Value
            i = user_variables(iden_ref)
            if i == None: return error(Line, "Variable is not declared ", output_strings)
            if var_pool[i][0] == tok_string:
                try: val = str(var_pool[i][2])
                except ValueError: return error(Line, "Incompatible data type  ", output_strings)
            else: return error(Line, "Invalid data type ", output_strings)
            var_pool.append([n, ref, val])
            return None
        else: return error(Line, "Incompatible data type", output_strings)
    if root == tok_varint:
        if Name == tok_int:
            statement_lenght_error(v)
            node = Value
            var_pool.append([n, ref, node])
            return None
        elif Name == tok_identifier:
            statement_lenght_error(v)
            iden_ref = Value
            i = user_variables(iden_ref)
            if i == None: return error(Line, "Variable is not declared ", output_strings)
            if var_pool[i][0] == tok_int:
                try: val = int(var_pool[i][2])
                except ValueError: return error(Line, "Incompatible data type  ", output_strings)
            else: return error(Line, "Invalid data type ", output_strings)
            var_pool.append([n, ref, val])
            return None
        elif Name in [tok_add, tok_sub, tok_mul, tok_div, tok_mod, tok_raise, tok_root, tok_mean, tok_dist]:
            op_pool.append([Name, Value])
            math_op()
            val = iterate_pool()
            var_pool.append([n, ref, val])
            return None
        else: return error(Line, "Incompatible data type", output_strings)

# Function for User Output
def output():
    str_lit = None
    counter()
    v = 3
    if not str_lit:
        if Name == tok_string:
            statement_lenght_error(v)
            str_lit = Value
            return output_display(str_lit) 
        elif Name == tok_int:
            statement_lenght_error(v)
            str_lit = Value
            return output_display(str_lit) 
        elif Name == tok_identifier:
            statement_lenght_error(v)
            iden_ref = Value
            i = user_variables(iden_ref)
            if i == None: return error(Line, "Variable is not declared ", output_strings)
            str_lit = var_pool[i][2]
            return output_display(str_lit) 
        elif Name in [tok_add, tok_sub, tok_mul, tok_div, tok_mod, tok_raise, tok_root, tok_mean, tok_dist]:
            op_pool.append([Name, Value])
            math_op()
            str_lit = iterate_pool()
            return output_display(str_lit) 
        else: return error(Line, "Invalid syntax", output_strings)
    else: return error(Line, "Invalid syntax", output_strings) 

# Function  to display result from Function output
def output_display(str_lit):
    if root == tok_print: return str_lit
    elif root == tok_println: return str(str_lit) + '\n'
    else: return error(Line, "Invalid syntax", output_strings)

#----------------------------------------------------------------------------MATH_EXPRESSION/STATEMENT_EVALUATOR
def math_op():
    global op_pool
    counter()
    if  Name in [tok_add, tok_sub, tok_mul, tok_div, tok_mod, tok_raise, tok_root, tok_mean, tok_dist, tok_int, tok_identifier, tok_and, tok_in]:
        op_pool.append([Name, Value])
        math_op()
    elif Name == tok_eos: pass
    else: return error(Line, "Invalid expression ", output_strings)

# Use Right derivation for math operator statement evaluation    
def iterate_pool():
    l = None
    r = None
    num = None
    sub_list_op = []
    node = []
    current_node = []
        
    for id, (t, n) in enumerate(op_pool):
        if t in [tok_add, tok_sub, tok_mul, tok_div, tok_mod, tok_raise, tok_root, tok_mean, tok_dist] : sub_list_op.append(id)
        
    sub_list_op.reverse()
    try:     
        for i in sub_list_op:
            node.clear()
            current_node = op_pool.copy()

            if op_pool[i][0] in [tok_add, tok_sub, tok_mul, tok_div, tok_mod, tok_raise, tok_root]:
                l = op_pool[i + 1][1]
                r = op_pool[i + 2][1]
                # check if operator with two parameters (l and r) is using variable in (user_variable)
                if op_pool[i + 1][0] == tok_identifier:
                    i_l = user_variables(l)
                    if i_l == None: return error(Line, "Variable is not declared ", output_strings)
                    if var_pool[i_l][0] == tok_int: l = var_pool[i_l][2]
                    else: return error(Line, "Incompatible data type ", output_strings)
                if op_pool[i + 2][0] == tok_identifier:
                    i_r = user_variables(r)
                    if i_r == None: return error(Line, "Variable is not declared ", output_strings)
                    if var_pool[i_r][0] == tok_int: r = var_pool[i_r][2]
                    else: return error(Line, "Incompatible data type ", output_strings)
                
            if op_pool[i][0] in [tok_mean, tok_dist]:
                extd_node = op_pool[i + 1:]
                # Check if operator using more then 2 parameters is using variable in (user_variable)
                for index, (x, y) in enumerate(extd_node):
                    if x == tok_identifier:
                        i_node = user_variables(y)
                        if i_node == None: return error(Line, "Variable is not declared ", output_strings)
                        if var_pool[i_node][0] != tok_int: return error(Line, "Incompatible data type", output_strings)
                        node.append(var_pool[i_node][2])
                    else: node.append(y)

            # Selection of Math Operators
            if op_pool[i][0] == tok_add:
                op_pool[i][1] = l + r
            elif op_pool[i][0] == tok_sub:
                op_pool[i][1] = l - r
            elif op_pool[i][0] == tok_mul:
                op_pool[i][1] = l * r
            elif op_pool[i][0] == tok_div:
                # Exception: Division to zero
                try:
                    if r == "0": pass
                    else: op_pool[i][1] = l // r
                except:
                    return error(Line, "Invalid arithmetic operation ", output_strings)
            elif op_pool[i][0] == tok_mod:
                # Exception: Modulo to zero
                try:
                    if r == "0": pass
                    else: op_pool[i][1] = l % r
                except:
                    return error(Line, "Invalid arithmetic operation ", output_strings)
            elif op_pool[i][0] == tok_raise:        
                # Exception: ZeroDivisionError: 0.0 cannot be raised to a negative power
                if l == 0 and r < 0: return error(Line, "Invalid arithmetic operation ", output_strings)
                op_pool[i][1] = l ** r
            elif op_pool[i][0] == tok_root:         
                op_pool[i][1] = r ** (1 / l)
            elif op_pool[i][0] == tok_mean: 
                for n in node:
                    try:
                        val = int(n)
                    except: return error(Line, "Invalid arithmetic operation   ", output_strings)
                op_pool[i][1] = sum(node) // len(node)
            elif op_pool[i][0] == tok_dist:  
                if extd_node[2][0] == tok_and: node.pop(2)
                else: return error(Line, "Invalid syntax", output_strings)
                op_pool[i][1] = int(MATH.sqrt(((node[0] - node[2])**2) + ((node[1] - node[3])**2)))
            else: return error(Line, "Invalid arithmetic operation ", output_strings)
            # Variable for every operator statement
            num = op_pool[i][1]
            # Reposition the op_pool content by removing the end node that already process
            if op_pool[i + 1]:
                op_pool_lenght = len(op_pool)
                if op_pool[i][0] in [tok_add, tok_sub, tok_mul, tok_div, tok_mod, tok_raise, tok_root]: 
                    if op_pool_lenght > 2:
                        op_pool.pop(i + 1)
                        op_pool.pop(i + 1)
                    else: op_pool.pop(i)
                if op_pool[i][0] == tok_mean:
                    node_len = len(node)
                    if op_pool_lenght > node_len:
                        for x in range(node_len):
                            op_pool.pop(i + 1)
                    else: op_pool.pop(i)
                if op_pool[i][0] == tok_dist:
                    if op_pool_lenght > 5:
                        op_pool.pop(i + 1)
                        op_pool.pop(i + 1)
                        op_pool.pop(i + 1)
                        op_pool.pop(i + 1)
                        op_pool.pop(i + 1)
                    else: op_pool.pop(i)
                
        # Check if operators are is structuraly adjacent 
        if len(current_node) > 3 and op_pool[0][0] in [tok_add, tok_sub, tok_mul, tok_div, tok_mod, tok_raise, tok_root]: return error(Line, "Invalid expression", output_strings)
        elif len(current_node) > 6 and op_pool[0][0] == tok_dist:  return error(Line, "Invalid expression", output_strings)
        else: return int(num)
    except Exception:
        return error(Line, "Invalid arithmetic operation ", output_strings)

#----------------------------------------------------------------------------------PROGRAM_LEXER
def lexer():
    while pointer.isspace():
        if pointer == '\n':
            read_next()
            return tok_eos, " ", line - 1
        read_next()
    # Refence Line per statement
    tok_line = line
    # Check the first character after space
    if not pointer: return tok_eof, " " , tok_line
    elif pointer == '#': return comment(tok_line)
    elif pointer == '"': return string_lit(pointer, tok_line)
    elif pointer.isalnum() == True: return integer_keyword_iden(pointer, tok_line)
    elif pointer == '-': return sign_int(pointer, tok_line)
    elif pointer == '+': return sign_int(pointer, tok_line)
    else: return tok_error, pointer, tok_line

#Iterate 1 character at a time
def read_next():
    global pointer, line
    pointer = f_ptr.read(1)
    if pointer == '\n':line += 1
    return pointer
# Function for Comment
def comment(tok_line):
    sentence = pointer
    while read_next() != '\n':
        sentence += pointer
        if not pointer: return tok_error, sentence, tok_line
    return lexer()
# Function for selecting String literal
def string_lit(first_char,tok_line):
    sentence = ""
    while read_next() != first_char:
        sentence += pointer
        if (not pointer) or (pointer == '\n'): return tok_error, sentence, tok_line
    read_next()
    if sentence.isascii() == False: return tok_error, sentence, tok_line
    return tok_string, sentence, tok_line
# Function for selecting KEYWORD, INTEGER LITERAL(UNSIGNED), and IDENTIFIER
def integer_keyword_iden(ref, tok_line):
    sentence = ""
    digit = True
    while pointer.isalnum() or pointer == '_':
        sentence += pointer
        if not pointer.isdigit(): digit = False
        read_next()
    if not sentence: return tok_error, sentence, tok_line
    if sentence[0].isdigit():
        if not digit: return tok_error, sentence, tok_line
        num = int(sentence)
        return tok_int, num, tok_line
    if sentence in keyword: return keyword[sentence], sentence, tok_line
    if len(sentence) > 49: return tok_error, sentence, tok_line
    return tok_identifier, sentence, tok_line
# Function for selecting SIGNED INTEGER LITERAL (+/-)
def sign_int(ref, tok_line):
    sentence = ref
    not_num = False
    read_next()
    while pointer.isalnum():
        sentence += pointer
        if pointer.isdigit() == False: not_num = True
        read_next()
    if not sentence: return tok_error, sentence, tok_line
    if not_num == True: return tok_error, sentence, tok_line
    if ref == "-":
        is_num = int(sentence)
        num = -abs(is_num)
    if ref == "+":
        num = int(sentence)
    return tok_int, num, tok_line

#-----------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()