class Symbol:  # 符号表中每一单元存储的内容
    def __init__(self, word, code, line, domain, val=None):
        self.word = word
        self.code = code
        self.line = line  # 当前标识符数字等第一次出现位置，默认值为-1
        self.domain = domain  # 保存作用域,初始值为-1
        self.val = val  # 标识符对应的类型


class TokenTable:
    def __init__(self):
        self.token_table = {}
        file_path = "./token.txt"  # 文件路径
        self.load_from_file(file_path)

    def add_symbol(self, symbol):
        if symbol.word not in self.token_table:
            self.token_table[symbol.word] = {
                'code': symbol.code,
                'line': symbol.line,  # 添加行号信息
                'domain': symbol.domain  # 添加作用域信息
            }

    def remove_symbol(self, word):
        if word in self.token_table:
            del self.token_table[word]

    def get_symbol_info(self, word):
        return self.token_table.get(word, None)

    def set_symbol_domain(self, word, domain):  # 更新作用域的值
        symbol_info = self.get_symbol_info(word)

        if symbol_info is not None:
            # 如果找到符号，更新 domain 值
            self.token_table[word]['domain'] = domain

    def set_symbol_val(self, word, val):  # 更新变量类型的值
        symbol_info = self.get_symbol_info(word)

        if symbol_info is not None:
            # 如果找到符号，更新 val 值
            self.token_table[word]['val'] = val

    def load_from_file(self, file_path):
        with open(file_path) as file:
            lines = file.readlines()

        for line in lines:
            word, code = line.strip().split('\t')
            code = int(code)
            symbol = Symbol(word, code, -1, -1)
            self.add_symbol(symbol)

# 创建符号表实例
token_table_instance = TokenTable()