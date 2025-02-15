# Type System

The type system needs to support the following features:
1. Expressions should support accessing type attributes.
2. Expression input prompts should support suggesting the currently accessible attributes of a type.
Implementation method: Infer the result type of the expression, then look up the definition of that type, and retrieve the list of attributes from the type definition.
Type registration: The execution engine will automatically register built-in types upon startup, and then automatically register types provided by components when scanning them.