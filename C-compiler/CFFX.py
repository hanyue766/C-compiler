from token_table import Symbol, token_table_instance  # 引入符号表,类


class token:
    def __init__(self, word, code, row, col):  # token类，用来存储当前单词，符号，行号和列号
        self.word = word
        self.code = code
        self.row = row
        self.col = col


tokendic = {}  # 存储从token文件读出的字符和对应代码符号，小型的符号表
tokens = []  # 传递给语法分析的数组，存储所有的token
wrong = []  # 存储出错情况
num_line = 1  # 行号


def read_file(filepath):  # 读入源文件
    print(filepath)
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    return content


# 识别标识符
def regid(content, index):
    state = 0
    word = ""
    while state != 2:
        if state == 0:
            if content[index].isalpha() or content[index] == '_':  # 是字母或者下划线
                word = word + content[index]
                state = 1
        elif state == 1:
            if content[index].isalpha() or content[index].isdigit() or content[index] == '_':  # 是字母，数字，下划线
                word = word + content[index]
            else:
                state = 2  # 退出状态
        if state == 2:
            index -= 1  # 回退索引
        index += 1
    if word in tokendic.keys():  # 字符串是关键字
        tokens.append(token(word, tokendic[word], num_line, 0))
    else:  # 字符串是标识符
        tokens.append(token(word, 800, num_line, 0))  # 不是关键字，那么就是用户自定义标识符
        pd = Symbol(word, 800, num_line, -1)
        token_table_instance.add_symbol(pd)  # 将标识符加入符号表之中
    return index


# 识别数字
# State 0: 初始状态，开始处理数字或实数。
# State 1: 处理整数部分。
# State 2: 遇到以0开头的情况，根据后续字符确定是八进制、十进制或者实数。
# State 3: 处理八进制整数部分。
# State 4: 结束状态，表示已经完成数字或实数的解析。
# State 5: 遇到'x'或'X'，表示十六进制整数部分。
# State 6: 处理十六进制整数部分的数字或字母。
# State 8: 遇到小数点，进入处理小数部分的状态。
# State 9: 处理小数部分的数字。
# State 10: 遇到'e'或'E'，表示科学计数法。
# State 11: 处理科学计数法中的正负号。
# State 12: 处理科学计数法中的指数部分的数字。
# State 14: 非法状态，表示实数结构错误。
def regnum(content, index):
    yunsuan = ['+', '-', '*', '/', '&', '|', '!', '>', '<', '=', '[', ']', '(', ')', '%', '\n', '\t', ';', ',']
    state = 0
    word = ""
    while state not in [4, 14]:
        if state == 0:
            if content[index] == '0':
                state = 2
            elif content[index].isdigit():
                state = 1
            word += content[index]
        elif state == 1:
            if content[index] == 'e' or content[index] == 'E':
                state = 10
                word += content[index]
            elif content[index] in yunsuan:
                state = 4
            elif content[index].isdigit():
                word += content[index]
            elif content[index] == '.':
                word += content[index]
                state = 8
            else:
                state = 14
                word += content[index]
        elif state == 2:
            if content[index] == '.':
                state = 8
                word += content[index]
            elif content[index] >= '0' and content[index] <= '7':
                word += content[index]
                state = 3
            elif content[index] == 'x' or content[index] == 'X':
                word += content[index]
                state = 5
            else:
                state = 4
        elif state == 3:
            if content[index] >= '0' and content[index] <= '7':
                word += content[index]
            else:
                state = 4
        elif state == 5:
            if content[index].isdigit() or content[index].isalpha():
                word += content[index]
                state = 6
        elif state == 6:
            if content[index].isdigit() or content[index].isalpha():
                word += content[index]
            else:
                state = 4
        elif state == 8:
            if content[index].isdigit():
                state = 9
            else:
                state = 14
            word += content[index]
        elif state == 9:
            if content[index] == 'e' or content[index] == 'E':
                word += content[index]
                state = 10
            elif content[index].isdigit():
                word += content[index]
            elif content[index] in yunsuan:
                state = 4
            else:
                word += content[index]
                state = 14
        elif state == 10:
            if content[index] == '+' or content[index] == '-':
                state = 11
            elif content[index].isdigit():
                state = 12
            else:
                state = 14
            word += content[index]
        elif state == 11:
            word += content[index]
            if content[index].isdigit():
                state = 12
            else:
                state = 14
        elif state == 12:
            if content[index].isdigit():
                word += content[index]
            elif content[index] in yunsuan:
                state = 4
            else:
                word += content[index]
                state = 14
        if state == 4:
            index -= 1
        index += 1
    if state == 4:
        tokens.append(token(word, 500, num_line, 0))
        pd = Symbol(word, 500, num_line, -1)
        token_table_instance.add_symbol(pd)  # 将数字加入符号表之中
    else:
        wrong.append("line:" + str(num_line) + " " + word + "   实数结构错误")
    return index


# 注释和除号
def regnode(content, index):
    global num_line
    state = 0
    word = ''
    while state not in [4, 5, 6]:
        if state == 0:
            if content[index] == '/':
                word += content[index]
                state = 1
        elif state == 1:
            if content[index] == '/':
                while content[index] != '\n':
                    index += 1
                num_line += 1
                state = 4
            elif content[index] == '*':
                state = 2
            elif content[index] == '=':
                word += content[index]
                state = 5
            else:
                state = 6
        elif state == 2:
            if content[index] == '*':
                state = 3
            if content[index] == '\n':
                num_line += 1
        elif state == 3:
            if content[index] == '/':
                state = 4
            else:
                state = 2
            if content[index] == '\n':
                num_line += 1
        if state == 6:
            index -= 1
        index += 1
    if state != 4:
        tokens.append(token(word, tokendic[word], num_line, 0))
    return index


# 字符常量
def regchar(content, index):
    zhuanyi = ['a', 'b', 'f', 'r', 'v', '\\', '\'', '\"', '?', 't']
    state = 0
    word = ''
    while state not in [4, 5]:
        if state == 0:
            if content[index] == '\'':
                word += content[index]
                state = 1
        elif state == 1:
            if content[index] == '\\':
                state = 2
            else:
                state = 3
            word += content[index]
        elif state == 2:
            word += content[index]
            if content[index] in zhuanyi:
                state = 3
            else:
                state = 5
        elif state == 3:
            word += content[index]
            if content[index] == '\'':
                state = 4
            else:
                state = 5
        if state == 5:
            index += 1
            while (content[index] != '\''):
                word += content[index]
                index += 1
            index += 1
            break
        index += 1
    if state != 5:
        tokens.append(token(word, 600, num_line, 0))
        pd = Symbol(word, 600, num_line, -1)
        token_table_instance.add_symbol(pd)  # 将字符常量加入符号表之中
    else:
        wrong.append("line:" + str(num_line) + " " + word + "\'" + "   字符常量不合法")
    return index


# 字符串常量
def regstr(content, index):
    state = 0
    word = ""
    while state != 3:
        if state == 0:
            if content[index] == "\"":
                word += content[index]
                state = 1
        elif state == 1:
            if content[index] == "\\":
                state = 2
            elif content[index] == "\"":
                state = 3
            word += content[index]
        elif state == 2:
            word += content[index]
            state = 1
        index += 1
    tokens.append(token(word, 700, num_line, 0))
    pd = Symbol(word, 700, num_line, -1)
    token_table_instance.add_symbol(pd)  # 将字符串常量加入符号表之中
    return index


# > >= >> >>= < <= << <<=
def regbs(content, index):
    state = 0
    word = ""
    while state not in [2, 4, 5, 6]:
        if state == 0:
            if content[index] == '>' or content[index] == '<':
                word += content[index]
                state = 1
        elif state == 1:
            if content[index] == '=':
                word += content[index]
                state = 2
            elif content[index] == word[0]:
                word += content[index]
                state = 3
            else:
                state = 6
        elif state == 3:
            if content[index] == '=':
                word += content[index]
                state = 4
            else:
                state = 5
        if state == 5 or state == 6:
            index -= 1
        index += 1
    tokens.append(token(word, tokendic[word], num_line, 0))
    return index


# * ! ^ % = *= != ^= %= ==
def regae(content, index):
    state = 0
    word = ""
    zifu = ['*', '!', '^', '%', '=']
    while state != 2 and state != 3:
        if state == 0:
            if content[index] in zifu:
                word += content[index]
                state = 1
        elif state == 1:
            if content[index] == '=':
                word += content[index]
                state = 2
            else:
                state = 3
        if state == 3:
            index -= 1
        index += 1
    tokens.append(token(word, tokendic[word], num_line, 0))
    return index


# + - & | += &= |= -= ++ -- && || ->
def regbe(content, index):
    state = 0
    word = ""
    while state not in [2, 3, 4]:
        if state == 0:
            if content[index] in ['+', '&', '|', '-']:
                word += content[index]
                state = 1
        elif state == 1:
            if content[index] == '=':
                word += content[index]
                state = 2
            elif content[index] == word[0] or (content[index] == '>' and word[0] == '-'):
                word += content[index]
                state = 3
            else:
                state = 4
        if state == 4:
            index -= 1
        index += 1
    tokens.append(token(word, tokendic[word], num_line, 0))
    return index


# default
def regce(content, index):
    if content[index] in tokendic.keys():
        tokens.append(token(content[index], tokendic[content[index]], num_line, 0))
    else:
        wrong.append("line:" + str(num_line) + " " + content[index] + "  未识别")
    index += 1
    return index


def gettoken(content):  # 获得token文件里定义的一些字符,并进行词法分析
    with open("./token.txt") as f:
        data = f.readlines()
    for i in data:
        temp = i.split('\t')
        tokendic[temp[0]] = temp[1][:-1]
    i = 0
    global num_line
    num_line = 1
    global wrong, tokens
    wrong = []
    tokens = []  # 初始化变量
    while (i < len(content)):  # 在源码内容上进行遍历
        while i < len(content) and (content[i] == ' ' or content[i] == '\n' or content[i] == '\t'):  # 跳过空格，换行，制表符号
            if content[i] == '\n':
                num_line += 1
            i += 1
        if i >= len(content):
            break
        if content[i].isalpha() or content[i] == '_':  # 标识符
            i = regid(content, i)
        elif content[i].isdigit():  # 数字
            i = regnum(content, i)
        elif content[i] == '/':  # 注释和除号
            i = regnode(content, i)
        elif content[i] == '\'':  # 字符常量
            i = regchar(content, i)
        elif content[i] == "\"":  # 字符串常量
            i = regstr(content, i)
        elif content[i] == '>' or content[i] == '<':  # 关系运算符
            i = regbs(content, i)
        elif content[i] in ['*', '!', '^', '%', '=']:  # 赋值运算符
            i = regae(content, i)
        elif content[i] in ['+', '&', '|', '-']:  # 特殊字符
            i = regbe(content, i)
        else:
            i = regce(content, i)
    for i in tokens:
        print(i.word + " " + str(i.code))

    with open('./tokenList.txt', 'w', encoding='utf-8') as f:  # 写入文件操作
        f.write('')
        f.close()
    with open('./tokenList.txt', 'a', encoding='utf-8') as f:  # 追加一行，表示词法分析结束
        for i in tokens:
            f.write(i.word + ' ' + str(i.code) + ' ' + str(i.row) + '\n')
        f.write('# 100 ' + str(tokens[-1].row))
        # 错误
    for i in wrong:  # 输出词法分析阶段的错误
        print(i)
    print(num_line)
    return tokens, wrong


def print_token_table(token_table):
    print("Token Table:")
    print("{:<15} {:<10} {:<10} {:<10} {:<10}".format("Word", "Code", "Line", "Domain", "Val"))
    print("-" * 55)

    for word, info in token_table.items():
        line_info = "{:<15} {:<10} {:<10} {:<10} {:<10}".format(
            word, info['code'], info['line'], info['domain'], info.get('val', ''))
        print(line_info)


def main():
    filepath = "./hello.c"  # 输入文件的路径
    content = read_file(filepath)
    gettoken(content)
    print_token_table(token_table_instance.token_table)


if __name__ == '__main__':
    main()
