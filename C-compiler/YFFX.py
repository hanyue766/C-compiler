'''
算术表达式改进文法：
    E -> TE1
    E1 -> +TE1|-TE1|&
    T -> FT1
    T1 -> *FT1|/FT1|%FT1|&
    F -> (E)|DIGIT|ID

布尔表达式改进文法：
    B -> HB1
    B1 -> && B | &
    H -> GH1
    H1 -> || H | &
    G -> F G1 | !B | (B)
    G1->ROP F|$
    ROP -> < | > | == | !=|>=|<=

声明语句文法：
    X -> YZ;
    Y -> int|char|bool
    Z -> MZ1
    Z1 -> ,Z|&
    M -> ID M1
    M1 -> = E|&

赋值语句文法：
    R -> R1R2;
    R1->ID = ER2
    R2->,R1 | $
语句文法：
    Q->idO | $
    O->++|--|$
    I -> if(B){A}ELSE | while(B){A} | for(RB;Q){A}
    ELSE->else{A}|$
    A -> CA|&
    C -> X|R|I          |I1|O1

输入输出语句：
    I1->scanf("%ID",&ID);
    O1->printf("%ID",ID);|$

main函数文法：
    S->void main ( ) { A }



I1:输入语句
O1:输出语句

算术表达式文法：

E: 表示算术表达式。
E1: 表示算术表达式的后续部分。
T: 表示项（term）。
T1: 表示项的后续部分。
F: 表示因子。
布尔表达式文法：

B: 表示布尔表达式。
B1: 表示布尔表达式的后续部分。
H: 表示逻辑或操作。
H1: 表示逻辑或操作的后续部分。
G: 表示逻辑与操作。
G1: 表示关系操作符和因子的组合。
ROP: 表示关系操作符。
声明语句文法：

X: 表示声明语句。
Y: 表示声明语句的类型（int、char、bool）。
Z: 表示声明语句的变量列表。
Z1: 表示变量列表的后续部分。
M: 表示变量的标识符。
M1: 表示变量的初始化部分。
赋值语句文法：

R: 表示赋值语句。
R1: 表示赋值语句的左侧（标识符）。
R2: 表示赋值语句的右侧（表达式）。
语句文法：

Q: 表示语句。
O: 表示递增（++）或递减（--）操作。
I: 表示条件语句（if）、循环语句（while、for）。
ELSE: 表示条件语句的else部分。
A: 表示语句块。
C: 表示声明语句、赋值语句或条件语句。
main函数文法：

S: 表示main函数。
void main ( ) { A }: 表示main函数的基本结构。
'''
from CFFX import token_table_instance
import json

token_list = []
token_index = 0
token = []
wrong = []
temporary = ''  # 存储一些需要用到的临时变量
temporary1 = ''  # 存储一下变量赋值时变量的类型
# 语义
variable_table = []  # [变量名, 变量类型,加上变量的作用域]，存储声明的变量，作用域用数字来标识
scope = 0  # 存储当前作用域
semAnalyse = []
variable_type = ''  # 存储的临时变量类型
# 四元式
temp_var = 0
NXQ = 0
quaternion = []  # 四元式列表


def newtemp():
    global temp_var
    temp_var += 1
    return 'T' + str(temp_var)


def GETCODE(OP, ARG1, ARG2, RESULT):
    global NXQ
    quaternion.insert(NXQ, [OP, ARG1, ARG2, RESULT])
    NXQ += 1


def lookup(varname):  # 判断变量是否已经定义
    for i in variable_table:
        if i[0] == varname:
            return True
    return False


def clear():
    global token_list, token_index, token, wrong, variable_table, semAnalyse
    global variable_type, temp_var, NXQ, quaternion, temporary, temporary1, scope
    token_list = []
    token_index = 0
    token = []
    wrong = []
    temporary = ''  # 存储一些需要用到的临时变量
    temporary1 = ''
    # 语义
    variable_table = []
    scope = 0
    semAnalyse = []
    variable_type = ''
    # 四元式
    temp_var = 0
    NXQ = 0
    quaternion = []  # 四元式列表


def remove_variable_table_by_scope(remove_scope):  # 函数功能，在作用域结束时，删除变量在表中的声明
    global variable_table
    variable_table[:] = [variable for variable in variable_table if variable[2] != remove_scope]


def get_token():
    clear()
    with open('./tokenList.txt', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            token_list.append(line.replace('\n', '').split(' '))
    print(token_list)


def GetNextToken():
    global token_index
    if token_index >= len(token_list):
        return
    token_index += 1
    return token_list[token_index - 1]


# 要查找变量类型的函数
def get_variable_type(variable_name):
    for entry in variable_table:
        if entry[0] == variable_name:
            return entry[1]
    return None  # 如果变量名不存在于 variable_table 中


def error(st=''):
    global token_index
    if st != '':
        token_index -= 1
        line = int(token_list[token_index][2])
        wrong.append('line:' + str(line) + '   缺少' + st)
    else:
        wrong.append('错误')


def A():
    global token
    if token[0] in ['int', 'char', 'bool', 'if', 'while', 'for', 'scanf', 'printf'] or token[
        1] == '800':  # 当识别到的不是预定义的关键字时是800
        C()
        A()


def O1():
    global token, temporary
    if token[0] == 'printf':
        token = GetNextToken()
        if token[0] != '(':
            error('(')
        token = GetNextToken()
        if len(token[0]) != 4:  # 不是按指定格式输出
            wrong.append('line: ' + str(token[2]) + '    printf语句引号内容出错' + token[0])
        else:
            part = gettokenpart(0)
            if part != '\"':  # 判断左引号
                error('\"')
            part = gettokenpart(1)
            if part != '%':
                error('%')
            part = gettokenpart(2)
            if part == 'd':
                temporary = 'int'  # 存储当前的输出类型
            elif part == 'c':
                temporary = 'char'
            else:
                temporary = part
            if part != 'd' and part != 'c':
                wrong.append('line: ' + str(token[2]) + '    输出类型错误' + token[0])
            part = gettokenpart(3)
            if part != '\"':
                error('\"')
        token = GetNextToken()
        if token[0] != ',':
            error(',')
        token = GetNextToken()
        # ID已经声明的变量值
        id = token[0]  # 存储当前分析的字符，例如g
        if token[1] == '800':  # 说明这个数据是标识符，token[1]指词法分析完成后的变量的标识数字
            if not lookup(token[0]):  # 当前变量不是已经声明的变量
                semAnalyse.append('line: ' + str(token[2]) + '    变量未定义' + token[0])  # 进语义错误，显示变量未声明
            elif get_variable_type(id) != temporary:  # scanf语句的输入和需要的类型不一致
                semAnalyse.append('line: ' + str(token[2]) + '    输出类型和实际类型' + get_variable_type(id) + '不一致')
            else:  # 当前变量是已经声明的变量并且类型一致
                GETCODE('printf', '', '', id)  # 输入的四元式
            token = GetNextToken()
        else:
            error('输出变量名')
            token = GetNextToken()

        if token[0] != ')':
            error(')')
        token = GetNextToken()
        if token[0] != ';':
            error(';')
        token = GetNextToken()


def C():
    global token
    if token[0] in ['int', 'char', 'bool']:
        X()
    elif token[0] in ['if', 'while', 'for']:
        I()
    elif token[0] == 'scanf':  # 识别输入语句
        I1()
    elif token[0] == 'printf':  # 识别输入语句
        O1()
    elif token[1] == '800':
        R()
    else:
        error()


def gettokenpart(index):  # 获取字符串部分的下一部分
    global token
    if index >= len(token[0]):
        return
    index += 1
    return token[0][index - 1]


def I1():
    global token, temporary
    if token[0] == 'scanf':
        token = GetNextToken()
        if token[0] != '(':
            error('(')
        token = GetNextToken()
        if len(token[0]) != 4:  # 不是按指定格式输入
            wrong.append('line: ' + str(token[2]) + '    scanf语句引号内容出错' + token[0])
        else:
            part = gettokenpart(0)
            if part != '\"':  # 判断左引号
                error('\"')
            part = gettokenpart(1)
            if part != '%':
                error('%')
            part = gettokenpart(2)
            if part == 'd':
                temporary = 'int'  # 存储当前的输入类型
            elif part == 'c':
                temporary = 'char'
            else:
                temporary = part
            if part != 'd' and part != 'c':
                wrong.append('line: ' + str(token[2]) + '    输入类型不支持' + token[0])
            part = gettokenpart(3)
            if part != '\"':
                error('\"')
        token = GetNextToken()
        if token[0] != ',':
            error(',')
        token = GetNextToken()
        if token[0] != '&':
            error('&')
        token = GetNextToken()
        # ID已经声明的变量值
        id = token[0]  # 存储当前分析的字符，例如g
        if token[1] == '800':  # 说明这个数据是标识符，token[1]指词法分析完成后的变量的标识数字
            if not lookup(token[0]):  # 当前变量不是已经声明的变量
                semAnalyse.append('line: ' + str(token[2]) + '    变量未定义' + token[0])  # 进语义错误，显示变量未声明
            elif get_variable_type(id) != temporary:  # scanf语句的输入和需要的类型不一致
                semAnalyse.append('line: ' + str(token[2]) + '    输入类型和需要类型' + get_variable_type(id) + '不一致')
            else:  # 当前变量是已经声明的变量并且类型一致
                GETCODE('scanf', '', '', id)  # 输入的四元式
            token = GetNextToken()
        else:
            error('输入变量名')
            token = GetNextToken()

        if token[0] != ')':
            error(')')
        token = GetNextToken()
        if token[0] != ';':
            error(';')
        token = GetNextToken()


def X():
    global token
    if token[0] in ['int', 'char', 'bool']:
        Y()
        Z()
        if token[0] != ';':
            error(';')
        token = GetNextToken()
    else:
        error('关键声明语句')


def Y():
    global token, variable_type
    if token[0] in ['int', 'char', 'bool']:
        variable_type = token[0]
        token = GetNextToken()
    else:
        error('关键声明语句')


def Z():
    global token
    if token[1] != '800':
        error('标识符')
    M()
    Z1()


def M():
    global token, variable_type
    if token[1] == '800':
        id = token[0]
        if not lookup(token[0]):
            variable_table.append([token[0], variable_type, scope])  # 将未声明的变量存储到数组中
            token_table_instance.set_symbol_domain(token[0], scope)
            token_table_instance.set_symbol_val(token[0], variable_type)

        else:
            semAnalyse.append('line: ' + str(token[2]) + '    重定义变量' + token[0])
        token = GetNextToken()
        M1(id)
    else:
        error('标识符')


def M1(id):
    global token
    if token[0] == '=':
        token = GetNextToken()
        es = E()
        GETCODE('=', es, '', id)


def E():
    global token
    if token[0] == '(' or token[1] in ['800', '500']:  # 是标识符或者常量
        e1i = T()
        es = E1(e1i)
        return es
    elif token[1] == '600':  # 说明是char类型的输入
        id = token[0]
        token = GetNextToken()
        return id[1]
    else:
        error()


def T():
    global token
    if token[0] == '(' or token[1] in ['800', '500']:
        t1i = F()
        ts = T1(t1i)
        return ts
    elif token[1] in ['600', '700']:
        semAnalyse.append('line: ' + str(token[2]) + '    变量类型不匹配' + token[0])
        token = GetNextToken()
    else:
        error()


def F():
    global token
    if token[0] == '(':
        token = GetNextToken()
        fval = E()
        if token[0] != ')':
            error(')')
        token = GetNextToken()
        return fval
    elif token[1] in ['800', '500']:
        if token[1] == '800':
            if not lookup(token[0]):
                message_to_find = 'line: ' + str(token[2]) + '    变量未定义' + token[0]  # 信息是否已存在
                if message_to_find not in semAnalyse:
                    semAnalyse.append('line: ' + str(token[2]) + '    变量未定义' + token[0])
        fval = token[0]
        token = GetNextToken()
        return fval
    else:
        error('数字标识符或左括号')


def T1(t11i):
    global token
    if token[0] in ['*', '/', '%']:
        temp = token[0]
        if token[0] != '*':
            token = GetNextToken()
            if token[0] == '0':
                semAnalyse.append('line: ' + str(token[2]) + '    除数为0')
        else:
            token = GetNextToken()
        fval = F()
        t1i = newtemp()
        if temp == '*':
            GETCODE('*', t11i, fval, t1i)
        elif temp == '/':
            GETCODE('/', t11i, fval, t1i)
        else:
            GETCODE('%', t11i, fval, t1i)
        t1s = T1(t1i)
        return t1s
    else:
        return t11i


def E1(e11i):
    global token
    if token[0] in ['+', '-']:
        temp = token[0]
        token = GetNextToken()
        tval = T()
        e1i = newtemp()
        if temp == '+':
            GETCODE('+', e11i, tval, e1i)
        else:
            GETCODE('-', e11i, tval, e1i)
        es = E1(e1i)
        return es
    else:
        return e11i


def Z1():
    global token
    if token[0] == ',':
        token = GetNextToken()
        Z()


def R():
    global token
    R1()
    R2()
    if token[0] != ';':
        error(';')
    token = GetNextToken()


def R1():
    global token
    if token[1] != '800':  # 当前不是标识符
        error('标识符')
    else:
        if not lookup(token[0]):
            semAnalyse.append('line: ' + str(token[2]) + '    变量未定义' + token[0])
    id = token[0]
    token = GetNextToken()
    if token[0] != '=':
        error('=')
    token = GetNextToken()
    es = E()
    GETCODE('=', es, '', id)
    R2()


def R2():
    global token
    if token[0] == ',':
        token = GetNextToken()
        R1()


def I():
    global token, scope
    if token[0] == 'if':
        token = GetNextToken()
        if token[0] != '(':
            error('(')
        token = GetNextToken()
        val = B()

        GETCODE('jnz', val, '', NXQ + 2)
        GETCODE('j', '_', '_', 0)

        if token[0] != ')':
            error(')')
        token = GetNextToken()
        if token[0] != '{':
            error('{')
        scope += 1
        token = GetNextToken()
        A()

        GETCODE('j', '_', '_', -1)

        if token[0] != '}':
            error('}')
        remove_variable_table_by_scope(scope)
        scope -= 1
        token = GetNextToken()
        ELSE()
    elif token[0] == 'while':
        token = GetNextToken()
        if token[0] != '(':
            error('(')
        token = GetNextToken()
        temp = NXQ
        bval = B()

        GETCODE('jnz', bval, '_', NXQ + 2)
        GETCODE('j', '_', '_', -2)

        if token[0] != ')':
            error(')')
        token = GetNextToken()
        if token[0] != '{':
            error('{')
        scope += 1
        token = GetNextToken()
        A()

        GETCODE('j', '_', '_', temp)

        if token[0] != '}':
            error('}')
        remove_variable_table_by_scope(scope)
        scope -= 1
        token = GetNextToken()

        for i in reversed(quaternion):
            if i[3] == -2:
                i[3] = NXQ
                break
    elif token[0] == 'for':
        token = GetNextToken()
        if token[0] != '(':
            error('(')
        token = GetNextToken()
        R()
        temp1 = NXQ
        bval = B()
        GETCODE('jnz', bval, '_', -1)  # 真
        GETCODE('j', '_', '_', -2)  # 假

        if token[0] != ';':
            error(';')
        token = GetNextToken()
        temp2 = NXQ
        Q()
        GETCODE('j', '_', '_', temp1)
        for i in reversed(quaternion):  # 找真出口
            if i[3] == -1:
                i[3] = NXQ
                break

        if token[0] != ')':
            error(')')
        token = GetNextToken()
        if token[0] != '{':
            error('{')
        scope += 1
        token = GetNextToken()
        A()

        GETCODE('j', '_', '_', temp2)
        for i in reversed(quaternion):  # 找假出口
            if i[3] == -2:
                i[3] = NXQ
                break

        if token[0] != '}':
            error('}')
        remove_variable_table_by_scope(scope)
        scope -= 1
        token = GetNextToken()
    else:
        error('控制语句')


def Q():
    global token
    if token[1] == '800':
        val = token[0]
        token = GetNextToken()
        O(val)


def O(val):
    global token
    if token[0] in ['++', '--']:
        GETCODE(token[0], val, '_', val)
        token = GetNextToken()
    elif token[0] == '=':
        token = GetNextToken()
        eval = E()
        GETCODE('=', eval, '_', val)


def ELSE():
    global token, scope
    if token[0] == 'else':
        token = GetNextToken()
        if token[0] != '{':
            error('{')
        scope += 1
        token = GetNextToken()
        for i in reversed(quaternion):  # 假出口
            if i[3] == 0:
                i[3] = NXQ
                break
        A()
        for i in reversed(quaternion):  # goto
            if i[3] == -1:
                i[3] = NXQ
                break
        if token[0] != '}':
            error('}')
        remove_variable_table_by_scope(scope)
        scope -= 1
        token = GetNextToken()
    else:
        for i in reversed(quaternion):  # 假出口
            if i[3] == 0:
                i[3] = NXQ
                break
        for i in reversed(quaternion):  # goto
            if i[3] == -1:
                i[3] = NXQ
                break


def B():
    hval = H()
    b1val = B1(hval)
    return b1val


def H():
    gval = G()
    h1val = H1(gval)
    return h1val


def G():
    global token
    if token[0] == '!':
        token = GetNextToken()
        temp = newtemp()
        bval = B()
        GETCODE('!', bval, '_', temp)
        return temp
    elif token[0] == '(':
        token = GetNextToken()
        bval = B()
        if token[0] != ')':
            error()
        token = GetNextToken()
        return bval
    elif token[1] == '800' or token[1] == '500':
        fval = F()
        g1val = G1(fval)
        return g1val
    else:
        error('布尔表达式')


def G1(fval):
    global token
    if token[0] in ['<', '>', '==', '!=', '>=', '<=']:
        op = ROP()
        f1val = F()
        temp = newtemp()
        GETCODE(op, fval, f1val, NXQ + 3)
        GETCODE('=', '0', '_', temp)
        GETCODE('j', '_', '_', NXQ + 2)
        GETCODE('=', '1', '_', temp)
        return temp
    else:
        return fval


def ROP():
    global token
    if token[0] in ['<', '>', '==', '!=', '>=', '<=']:
        temp = token[0]
        token = GetNextToken()
        return temp
    else:
        error('操作符')


def H1(gval):
    global token
    if token[0] == '&&':
        token = GetNextToken()
        hval = H()
        temp = newtemp()
        GETCODE('&&', gval, hval, temp)
        return temp
    else:
        return gval


def B1(hval):
    global token
    if token[0] == '||':
        token = GetNextToken()
        temp = newtemp()
        bval = B()
        GETCODE('||', hval, bval, temp)
        return temp
    else:
        return hval


def parser():
    global token, scope
    token = GetNextToken()
    if token[0] != 'void':
        error('void')
    token = GetNextToken()
    if token[0] != 'main':
        error('main')
    token = GetNextToken()
    if token[0] != '(':
        error('(')
    token = GetNextToken()
    if token[0] != ')':
        error(')')
    token = GetNextToken()
    if token[0] != '{':
        error('{')
    scope += 1
    token = GetNextToken()
    A()
    if token[0] != '}':
        error('}')

    remove_variable_table_by_scope(scope)  # 先删除当前scope对应的元素
    scope -= 1  # 然后进行减一，返回之前的作用域
    token = GetNextToken()

    if token[0] == '#':
        print('分析完成！')
    else:
        error()


def write_quater():
    with open('中间代码.txt', 'w', encoding='utf-8') as f:
        #  f.write(json.dumps(quaternion))
        # f.close()
        for quarter in quaternion:
            f.write(json.dumps(quarter) + '\n')


def print_token_table(token_table):
    print("Token Table:")
    print("{:<15} {:<10} {:<10} {:<10} {:<10}".format("Word", "Code", "Line", "Domain", "Val"))
    print("-" * 55)

    for word, info in token_table.items():
        line_info = "{:<15} {:<10} {:<10} {:<10} {:<10}".format(
            word, info['code'], info['line'], info['domain'], info.get('val', ''))
        print(line_info)


def main():
    get_token()  # 从文件里获取词法分析的结果
    parser()  # 进行分析
    write_quater()  # 存储中间代码
    # for i in variable_table:
    # print(i)
    for i in wrong:  # 语法错误
        print("语法错误：")
        print(i)

    for i in semAnalyse:  # 语义错误
        print("语义错误：")
        print(i)
    for i in range(len(quaternion)):  # 四元式
        print(i, '   ', quaternion[i])
    # print_token_table(token_table_instance.token_table)


if __name__ == '__main__':
    main()
