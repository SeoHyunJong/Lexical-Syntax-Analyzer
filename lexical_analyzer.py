import sys #input 파일 받아올때 필요.

##DFA class 정의
class DFA:
    cur = 0 #초기 start state
    accept = True # accept : final에 도달했는가
    pop_string = '' #유효한 심볼을 담는 일종의 '큐'
    garbage = '' #symbol 이 아닌 값을 쓰레기통에 하나 저장
    
    def dfa_clear(self):
        self.cur = 0
        self.accept = True
        self.pop_string = ''
    
    def garbage_clear(self):
        self.garbage = ''
        
    def set_name(self, name):
        self.name = name
        
    def set_symbol(self, symbol): #input string in DFA.symbol 을 이용하여 DFA 추리기
        self.symbol = symbol
            
    def read_transition(self, transition):
        self.transition = transition
            
    def set_final(self, final): #final은 정수형으로 받자
        self.final = final
    
    def go_next_state(self, symbol):
        next_idx = self.transition[self.cur][symbol]
        if next_idx == 'E': # 'E' 는 공집합
            self.accept = False
        else:
            self.cur = int(next_idx)
            
    def is_accept(self):
        if self.accept:
            if self.cur in self.final:
                self.accept = True
            else:
                self.accept = False
                
                
class DFA_type(DFA):
    def analyzer(self, character, out):
        if character in self.symbol:
            self.go_next_state(character)
            if self.accept == False:
                self.dfa_clear()
            else:
                self.pop_string = self.pop_string + character
        elif character in common_sym:
            self.is_accept()
            if self.accept:
                if self.name == 'BOOLEAN':
                    out.append([self.name,self.pop_string])
                else:
                    out.append([self.name,])
            self.dfa_clear()
        else:
            self.dfa_clear()
            
class DFA_integer(DFA): # integer를 위한 클래스. - 때문에 그렇다.
    def analyzer(self, character, out):
        if character in self.symbol:
            self.go_next_state(character)
            if self.accept == False:
                if self.pop_string != '-' and self.garbage == '': # -- 오류 방지
                    out.append([self.name,self.pop_string])
                self.dfa_clear()
                self.analyzer(character, out)
            elif character == '-':
                if self.garbage == '':
                    self.pop_string = self.pop_string + character
                else:
                    self.garbage_clear()
                    self.dfa_clear()
            else:
                self.pop_string = self.pop_string + character
        elif character in common_sym:
            self.is_accept()
            if self.accept and self.garbage == '':
                out.append([self.name,self.pop_string])
            self.garbage_clear()
            self.dfa_clear()
        else:
            self.is_accept()
            if self.accept and self.garbage == '':
                out.append([self.name,self.pop_string])
            self.garbage = character # integer와 id가 겹치는 문제를 해결하기 위해서다. abc120 같은 것들. c를 쓰레기로 저장...
            self.dfa_clear()

class DFA_op(DFA): # common_sym: +, -, *, /... 를 위한 클래스.
    def analyzer(self, character, out):
        if character in self.symbol:
            self.go_next_state(character)
            if self.accept == False:
                if self.name == 'COMPARISON':
                    out.append([self.name,self.pop_string])
                else:
                    out.append([self.name,])
                self.dfa_clear()
                self.analyzer(character, out)
            else:
                self.pop_string = self.pop_string + character
        else:
            self.is_accept()
            if self.accept:
                if self.name == 'COMPARISON':
                    out.append([self.name,self.pop_string])
                else:
                    out.append([self.name,])
            self.dfa_clear()

class DFA_ch(DFA):
    def analyzer(self, character,out):
        if character in self.symbol:
            self.go_next_state(character)
            if self.accept == False:
                if len(self.pop_string) > 1: # 'a'b 'a'1 등의 character인식 불가 오류 해결.
                    if self.pop_string[-1] == '\'':
                        out.append([self.name,self.pop_string])
                self.dfa_clear()
            else:
                self.pop_string = self.pop_string + character
        else:
            self.is_accept()
            if self.accept:
                out.append([self.name,self.pop_string])
            self.dfa_clear()
            
class DFA_string(DFA):
    def analyzer(self, character, out):
        if character in self.symbol:
            self.go_next_state(character)
            if self.accept == False:
                if len(self.pop_string) > 1:
                    if self.pop_string[-1] == '\"':
                        out.append([self.name,self.pop_string])
                self.dfa_clear()
            else:
                self.pop_string = self.pop_string + character
        else:
            self.is_accept()
            if self.accept:
                out.append([self.name,self.pop_string])
            self.dfa_clear()
            
class DFA_id(DFA):
    def analyzer(self, character,out):
        if character in self.symbol:
            self.go_next_state(character)
            if self.accept == False:
                self.dfa_clear()
            else:
                self.pop_string = self.pop_string + character
        elif character in common_sym:
            self.is_accept()
            if self.accept and self.garbage == '' and self.pop_string not in Keyword:
                out.append([self.name,self.pop_string])
            self.garbage_clear()
            self.dfa_clear()
        else:
            self.garbage = character
            self.dfa_clear()
            
class DFA_assign(DFA): # assign 의 경우 비교연산자 <=. >=, != 충돌이 있어 다른 클래스가 필요.
    def analyzer(self, character, out):
        if character in self.symbol:
            self.go_next_state(character)
            if self.accept == False:
                self.dfa_clear()
            else:
                self.pop_string = self.pop_string + character
        elif character in ['<', '>', '!']:
            self.garbage = character
            self.dfa_clear()
        else:
            self.is_accept()
            if self.accept and self.garbage == '':
                out.append([self.name,])
            self.garbage_clear()
            self.dfa_clear()
            
class DFA_brace(DFA): # (,),[,],{,}를 위한 클래스.
    def analyzer(self, character, out):
        if character in self.symbol:
            out.append([self.name,])

##DFA table 입력

common_sym = ['+', '-', '*', '/', '=', ' ', '<', '>', '!', ';', '(', ')', '[', ']', '{', '}', ',', '\n', '\t']
Keyword = ['int', 'char', 'bool', 'String', 'true', 'false', 'if', 'else', 'while', 'class', 'return']
###############################################
_INTEGER = DFA_integer()
_INTEGER.set_name('INTEGER')
_INTEGER.set_symbol(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-'])
_INTEGER.set_final([1, 3, 4])
transition_integer = [ {'0':'1', '1':'3', '2':'3', '3':'3', '4':'3', '5':'3', '6':'3', '7':'3', '8':'3', '9':'3', '-':'2'},
                       {'0':'E', '1':'E', '2':'E', '3':'E', '4':'E', '5':'E', '6':'E', '7':'E', '8':'E', '9':'E', '-':'E'},
                       {'0':'E', '1':'3', '2':'3', '3':'3', '4':'3', '5':'3', '6':'3', '7':'3', '8':'3', '9':'3', '-':'E'},
                       {'0':'4', '1':'4', '2':'4', '3':'4', '4':'4', '5':'4', '6':'4', '7':'4', '8':'4', '9':'4', '-':'E'},
                       {'0':'4', '1':'4', '2':'4', '3':'4', '4':'4', '5':'4', '6':'4', '7':'4', '8':'4', '9':'4', '-':'E'}
                     ]
_INTEGER.read_transition(transition_integer)
################################################
_INT = DFA_type()
_INT.set_name('INT')
_INT.set_symbol(['i', 'n', 't'])
_INT.set_final([3,])
transition_int     = [ {'i':'1', 'n':'E', 't':'E'},
                       {'i':'E', 'n':'2', 't':'E'},
                       {'i':'E', 'n':'E', 't':'3'},
                       {'i':'E', 'n':'E', 't':'E'}
                     ]
_INT.read_transition(transition_int)
################################################
_CHAR = DFA_type()
_CHAR.set_name('CHAR')
_CHAR.set_symbol(['c', 'h', 'a', 'r'])
_CHAR.set_final([4,])
transition_char    = [ {'c':'1', 'h':'E', 'a':'E', 'r':'E'},
                       {'c':'E', 'h':'2', 'a':'E', 'r':'E'},
                       {'c':'E', 'h':'E', 'a':'3', 'r':'E'},
                       {'c':'E', 'h':'E', 'a':'E', 'r':'4'},
                       {'c':'E', 'h':'E', 'a':'E', 'r':'E'},
                     ]
_CHAR.read_transition(transition_char)
################################################
_BOOL = DFA_type()
_BOOL.set_name('BOOL')
_BOOL.set_symbol(['b', 'o', 'l'])
_BOOL.set_final([4,])
transition_bool    = [ {'b':'1', 'o':'E', 'l':'E'},
                       {'b':'E', 'o':'2', 'l':'E'},
                       {'b':'E', 'o':'3', 'l':'E'},
                       {'b':'E', 'o':'E', 'l':'4'},
                       {'b':'E', 'o':'E', 'l':'E'}
                     ]
_BOOL.read_transition(transition_bool)
################################################
_STRING = DFA_type()
_STRING.set_name('STRING')
_STRING.set_symbol(['S', 't', 'r', 'i', 'n', 'g'])
_STRING.set_final([6,])
transition_string  = [ {'S':'1', 't':'E', 'r':'E', 'i':'E', 'n':'E', 'g':'E'},
                       {'S':'E', 't':'2', 'r':'E', 'i':'E', 'n':'E', 'g':'E'},
                       {'S':'E', 't':'E', 'r':'3', 'i':'E', 'n':'E', 'g':'E'},
                       {'S':'E', 't':'E', 'r':'E', 'i':'4', 'n':'E', 'g':'E'},
                       {'S':'E', 't':'E', 'r':'E', 'i':'E', 'n':'5', 'g':'E'},
                       {'S':'E', 't':'E', 'r':'E', 'i':'E', 'n':'E', 'g':'6'},
                       {'S':'E', 't':'E', 'r':'E', 'i':'E', 'n':'E', 'g':'E'}
                     ]
_STRING.read_transition(transition_string)
################################################
_CHARACTER = DFA_ch()
_CHARACTER.set_name('CHARACTER')
_CHARACTER.set_symbol(['\'', ' ', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                      'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                      'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                      'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                      'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])
_CHARACTER.set_final([5,])
transition_character  = [{'\'':'1', ' ':'E', '0':'E', '1':'E', '2':'E', '3':'E', '4':'E', '5':'E', '6':'E', '7':'E', '8':'E', '9':'E',
                      'a':'E', 'b':'E', 'c':'E', 'd':'E', 'e':'E', 'f':'E', 'g':'E', 'h':'E', 'i':'E', 'j':'E', 'k':'E', 'l':'E',
                      'm':'E', 'n':'E', 'o':'E', 'p':'E', 'q':'E', 'r':'E', 's':'E', 't':'E', 'u':'E', 'v':'E', 'w':'E', 'x':'E',
                      'y':'E', 'z':'E', 'A':'E', 'B':'E', 'C':'E', 'D':'E', 'E':'E', 'F':'E', 'G':'E', 'H':'E', 'I':'E', 'J':'E',
                      'K':'E', 'L':'E', 'M':'E', 'N':'E', 'O':'E', 'P':'E', 'Q':'E', 'R':'E', 'S':'E', 'T':'E', 'U':'E', 'V':'E',
                      'W':'E', 'X':'E', 'Y':'E', 'Z':'E'},
                         {'\'':'E', ' ':'4', '0':'2', '1':'2', '2':'2', '3':'2', '4':'2', '5':'2', '6':'2', '7':'2', '8':'2', '9':'2',
                      'a':'3', 'b':'3', 'c':'3', 'd':'3', 'e':'3', 'f':'3', 'g':'3', 'h':'3', 'i':'3', 'j':'3', 'k':'3', 'l':'3',
                      'm':'3', 'n':'3', 'o':'3', 'p':'3', 'q':'3', 'r':'3', 's':'3', 't':'3', 'u':'3', 'v':'3', 'w':'3', 'x':'3',
                      'y':'3', 'z':'3', 'A':'3', 'B':'3', 'C':'3', 'D':'3', 'E':'3', 'F':'3', 'G':'3', 'H':'3', 'I':'3', 'J':'3',
                      'K':'3', 'L':'3', 'M':'3', 'N':'3', 'O':'3', 'P':'3', 'Q':'3', 'R':'3', 'S':'3', 'T':'3', 'U':'3', 'V':'3',
                      'W':'3', 'X':'3', 'Y':'3', 'Z':'3'},
                         {'\'':'5', ' ':'E', '0':'E', '1':'E', '2':'E', '3':'E', '4':'E', '5':'E', '6':'E', '7':'E', '8':'E', '9':'E',
                      'a':'E', 'b':'E', 'c':'E', 'd':'E', 'e':'E', 'f':'E', 'g':'E', 'h':'E', 'i':'E', 'j':'E', 'k':'E', 'l':'E',
                      'm':'E', 'n':'E', 'o':'E', 'p':'E', 'q':'E', 'r':'E', 's':'E', 't':'E', 'u':'E', 'v':'E', 'w':'E', 'x':'E',
                      'y':'E', 'z':'E', 'A':'E', 'B':'E', 'C':'E', 'D':'E', 'E':'E', 'F':'E', 'G':'E', 'H':'E', 'I':'E', 'J':'E',
                      'K':'E', 'L':'E', 'M':'E', 'N':'E', 'O':'E', 'P':'E', 'Q':'E', 'R':'E', 'S':'E', 'T':'E', 'U':'E', 'V':'E',
                      'W':'E', 'X':'E', 'Y':'E', 'Z':'E'},
                         {'\'':'5', ' ':'E', '0':'E', '1':'E', '2':'E', '3':'E', '4':'E', '5':'E', '6':'E', '7':'E', '8':'E', '9':'E',
                      'a':'E', 'b':'E', 'c':'E', 'd':'E', 'e':'E', 'f':'E', 'g':'E', 'h':'E', 'i':'E', 'j':'E', 'k':'E', 'l':'E',
                      'm':'E', 'n':'E', 'o':'E', 'p':'E', 'q':'E', 'r':'E', 's':'E', 't':'E', 'u':'E', 'v':'E', 'w':'E', 'x':'E',
                      'y':'E', 'z':'E', 'A':'E', 'B':'E', 'C':'E', 'D':'E', 'E':'E', 'F':'E', 'G':'E', 'H':'E', 'I':'E', 'J':'E',
                      'K':'E', 'L':'E', 'M':'E', 'N':'E', 'O':'E', 'P':'E', 'Q':'E', 'R':'E', 'S':'E', 'T':'E', 'U':'E', 'V':'E',
                      'W':'E', 'X':'E', 'Y':'E', 'Z':'E'},
                         {'\'':'5', ' ':'E', '0':'E', '1':'E', '2':'E', '3':'E', '4':'E', '5':'E', '6':'E', '7':'E', '8':'E', '9':'E',
                      'a':'E', 'b':'E', 'c':'E', 'd':'E', 'e':'E', 'f':'E', 'g':'E', 'h':'E', 'i':'E', 'j':'E', 'k':'E', 'l':'E',
                      'm':'E', 'n':'E', 'o':'E', 'p':'E', 'q':'E', 'r':'E', 's':'E', 't':'E', 'u':'E', 'v':'E', 'w':'E', 'x':'E',
                      'y':'E', 'z':'E', 'A':'E', 'B':'E', 'C':'E', 'D':'E', 'E':'E', 'F':'E', 'G':'E', 'H':'E', 'I':'E', 'J':'E',
                      'K':'E', 'L':'E', 'M':'E', 'N':'E', 'O':'E', 'P':'E', 'Q':'E', 'R':'E', 'S':'E', 'T':'E', 'U':'E', 'V':'E',
                      'W':'E', 'X':'E', 'Y':'E', 'Z':'E'},
                         {'\'':'E', ' ':'E', '0':'E', '1':'E', '2':'E', '3':'E', '4':'E', '5':'E', '6':'E', '7':'E', '8':'E', '9':'E',
                      'a':'E', 'b':'E', 'c':'E', 'd':'E', 'e':'E', 'f':'E', 'g':'E', 'h':'E', 'i':'E', 'j':'E', 'k':'E', 'l':'E',
                      'm':'E', 'n':'E', 'o':'E', 'p':'E', 'q':'E', 'r':'E', 's':'E', 't':'E', 'u':'E', 'v':'E', 'w':'E', 'x':'E',
                      'y':'E', 'z':'E', 'A':'E', 'B':'E', 'C':'E', 'D':'E', 'E':'E', 'F':'E', 'G':'E', 'H':'E', 'I':'E', 'J':'E',
                      'K':'E', 'L':'E', 'M':'E', 'N':'E', 'O':'E', 'P':'E', 'Q':'E', 'R':'E', 'S':'E', 'T':'E', 'U':'E', 'V':'E',
                      'W':'E', 'X':'E', 'Y':'E', 'Z':'E'}
                        ]
_CHARACTER.read_transition(transition_character)
################################################
_BOOLEAN = DFA_type()
_BOOLEAN.set_name('BOOLEAN')
_BOOLEAN.set_symbol(['t', 'r', 'u', 'e', 'f', 'a', 'l', 's'])
_BOOLEAN.set_final([7,9])
transition_boolean  = [{'t':'1', 'r':'E', 'u':'E', 'e':'E', 'f':'2', 'a':'E', 'l':'E', 's':'E'},
                       {'t':'E', 'r':'3', 'u':'E', 'e':'E', 'f':'E', 'a':'E', 'l':'E', 's':'E'},
                       {'t':'E', 'r':'E', 'u':'E', 'e':'E', 'f':'E', 'a':'4', 'l':'E', 's':'E'},
                       {'t':'E', 'r':'E', 'u':'5', 'e':'E', 'f':'E', 'a':'E', 'l':'E', 's':'E'},
                       {'t':'E', 'r':'E', 'u':'E', 'e':'E', 'f':'E', 'a':'E', 'l':'6', 's':'E'},
                       {'t':'E', 'r':'E', 'u':'E', 'e':'7', 'f':'E', 'a':'E', 'l':'E', 's':'E'},
                       {'t':'E', 'r':'E', 'u':'E', 'e':'E', 'f':'E', 'a':'E', 'l':'E', 's':'8'},
                       {'t':'E', 'r':'E', 'u':'E', 'e':'E', 'f':'E', 'a':'E', 'l':'E', 's':'E'},
                       {'t':'E', 'r':'E', 'u':'E', 'e':'9', 'f':'E', 'a':'E', 'l':'E', 's':'E'},
                       {'t':'E', 'r':'E', 'u':'E', 'e':'E', 'f':'E', 'a':'E', 'l':'E', 's':'E'}
                     ]
_BOOLEAN.read_transition(transition_boolean)
################################################
_LITERAL = DFA_string()
_LITERAL.set_name('LITERAL')
_LITERAL.set_symbol(['\"', ' ', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                      'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                      'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                      'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                      'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])
_LITERAL.set_final([2,])
transition_literal    = [{'\"':'1', ' ':'E', '0':'E', '1':'E', '2':'E', '3':'E', '4':'E', '5':'E', '6':'E', '7':'E', '8':'E', '9':'E',
                      'a':'E', 'b':'E', 'c':'E', 'd':'E', 'e':'E', 'f':'E', 'g':'E', 'h':'E', 'i':'E', 'j':'E', 'k':'E', 'l':'E',
                      'm':'E', 'n':'E', 'o':'E', 'p':'E', 'q':'E', 'r':'E', 's':'E', 't':'E', 'u':'E', 'v':'E', 'w':'E', 'x':'E',
                      'y':'E', 'z':'E', 'A':'E', 'B':'E', 'C':'E', 'D':'E', 'E':'E', 'F':'E', 'G':'E', 'H':'E', 'I':'E', 'J':'E',
                      'K':'E', 'L':'E', 'M':'E', 'N':'E', 'O':'E', 'P':'E', 'Q':'E', 'R':'E', 'S':'E', 'T':'E', 'U':'E', 'V':'E',
                      'W':'E', 'X':'E', 'Y':'E', 'Z':'E'},
                         {'\"':'2', ' ':'5', '0':'3', '1':'3', '2':'3', '3':'3', '4':'3', '5':'3', '6':'3', '7':'3', '8':'3', '9':'3',
                      'a':'4', 'b':'4', 'c':'4', 'd':'4', 'e':'4', 'f':'4', 'g':'4', 'h':'4', 'i':'4', 'j':'4', 'k':'4', 'l':'4',
                      'm':'4', 'n':'4', 'o':'4', 'p':'4', 'q':'4', 'r':'4', 's':'4', 't':'4', 'u':'4', 'v':'4', 'w':'4', 'x':'4',
                      'y':'4', 'z':'4', 'A':'4', 'B':'4', 'C':'4', 'D':'4', 'E':'4', 'F':'4', 'G':'4', 'H':'4', 'I':'4', 'J':'4',
                      'K':'4', 'L':'4', 'M':'4', 'N':'4', 'O':'4', 'P':'4', 'Q':'4', 'R':'4', 'S':'4', 'T':'4', 'U':'4', 'V':'4',
                      'W':'4', 'X':'4', 'Y':'4', 'Z':'4'},
                         {'\"':'E', ' ':'E', '0':'E', '1':'E', '2':'E', '3':'E', '4':'E', '5':'E', '6':'E', '7':'E', '8':'E', '9':'E',
                      'a':'E', 'b':'E', 'c':'E', 'd':'E', 'e':'E', 'f':'E', 'g':'E', 'h':'E', 'i':'E', 'j':'E', 'k':'E', 'l':'E',
                      'm':'E', 'n':'E', 'o':'E', 'p':'E', 'q':'E', 'r':'E', 's':'E', 't':'E', 'u':'E', 'v':'E', 'w':'E', 'x':'E',
                      'y':'E', 'z':'E', 'A':'E', 'B':'E', 'C':'E', 'D':'E', 'E':'E', 'F':'E', 'G':'E', 'H':'E', 'I':'E', 'J':'E',
                      'K':'E', 'L':'E', 'M':'E', 'N':'E', 'O':'E', 'P':'E', 'Q':'E', 'R':'E', 'S':'E', 'T':'E', 'U':'E', 'V':'E',
                      'W':'E', 'X':'E', 'Y':'E', 'Z':'E'},
                        {'\"':'2', ' ':'5', '0':'3', '1':'3', '2':'3', '3':'3', '4':'3', '5':'3', '6':'3', '7':'3', '8':'3', '9':'3',
                      'a':'4', 'b':'4', 'c':'4', 'd':'4', 'e':'4', 'f':'4', 'g':'4', 'h':'4', 'i':'4', 'j':'4', 'k':'4', 'l':'4',
                      'm':'4', 'n':'4', 'o':'4', 'p':'4', 'q':'4', 'r':'4', 's':'4', 't':'4', 'u':'4', 'v':'4', 'w':'4', 'x':'4',
                      'y':'4', 'z':'4', 'A':'4', 'B':'4', 'C':'4', 'D':'4', 'E':'4', 'F':'4', 'G':'4', 'H':'4', 'I':'4', 'J':'4',
                      'K':'4', 'L':'4', 'M':'4', 'N':'4', 'O':'4', 'P':'4', 'Q':'4', 'R':'4', 'S':'4', 'T':'4', 'U':'4', 'V':'4',
                      'W':'4', 'X':'4', 'Y':'4', 'Z':'4'},
                        {'\"':'2', ' ':'5', '0':'3', '1':'3', '2':'3', '3':'3', '4':'3', '5':'3', '6':'3', '7':'3', '8':'3', '9':'3',
                      'a':'4', 'b':'4', 'c':'4', 'd':'4', 'e':'4', 'f':'4', 'g':'4', 'h':'4', 'i':'4', 'j':'4', 'k':'4', 'l':'4',
                      'm':'4', 'n':'4', 'o':'4', 'p':'4', 'q':'4', 'r':'4', 's':'4', 't':'4', 'u':'4', 'v':'4', 'w':'4', 'x':'4',
                      'y':'4', 'z':'4', 'A':'4', 'B':'4', 'C':'4', 'D':'4', 'E':'4', 'F':'4', 'G':'4', 'H':'4', 'I':'4', 'J':'4',
                      'K':'4', 'L':'4', 'M':'4', 'N':'4', 'O':'4', 'P':'4', 'Q':'4', 'R':'4', 'S':'4', 'T':'4', 'U':'4', 'V':'4',
                      'W':'4', 'X':'4', 'Y':'4', 'Z':'4'},
                        {'\"':'2', ' ':'5', '0':'3', '1':'3', '2':'3', '3':'3', '4':'3', '5':'3', '6':'3', '7':'3', '8':'3', '9':'3',
                      'a':'4', 'b':'4', 'c':'4', 'd':'4', 'e':'4', 'f':'4', 'g':'4', 'h':'4', 'i':'4', 'j':'4', 'k':'4', 'l':'4',
                      'm':'4', 'n':'4', 'o':'4', 'p':'4', 'q':'4', 'r':'4', 's':'4', 't':'4', 'u':'4', 'v':'4', 'w':'4', 'x':'4',
                      'y':'4', 'z':'4', 'A':'4', 'B':'4', 'C':'4', 'D':'4', 'E':'4', 'F':'4', 'G':'4', 'H':'4', 'I':'4', 'J':'4',
                      'K':'4', 'L':'4', 'M':'4', 'N':'4', 'O':'4', 'P':'4', 'Q':'4', 'R':'4', 'S':'4', 'T':'4', 'U':'4', 'V':'4',
                      'W':'4', 'X':'4', 'Y':'4', 'Z':'4'}
                        ]
_LITERAL.read_transition(transition_literal)
################################################
_ID = DFA_id()
_ID.set_name('ID')
_ID.set_symbol(['_', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])
_ID.set_final([1,2,3,4,5])
transition_id    = [ {'_':'2', '0':'E', '1':'E', '2':'E', '3':'E', '4':'E', '5':'E', '6':'E', '7':'E', '8':'E', '9':'E',
                      'a':'1', 'b':'1', 'c':'1', 'd':'1', 'e':'1', 'f':'1', 'g':'1', 'h':'1', 'i':'1', 'j':'1', 'k':'1', 'l':'1',
                      'm':'1', 'n':'1', 'o':'1', 'p':'1', 'q':'1', 'r':'1', 's':'1', 't':'1', 'u':'1', 'v':'1', 'w':'1', 'x':'1',
                      'y':'1', 'z':'1', 'A':'1', 'B':'1', 'C':'1', 'D':'1', 'E':'1', 'F':'1', 'G':'1', 'H':'1', 'I':'1', 'J':'1',
                      'K':'1', 'L':'1', 'M':'1', 'N':'1', 'O':'1', 'P':'1', 'Q':'1', 'R':'1', 'S':'1', 'T':'1', 'U':'1', 'V':'1',
                      'W':'1', 'X':'1', 'Y':'1', 'Z':'1'},
                     {'_':'4', '0':'5', '1':'5', '2':'5', '3':'5', '4':'5', '5':'5', '6':'5', '7':'5', '8':'5', '9':'5',
                      'a':'3', 'b':'3', 'c':'3', 'd':'3', 'e':'3', 'f':'3', 'g':'3', 'h':'3', 'i':'3', 'j':'3', 'k':'3', 'l':'3',
                      'm':'3', 'n':'3', 'o':'3', 'p':'3', 'q':'3', 'r':'3', 's':'3', 't':'3', 'u':'3', 'v':'3', 'w':'3', 'x':'3',
                      'y':'3', 'z':'3', 'A':'3', 'B':'3', 'C':'3', 'D':'3', 'E':'3', 'F':'3', 'G':'3', 'H':'3', 'I':'3', 'J':'3',
                      'K':'3', 'L':'3', 'M':'3', 'N':'3', 'O':'3', 'P':'3', 'Q':'3', 'R':'3', 'S':'3', 'T':'3', 'U':'3', 'V':'3',
                      'W':'3', 'X':'3', 'Y':'3', 'Z':'3'},
                     {'_':'4', '0':'5', '1':'5', '2':'5', '3':'5', '4':'5', '5':'5', '6':'5', '7':'5', '8':'5', '9':'5',
                      'a':'3', 'b':'3', 'c':'3', 'd':'3', 'e':'3', 'f':'3', 'g':'3', 'h':'3', 'i':'3', 'j':'3', 'k':'3', 'l':'3',
                      'm':'3', 'n':'3', 'o':'3', 'p':'3', 'q':'3', 'r':'3', 's':'3', 't':'3', 'u':'3', 'v':'3', 'w':'3', 'x':'3',
                      'y':'3', 'z':'3', 'A':'3', 'B':'3', 'C':'3', 'D':'3', 'E':'3', 'F':'3', 'G':'3', 'H':'3', 'I':'3', 'J':'3',
                      'K':'3', 'L':'3', 'M':'3', 'N':'3', 'O':'3', 'P':'3', 'Q':'3', 'R':'3', 'S':'3', 'T':'3', 'U':'3', 'V':'3',
                      'W':'3', 'X':'3', 'Y':'3', 'Z':'3'},
                     {'_':'4', '0':'5', '1':'5', '2':'5', '3':'5', '4':'5', '5':'5', '6':'5', '7':'5', '8':'5', '9':'5',
                      'a':'3', 'b':'3', 'c':'3', 'd':'3', 'e':'3', 'f':'3', 'g':'3', 'h':'3', 'i':'3', 'j':'3', 'k':'3', 'l':'3',
                      'm':'3', 'n':'3', 'o':'3', 'p':'3', 'q':'3', 'r':'3', 's':'3', 't':'3', 'u':'3', 'v':'3', 'w':'3', 'x':'3',
                      'y':'3', 'z':'3', 'A':'3', 'B':'3', 'C':'3', 'D':'3', 'E':'3', 'F':'3', 'G':'3', 'H':'3', 'I':'3', 'J':'3',
                      'K':'3', 'L':'3', 'M':'3', 'N':'3', 'O':'3', 'P':'3', 'Q':'3', 'R':'3', 'S':'3', 'T':'3', 'U':'3', 'V':'3',
                      'W':'3', 'X':'3', 'Y':'3', 'Z':'3'},
                     {'_':'4', '0':'5', '1':'5', '2':'5', '3':'5', '4':'5', '5':'5', '6':'5', '7':'5', '8':'5', '9':'5',
                      'a':'3', 'b':'3', 'c':'3', 'd':'3', 'e':'3', 'f':'3', 'g':'3', 'h':'3', 'i':'3', 'j':'3', 'k':'3', 'l':'3',
                      'm':'3', 'n':'3', 'o':'3', 'p':'3', 'q':'3', 'r':'3', 's':'3', 't':'3', 'u':'3', 'v':'3', 'w':'3', 'x':'3',
                      'y':'3', 'z':'3', 'A':'3', 'B':'3', 'C':'3', 'D':'3', 'E':'3', 'F':'3', 'G':'3', 'H':'3', 'I':'3', 'J':'3',
                      'K':'3', 'L':'3', 'M':'3', 'N':'3', 'O':'3', 'P':'3', 'Q':'3', 'R':'3', 'S':'3', 'T':'3', 'U':'3', 'V':'3',
                      'W':'3', 'X':'3', 'Y':'3', 'Z':'3'},
                     {'_':'4', '0':'5', '1':'5', '2':'5', '3':'5', '4':'5', '5':'5', '6':'5', '7':'5', '8':'5', '9':'5',
                      'a':'3', 'b':'3', 'c':'3', 'd':'3', 'e':'3', 'f':'3', 'g':'3', 'h':'3', 'i':'3', 'j':'3', 'k':'3', 'l':'3',
                      'm':'3', 'n':'3', 'o':'3', 'p':'3', 'q':'3', 'r':'3', 's':'3', 't':'3', 'u':'3', 'v':'3', 'w':'3', 'x':'3',
                      'y':'3', 'z':'3', 'A':'3', 'B':'3', 'C':'3', 'D':'3', 'E':'3', 'F':'3', 'G':'3', 'H':'3', 'I':'3', 'J':'3',
                      'K':'3', 'L':'3', 'M':'3', 'N':'3', 'O':'3', 'P':'3', 'Q':'3', 'R':'3', 'S':'3', 'T':'3', 'U':'3', 'V':'3',
                      'W':'3', 'X':'3', 'Y':'3', 'Z':'3'}
                        ]
_ID.read_transition(transition_id)
################################################
_IF = DFA_type()
_IF.set_name('IF')
_IF.set_symbol(['i', 'f'])
_IF.set_final([2,])
transition_if       = [{'i':'1', 'f':'E'},
                       {'i':'E', 'f':'2'},
                       {'i':'E', 'f':'E'}
                     ]
_IF.read_transition(transition_if)
################################################
_ELSE = DFA_type()
_ELSE.set_name('ELSE')
_ELSE.set_symbol(['e', 'l', 's'])
_ELSE.set_final([4,])
transition_else     = [{'e':'1', 'l':'E', 's':'E'},
                       {'e':'E', 'l':'2', 's':'E'},
                       {'e':'E', 'l':'E', 's':'3'},
                       {'e':'4', 'l':'E', 's':'E'},
                       {'e':'E', 'l':'E', 's':'E'}
                     ]
_ELSE.read_transition(transition_else)
################################################
_WHILE = DFA_type()
_WHILE.set_name('WHILE')
_WHILE.set_symbol(['w', 'h', 'i', 'l', 'e'])
_WHILE.set_final([5,])
transition_while    = [{'w':'1', 'h':'E', 'i':'E', 'l':'E', 'e':'E'},
                       {'w':'E', 'h':'2', 'i':'E', 'l':'E', 'e':'E'},
                       {'w':'E', 'h':'E', 'i':'3', 'l':'E', 'e':'E'},
                       {'w':'E', 'h':'E', 'i':'E', 'l':'4', 'e':'E'},
                       {'w':'E', 'h':'E', 'i':'E', 'l':'E', 'e':'5'},
                       {'w':'E', 'h':'E', 'i':'E', 'l':'E', 'e':'E'}
                     ]
_WHILE.read_transition(transition_while)
################################################
_CLASS = DFA_type()
_CLASS.set_name('CLASS')
_CLASS.set_symbol(['c', 'l', 'a', 's'])
_CLASS.set_final([5,])
transition_class    = [{'c':'1', 'l':'E', 'a':'E', 's':'E'},
                       {'c':'E', 'l':'2', 'a':'E', 's':'E'},
                       {'c':'E', 'l':'E', 'a':'3', 's':'E'},
                       {'c':'E', 'l':'E', 'a':'E', 's':'4'},
                       {'c':'E', 'l':'E', 'a':'E', 's':'5'},
                       {'c':'E', 'l':'E', 'a':'E', 's':'E'}
                     ]
_CLASS.read_transition(transition_class)
################################################
_RETURN = DFA_type()
_RETURN.set_name('RETURN')
_RETURN.set_symbol(['r', 'e', 't', 'u', 'n'])
_RETURN.set_final([6,])
transition_return   = [{'r':'1', 'e':'E', 't':'E', 'u':'E', 'n':'E'},
                       {'r':'E', 'e':'2', 't':'E', 'u':'E', 'n':'E'},
                       {'r':'E', 'e':'E', 't':'3', 'u':'E', 'n':'E'},
                       {'r':'E', 'e':'E', 't':'E', 'u':'4', 'n':'E'},
                       {'r':'5', 'e':'E', 't':'E', 'u':'E', 'n':'E'},
                       {'r':'E', 'e':'E', 't':'E', 'u':'E', 'n':'6'},
                       {'r':'E', 'e':'E', 't':'E', 'u':'E', 'n':'E'}
                     ]
_RETURN.read_transition(transition_return)
################################################
_ADD = DFA_op()
_ADD.set_name('ADD')
_ADD.set_symbol(['+',])
_ADD.set_final([1,])
transition_add      = [{'+':'1'},
                       {'+':'E'}
                     ]
_ADD.read_transition(transition_add)
################################################
_SUB = DFA_op()
_SUB.set_name('SUB')
_SUB.set_symbol(['-',])
_SUB.set_final([1,])
transition_sub      = [{'-':'1'},
                       {'-':'E'}
                     ]
_SUB.read_transition(transition_sub)
################################################
_MUL = DFA_op()
_MUL.set_name('MUL')
_MUL.set_symbol(['*',])
_MUL.set_final([1,])
transition_mul      = [{'*':'1'},
                       {'*':'E'}
                     ]
_MUL.read_transition(transition_mul)
################################################
_DIV = DFA_op()
_DIV.set_name('DIV')
_DIV.set_symbol(['/',])
_DIV.set_final([1,])
transition_div      = [{'/':'1'},
                       {'/':'E'}
                     ]
_DIV.read_transition(transition_div)
################################################
_ASSIGN = DFA_assign()
_ASSIGN.set_name('ASSIGN')
_ASSIGN.set_symbol(['=',])
_ASSIGN.set_final([1,])
transition_assign   = [{'=':'1'},
                       {'=':'E'}
                     ]
_ASSIGN.read_transition(transition_assign)
################################################
_COMPARISON = DFA_op()
_COMPARISON.set_name('COMPARISON')
_COMPARISON.set_symbol(['<','>','=','!'])
_COMPARISON.set_final([1,2,5,6,7,8])
transition_comparison   = [{'<':'1', '>':'2', '=':'3', '!':'4'},
                       {'<':'E', '>':'E', '=':'5', '!':'E'},
                       {'<':'E', '>':'E', '=':'6', '!':'E'},
                       {'<':'E', '>':'E', '=':'7', '!':'E'},
                       {'<':'E', '>':'E', '=':'8', '!':'E'},
                       {'<':'E', '>':'E', '=':'E', '!':'E'},
                       {'<':'E', '>':'E', '=':'E', '!':'E'},
                       {'<':'E', '>':'E', '=':'E', '!':'E'},
                       {'<':'E', '>':'E', '=':'E', '!':'E'}
                     ]
_COMPARISON.read_transition(transition_comparison)
################################################
_SEMI = DFA_op()
_SEMI.set_name('SEMI')
_SEMI.set_symbol([';',])
_SEMI.set_final([1,])
transition_semi      = [{';':'1'},
                       {';':'E'}
                     ]
_SEMI.read_transition(transition_semi)
################################################
_COMMA = DFA_op()
_COMMA.set_name('COMMA')
_COMMA.set_symbol([',',])
_COMMA.set_final([1,])
transition_comma    = [{',':'1'},
                       {',':'E'}
                     ]
_COMMA.read_transition(transition_comma)
################################################
_LBRACE = DFA_brace()
_LBRACE.set_name('LBRACE')
_LBRACE.set_symbol(['{',])
_LBRACE.set_final([1,])
transition_lbrace    = [{'{':'1'},
                       {'{':'E'}
                     ]
_LBRACE.read_transition(transition_lbrace)
################################################
_RBRACE = DFA_brace()
_RBRACE.set_name('RBRACE')
_RBRACE.set_symbol(['}',])
_RBRACE.set_final([1,])
transition_rbrace    = [{'}':'1'},
                       {'}':'E'}
                     ]
_RBRACE.read_transition(transition_rbrace)
################################################
_LPAREN = DFA_brace()
_LPAREN.set_name('LPAREN')
_LPAREN.set_symbol(['(',])
_LPAREN.set_final([1,])
transition_lparen    = [{'(':'1'},
                       {'(':'E'}
                     ]
_LPAREN.read_transition(transition_lparen)
################################################
_RPAREN = DFA_brace()
_RPAREN.set_name('RPAREN')
_RPAREN.set_symbol([')',])
_RPAREN.set_final([1,])
transition_rparen    = [{')':'1'},
                       {')':'E'}
                     ]
_RPAREN.read_transition(transition_rparen)
################################################
_LSQUARE = DFA_brace()
_LSQUARE.set_name('LSQUARE')
_LSQUARE.set_symbol(['[',])
_LSQUARE.set_final([1,])
transition_lsquare    = [{'[':'1'},
                       {'[':'E'}
                     ]
_LSQUARE.read_transition(transition_lsquare)
################################################
_RSQUARE = DFA_brace()
_RSQUARE.set_name('RSQUARE')
_RSQUARE.set_symbol([']',])
_RSQUARE.set_final([1,])
transition_rsquare    = [{']':'1'},
                       {']':'E'}
                     ]
_RSQUARE.read_transition(transition_rsquare)

##파일 읽기, output 파일 만들기

f = open(sys.argv[1], 'r')
lines = f.readlines()
f.close()

f2 = open("MyClass_output.txt", 'w')

##dfa 합치기
def mergedDFA(character, out1):
    _INT.analyzer(character,out1)
    _CHAR.analyzer(character,out1)
    _BOOL.analyzer(character,out1)
    _STRING.analyzer(character,out1)
    _INTEGER.analyzer(character,out1)
    _CHARACTER.analyzer(character,out1)
    _BOOLEAN.analyzer(character,out1)
    _LITERAL.analyzer(character,out1)
    _ID.analyzer(character,out1)
    _IF.analyzer(character,out1)
    _ELSE.analyzer(character,out1)
    _WHILE.analyzer(character,out1)
    _CLASS.analyzer(character,out1)
    _RETURN.analyzer(character,out1)
    _ADD.analyzer(character,out1)
    _SUB.analyzer(character,out1)
    _MUL.analyzer(character,out1)
    _DIV.analyzer(character,out1)
    _ASSIGN.analyzer(character,out1)
    _COMPARISON.analyzer(character,out1)
    _SEMI.analyzer(character,out1)
    _COMMA.analyzer(character,out1)
    _LBRACE.analyzer(character,out1)
    _RBRACE.analyzer(character,out1)
    _LPAREN.analyzer(character,out1)
    _RPAREN.analyzer(character,out1)
    _LSQUARE.analyzer(character,out1)
    _RSQUARE.analyzer(character,out1)

##input string 넣기. 한줄씩 넣어 처리. DFA에 속하지 않는 symbol이 오면
##유효한 string을 pop

for input_string in lines:
    out1 = []
    #_INTEGER.dfa_clear()

    mode_string = False
    for character in input_string: #Literal 의 경우 예외를 두어서 처리해야 할듯....ㅠㅠ
        if character == '\"' and mode_string == False:
            _LITERAL.analyzer(character,out1)
            mode_string = True
            continue
        elif character == '\"' and mode_string == True:
            mode_string = False
        
        if mode_string:
            _LITERAL.analyzer(character,out1)
        else:
            mergedDFA(character, out1)

    for idx in range(len(out1)): # 빼기와 음수 구별하기. 문맥상 SUB는 앞에 ID가 있거나 INTEGER가 있다는 걸 이용.
        if out1[idx][0] == 'SUB':
            if idx != 0:
                if out1[idx-1][0] != 'ID' and out1[idx-1][0] != 'INTEGER' and out1[idx+1][1] != '0':
                    out1[idx] = ['E']
            else:
                out1[idx] = ['E']

        if out1[idx][0] == 'INTEGER':
            if out1[idx][1][0] == '-' and out1[idx-1][0] == 'SUB':
                out1[idx][1] = out1[idx][1][1:]

        if out1[idx] != ['E']:
            f2.write('  '.join(out1[idx]))
            f2.write('\n')
   
f2.close()
