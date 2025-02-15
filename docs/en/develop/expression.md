# Expressions

## Supported Expression Examples

String: "string abc123"
If the string contains double quotes or backslashes, they need to be escaped, e.g., "\"", "\\"
Number: 123, -123, 123.456, -123.456
Boolean: true, false
Variable: var1
Variable property: var1.prop1, var1.prop1.prop2
Array index: arr1[0], obj1.arr_prop[1], a+b[0]+c[1].arr1[2]
Operation expression: var1+123, a-12+b, var1+(var2.prop1*10-2), a==b && c!=d || e>f, var1 && !var2.prop1

## Supported Operators

Mathematical operations: + - * / %
Comparison operations: == != > >= < <=
Logical operations: && || !
Parentheses: ()
Array index: []

## EBNF Syntax

```ebnf
(* Basic elements *)
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

(* Character set definitions *)
digit            = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;

letter           = "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" 
                 | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" 
                 | "y" | "z" 
                 | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L"
                 | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X"
                 | "Y" | "Z" ;

character        = letter | digit | any printable character except '"' ;

```