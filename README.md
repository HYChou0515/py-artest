# Artest: Auto Regression Test


Imagine you have a software program, and you want to create a regression test case for a specific function within it. 
🔬 To achieve this, it's best to simulate real-life scenarios. 
🌍 This is where Artest, a useful tool, comes into play. 
Artest automates the process of generating test cases while your program is running. 
🤖 These test cases are then stored in a designated directory. 
📂 When you make future modifications to your program, 
you can rely on the previously generated test cases to ensure that everything continues to work smoothly. 
👌 This approach safeguards the stability and dependability of 
your program by preventing unexpected issues and accidental breakdowns. 🚀

## Installation

You can install Artest using pip:

```bash
pip install py-artest
```

This will install Artest and its dependencies. 
Optionally, if you require the 'dill' package for additional functionality, 
you can install it as follows:

```bash
pip install py-artest[dill]
```

## Advantages 


- Automation 🤖: Artest automates the process of generating test cases for your software program while it is running, saving you time and effort in creating them manually.
- Real-life Scenarios 🌟: Artest allows you to simulate real-life scenarios for regression testing, enabling you to validate your program's behavior in a more realistic context.
- Test Case Storage 📂: Artest stores the generated test cases in a designated directory, making it easy to access and manage them.
- Regression Testing 👨‍💻: By relying on previously generated test cases, Artest enables you to perform regression testing. This means you can run the tests after making future modifications to ensure that the program continues to function correctly, catching any unexpected issues or breakdowns.
- Stability and Dependability 🚀: Utilizing Artest's generated test cases helps safeguard the stability and dependability of your program. By identifying and preventing issues early on, it ensures that your program remains reliable and performs as expected.

## Basic use case: autoreg

Let's consider a program written in Python:


```python
def hello(say):
    to = to_whom(1)
    return f"{say} {to}!"

def to_whom(x):
    choices = read_from_db()
    # choices = ["sir", "world",]
    return choices[x]

if __name__ == "__main__":
    print(hello("hello"))
    # Output: hello world!
```

In this program, you only need to add a decorator called autoreg to the hello function:

```python
from artest import autoreg

@autoreg("a5f4cb0f")  # 🎉 add this to auto create test case
def hello(say):
    to = to_whom(1)
    return f"{say} {to}!"

def to_whom(x):
    choices = read_from_db()
    # choices = ["sir", "world",]
    return choices[x]

if __name__ == "__main__":
    print(hello("hello"))
    # Output: hello world!
```

By applying the autoreg decorator, 
you enable the creation of a test case associated with the 
unique function id `a5f4cb0f`
whenever the hello function is called.
The test case generation is done automatically.
In this updated version, we still have the to_whom function to determine the value of to.
When running the program, the output remains the same: "hello world!".

## Mocking with automock
In situations where the to_whom function takes a long time to execute or is not available during testing, you can create a mock instead. A mock is a simulated function that returns predefined values specifically defined in the test case.

To automatically create a mock, you can use the automock decorator. When applied to a function, Artest will generate the mock for you.

```python
from artest import autoreg, automock

@autoreg("a5f4cb0f")
def hello(say):
    to = to_whom(1)
    return f"{say} {to}!"

@automock("35988d25")  # 🎉 add this to auto create mock function
def to_whom(x):
    choices = read_from_db()
    # choices = ["sir", "world",]
    return choices[x]

if __name__ == "__main__":
    print(hello("hello"))
    # Output: hello world!
```

In the updated code, the to_whom function has been decorated with automock 
using the unique identifier "35988d25". 
This allows Artest to automatically generate a mock for the to_whom function. 
Inside the mock, the choices variable is typically defined in the test case 
rather than being fetched from the database, 
ensuring faster and more controlled testing.

When running the program, the output remains the same: "hello world!".


## Test with artest

Once artest is installed, you can run it in test mode using the command:

```bash
python -m artest
```

This command executes artest in test mode, 
allowing the framework to manage and execute the defined test cases 
based on the configured environment. 
Running artest in test mode enables the verification and 
validation of your program's behavior against the predefined test cases, 
ensuring that the functionality operates as expected 
and remains stable even after modifications.
