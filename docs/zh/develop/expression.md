# 表达式

## 支持的表达式示例

字符串："字符串abc123"
如果字符串带有双引号或反斜杠，则需要进行转义，如："\""、"\\"
数值：123、-123、123.456、-123.456
布尔值：true、false
变量：var1
变量属性：var1.prop1、var1.prop1.prop2 
数组索引：arr1[0]、obj1.arr_prop[1]、a+b[0]+c[1].arr1[2]
运算表达式：var1+123、a-12+b、var1+(var2.prop1*10-2)、a==b && c!=d || e>f、var1 && !var2.prop1

## 支持的运算符

数学运算：+ - * / %
比较运算：== != > >= < <=
逻辑运算：&& || !
括号：()
数组索引：[]

## EBNF语法

```ebnf
(* 基础元素 *)
expression       = logical_or_expression ;

logical_or_expression
                 = logical_and_expression { "||" logical_and_expression } ;
                 
logical_and_expression
                 = equality_expression { "&&" equality_expression } ;

equality_expression
                 = relational_expression { ( "==" | "!=" ) relational_expression } ;

relational_expression
                 = additive_expression { ( ">" | ">=" | "<" | "<=" ) additive_expression } ;

additive_expression
                 = multiplicative_expression { ( "+" | "-" ) multiplicative_expression } ;

multiplicative_expression
                 = unary_expression { ( "*" | "/" | "%" ) unary_expression } ;

unary_expression = [ "!" ] primary_expression ;

primary_expression
                 = "(" expression ")"
                 | value ;

value            = text | number | boolean | variable ;

text             = '"' { character } '"' ;

number           = digit { digit } ;

boolean          = "true" | "false" ;

variable         = identifier { "." identifier | "[" expression "]" } ;

identifier       = letter { letter | digit | "_" } ;

(* 字符集定义 *)
digit            = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;

letter           = "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" 
                 | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" 
                 | "y" | "z" 
                 | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L"
                 | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X"
                 | "Y" | "Z" ;

character        = letter | digit | any printable character except '"' ;

```

