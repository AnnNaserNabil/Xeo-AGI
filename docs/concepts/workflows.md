# Workflows

Workflows in the Xeo framework allow you to define and execute sequences of tasks, with support for dependencies, error handling, and parallel execution.

## Key Concepts

### Task
A single unit of work with:
- A unique name
- An action (function or method) to execute
- Input parameters
- Dependencies on other tasks

### Workflow
A collection of tasks with defined dependencies that can be executed as a single unit.

## Creating a Workflow

### 1. Define Tasks

```python
from xeo import TaskDefinition

# Simple task with no dependencies
task1 = TaskDefinition(
    name="fetch_data",
    action=fetch_data_function,
    parameters={"source": "api"}
)

# Task that depends on fetch_data
task2 = TaskDefinition(
    name="process_data",
    action=process_data_function,
    depends_on=["fetch_data"]  # This task will only run after fetch_data completes
)
```

### 2. Create and Run a Workflow

```python
from xeo import Workflow

# Create workflow
workflow = Workflow("data_processing")

# Add tasks
workflow.add_task(task1)
workflow.add_task(task2)

# Run the workflow
results = await workflow.run()
```

## Task Dependencies

Dependencies are defined using the `depends_on` parameter:

```python
task_a = TaskDefinition("task_a", action_a)
task_b = TaskDefinition("task_b", action_b, depends_on=["task_a"])
task_c = TaskDefinition("task_c", action_c, depends_on=["task_a"])
task_d = TaskDefinition("task_d", action_d, depends_on=["task_b", "task_c"])
```

This creates the following dependency graph:
```
   task_a
   /    \
 task_b  task_c
   \    /
   task_d
```

## Error Handling

Workflows include built-in error handling:

```python
# Task with retry logic
task = TaskDefinition(
    name="api_call",
    action=make_api_call,
    retry_count=3,  # Retry up to 3 times on failure
    retry_delay=5.0  # Wait 5 seconds between retries
)

# Handle task failure in the workflow
workflow.on_task_failure("api_call", handle_api_failure)
```

## Parallel Execution

Independent tasks run in parallel by default:

```python
# These tasks will run in parallel
task1 = TaskDefinition("fetch_users", fetch_users)
task2 = TaskDefinition("fetch_products", fetch_products)

# This task runs after both complete
task3 = TaskDefinition("process_all", process_data, depends_on=["fetch_users", "fetch_products"])
```

## Workflow Events

You can hook into workflow events:

```python
# Called when workflow starts
workflow.on_start(lambda: print("Workflow started"))

# Called when workflow completes
workflow.on_complete(lambda results: print(f"Workflow completed: {results}"))

# Called if workflow fails
workflow.on_failure(lambda error: print(f"Workflow failed: {error}"))
```

## Example: Data Processing Pipeline

```python
from xeo import Workflow, TaskDefinition

async def extract():
    print("Extracting data...")
    return ["data1", "data2", "data3"]

async def transform(data):
    print(f"Transforming {len(data)} items...")
    return [d.upper() for d in data]

async def load(data):
    print(f"Loading {len(data)} items...")
    return f"Loaded {len(data)} items"

# Create workflow
pipeline = Workflow("etl_pipeline")

# Define tasks
extract_task = TaskDefinition("extract", extract)
transform_task = TaskDefinition("transform", transform, 
    parameters={"data": "${tasks.extract.output}"},
    depends_on=["extract"]
)
load_task = TaskDefinition("load", load,
    parameters={"data": "${tasks.transform.output}"},
    depends_on=["transform"]
)

# Add tasks to workflow
pipeline.add_task(extract_task)
pipeline.add_task(transform_task)
pipeline.add_task(load_task)

# Run the workflow
results = await pipeline.run()
print(results["load"])  # Output: Loaded 3 items
```

## Best Practices

1. **Task Granularity**: Keep tasks focused and single-purpose
2. **Error Handling**: Implement proper error handling at both task and workflow levels
3. **Idempotency**: Design tasks to be idempotent when possible
4. **Logging**: Include detailed logging for debugging
5. **Testing**: Test workflows with various input scenarios

## Next Steps

- Learn about [Advanced Workflow Patterns](../../use_cases/advanced/complex_workflows.md)
- Explore [Workflow API Reference](../../api/workflow.md)
- See [Real-world Examples](../../use_cases/)
