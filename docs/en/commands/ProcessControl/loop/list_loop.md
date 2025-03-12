# List Loop

Loop through each element in the list and then execute the instructions within the loop.

## Instruction Configuration

![List Loop Configuration Dialog Box](list_loop_config.png)

### List

Enter the list expression to be traversed.

### Loop Item

Enter the variable name used to save the elements in the list.

## Usage Example

![Screenshot of List Loop Example Process](list_loop_demo_process.png)

The execution logic of this process is as follows:

1. Parse the JSON list data and save it to the variable `list`.
2. Loop through each element in the `list`, save the current item to the variable `current_value`, and then execute the instructions within the loop.
    1. Print the variable `current_value`.

Running Log:

![Running Log of List Loop Example Process](list_loop_demo_log.png)

Application download link: [Example Application of List Loop](../../../examples/list_loop_demo.zip)
