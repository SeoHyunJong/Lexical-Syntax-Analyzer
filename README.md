# Lexical-Syntax-Analyzer
CAUCSE 2021

Specifying Tokens

TOKEN NAME	REGULAR EXPRESSION
INT	int
CHAR	char
BOOL	bool
STRING	String
INTEGER	0|(-|e)(PositiveDigit*)
Positive = 1|2|3|…|9
Digit = 0|1|2|3|…|9
CHARACTER	‘(Digit|Letter|Blank)’
Letter = a|b|c…|A|B|…|Z
Blank = 
BOOLEAN	true|false
LITERAL	“(Digit|Letter|Blank)*”
ID	(Letter|_)(Letter|Digit|_)*
IF	if
ELSE	else
WHILE	while
CLASS	class
RETURN	return
ADD	+
SUB	-
MUL	*
DIV	/
ASSIGN	=
COMPARISON	<|>|==|!=|<=|>=
SEMI	;
LBRACE	{
RBRACE	}
LPAREN	(
RPAREN	)
LSQUARE	[
RSQUARE	]
COMMA	,
WHITESPACE	(\t|\n)(\t|\n)*

