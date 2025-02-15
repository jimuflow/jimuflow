# Component Error Handling

Add an attribute to the component definition to indicate whether error handling is supported.

Add error handling-related configuration parameters to the node configuration in the process definition.

There are three ways to handle errors: retry, ignore errors and continue execution, and terminate.

Retry configuration: number of retries, retry interval

Ignore errors and continue execution configuration: output parameter configuration

Termination does not require configuration; errors are directly thrown.