"""A module for automatic test cases and writing test boilerplate

TODO - Create tests
"""

import re
import traceback

def create_tests_from_test_cases(
        test_module:str,
        test_function_name:str,
        test_cases:list,
        number_of_args=1,
        let_crash=True
) -> None:

    """Creates unit tests for complex / repetitive test cases

    :param test_module: The full path for the module being tested in dot notation (e.g. 'src.foo.bar')
    :type test_module: str
    :param test_function_name: The name of the function being tested
    :type test_function_name: str
    :param test_cases: A list of dictionaries, each dictionary containing one test case (see below)
    :type test_cases: list
    :param number_of_args: The number of arguments in test_function_name
    :param let_crash: If True (default), allows this function to crash so that test cases can be debugged.
        If False, all test cases will run and failed tests will have errors and traceback printed inside Python comments
    :type let_crash: bool
    :returns None
    :rtype: None

    ## Warning
    This function uses:
     - exec() on test_module_path and test_function_name
     - eval() on test_function_name and your args and kwargs.
     Do not pass unsafe code through these parameters.

    ## Rationale
    Writing tests manually can be prone to errors when:
    - creating many tests (e.g. missing cases),
    - copying and pasting oexisting tests to create new tests (e.g. duplicating test function names, copying and using the wrong args/kwargs, etc.), and
    - the args, kwargs and/or results are intricate (and manually writing test cases is error-prone).

    This function provides a more reliable (and potentially faster) method for creating a large number of tests for complex test cases.

    ## Usage
    Define test_module_path and test_function_name, which will be run as:

            from {test_module} import {test_function_name}

    Define a list of test cases, each defined by a dictionary:

            test_cases = [

                #Note: The args key below expects a *list* of args, e.g. [arg1, arg2]. Wrap a single arg in square brackets!

                {
    'description': 'AND parent AND child OR grandchild',
                    'args': [['*', 'a', 'b', ['*', 'c', 'd', ['e', 'f']]]],
                    'kwargs': {'sort_results': True}
                },
                {
    'description': 'AND parent OR child AND grandchild (unsorted)',
                    'args': [['*', 'a', 'b', ['c', 'd', ['*', 'e', 'f']]]],
                    'kwargs': {'sort_results': False}
                },
                # etc.
            ]

            test_module_path = 'src.foo.bar.my_awesome_module'
            test_function_name = 'my_awesome_function'

    Run this function and the args and kwargs for each test case will be passed through the test function.
    The results will appear in stdout (and in your clipboard if pyperclip is available), showing the result of the test:

            class TestMyAwesomeFunction(unittest.TestCase):

            # AND parent AND child OR grandchild
            # args:    ['*', 'a', 'b', ['*', 'c', 'd', ['e', 'f']]]
            # kwargs:  sort_results=True
            # expect:  [no 'expect' key in test data]
            # result:  [['*', 'a', 'b', 'c', 'd', 'e'], ['*', 'a', 'b', 'c', 'd', 'f']]


            # AND parent OR child AND grandchild (unsorted)
            # args:    ['*', 'a', 'b', ['c', 'd', ['*', 'e', 'f']]]
            # kwargs:  sort_results=False
            # expect:  [no 'expect' key in test data]
            # result:  [['*', 'a', 'b', 'c'], ['*', 'a', 'b', 'd'], ['*', 'a', 'b', 'e', 'f']]

    If the result for the first test is correct, create an 'expect' key in the first test case and copy the result text in:

            test_cases = [

                #Note: The args key below expects a *list* of args, e.g. [arg1, arg2]. Wrap a single arg in square brackets!

                {
    'description': 'AND parent AND child OR grandchild',
                    'args': [['*', 'a', 'b', ['*', 'c', 'd', ['e', 'f']]]],
                    'kwargs': {'sort_results': True},
                    'expect': [['*', 'a', 'b', 'c', 'd', 'e'], ['*', 'a', 'b', 'c', 'd', 'f']]
                },
                # etc.
            ]

    Rerun this function, and the following test will appear in stdout (and your clipboard):

            class TesttMyAwesomeFunction(unittest.TestCase):

                def test_and_parent_and_child_or_grandchild(self):
                    # AND parent AND child OR grandchild
                    assert test_function_name(['*', 'a', 'b', ['*', 'c', 'd', ['e', 'f']]], sort_results=True) == [['*', 'a', 'b', 'c', 'd', 'e'], ['*', 'a', 'b', 'c', 'd', 'f']]

            # AND parent OR child AND grandchild (unsorted)
            # args:    ['*', 'a', 'b', ['c', 'd', ['*', 'e', 'f']]]
            # kwargs:  sort_results=False
            # expect:  [no 'expect' key in test data]
            # result:  [['*', 'a', 'b', 'c'], ['*', 'a', 'b', 'd'], ['*', 'a', 'b', 'e', 'f']]

    Continue rerunning tests (and debugging your function) until all of your tests pass:

        class TestMyAwesomeFunction(unittest.TestCase):

            def test_and_parent_and_child_or_grandchild(self):
                # AND parent AND child OR grandchild
                assert my_awesome_function(['*', 'a', 'b', ['*', 'c', 'd', ['e', 'f']]], sort_results=True) == [['*', 'a', 'b', 'c', 'd', 'e'], ['*', 'a', 'b', 'c', 'd', 'f']]


           def test_and_parent_or_child_and_grandchild_unsorted(self):
                # AND parent OR child AND grandchild (unsorted)
                assert my_awesome_function(['*', 'a', 'b', ['c', 'd', ['*', 'e', 'f']]], sort_results=False) == [['*', 'a', 'b', 'c'], ['*', 'a', 'b', 'd'], ['*', 'a', 'b', 'e', 'f']]

    Copy the output to the module containing your unit tests.

    To create a comment in your tests which is independent of a test case, create a dictionary with only a comment key:

            {
                'comment': 'This comment is independent of a test case (and will be included in the output)'
            }

    This function will warn you in stdout and the clipboard text (as Python-commented text) if:
    - your code crashes,
    - tests fail,
    - you have duplicated a description (which will create a duplicate function, one of which won't run in tests),
    - you have reused your args and kwargs (if both your args and kwargs are the same as a previous test).

    If let_crash=True, this function will raise an error (and stop) so that you can debug the first error thrown by
    your test cases. your code. Otherwise the function handle exceptions and run all test cases (and errors
    and tracebacks will appear as python comments in stdout and your clipboard).
    """

    # Import the module and function to be tested
    try:
        # TODO Fix this import kluge
        exec(f'from {test_module} import {test_function_name}')
    except ImportError:
        print(f'Sorry, the test_module_path \'{test_module}\' and test_function_name {test_function_name} '
              f'could not be imported')

    # Attempt to load pyperclip from the environment (for automatic copying of results to the clipboard)
    try:
        import pyperclip
        use_pyperclip = True
    except ImportError:
        use_pyperclip = False

    # To avoid copy/paste errors and duplicated tests, track:
        # 1. Whether descriptions are reused (which would create a duplicate test functions which won't run)
    descriptions_already_used = []

    # 2. Whether an args/kwargs combo has been reused accidentally
    args_and_kwargs_already_used = []

    # Render the class name to be used when creating a test function for this case
    function_name_in_upper_camel_case = ''.join([word[0:1].upper() + word[1:] for word in
                                                 test_function_name.lower().split('_')])

    # Store output for copying to clipboard (if pyperclip installed)
    output = f'class Test{function_name_in_upper_camel_case}(unittest.TestCase):\n\n'
    print (output)

    for test_case in test_cases:
        output_for_test_case = ''

        # Get metadata
        description = test_case.get('description')
        comment = test_case.get('comment')

        if comment and not description:
            # This is not a test, it's a comment to be reposted to the output
            output_for_test_case = f'    # {comment}\n\n'
            print (output_for_test_case)
            output += output_for_test_case
            continue

        # Get and check args
        args_rendered = ''
        args = test_case.get('args')
        if number_of_args == 0:
            if args:
                output_for_test_case += ('# !!! number_of_args == 0 but args were provided !!!')
        elif number_of_args == 1:
            args_rendered = str(args)
        elif number_of_args > 1:
            # The args must be in an iterable
            args_as_strings = [str(arg) for arg in args]
            if number_of_args != len(args_as_strings):
                output_for_test_case += (f'# !!! number_of_args == {number_of_args} but {len(args_as_strings)} '
                                         'args were provided !!!')
            args_rendered = ', '.join(args_as_strings)

        # Get kwargs
        kwargs = test_case.get('kwargs')
        if kwargs:
            kwargs_rendered = ', '.join([f'{k}={v}' for k, v in kwargs.items()])
        else:
            # No printed warning for missing kwags
            kwargs_rendered = ''

        # Obtain the 'expect' key if present
        expect = None
        expect_key_present = False
        if 'expect' in test_case:
            expect = test_case.get('expect')
            expect_key_present = True

        # Create the normalized description text
        description_as_function_name = re.sub('[^a-zA-Z0-9_]', '', description.replace(" ", "_").lower())
        if description_as_function_name not in descriptions_already_used:
            descriptions_already_used.append(description_as_function_name)
        else:
           output_for_test_case += f'# !!! THIS DESCRIPTION (AND TEST FUNCTION NAME) HAS ALREADY BEEN USED !!!\n'

        # Check for copied args and kargs
        args_and_kwargs = args_rendered + kwargs_rendered
        if args_and_kwargs not in args_and_kwargs_already_used:
            args_and_kwargs_already_used.append(args_and_kwargs)
        else:
            output_for_test_case += f'# !!! THIS SET OF ARGS AND KWARGS HAS ALREADY BEEN USED !!!\n'

        # Render and eval() the code string
        code = ''
        try:
            if args_rendered and kwargs_rendered:
                code = f'{test_function_name}({args_rendered}, {kwargs_rendered})'
                result = eval(code)
            elif args_rendered:
                code = f'{test_function_name}({args_rendered})'
                result = eval(code)
            elif kwargs_rendered:
                code = f'{test_function_name}({kwargs_rendered})'
                result = eval(code)
            else:
                code = f'{test_function_name}()'
                result = eval(code)
                output_for_test_case += '# !!! There were no args or kwargs - is that what you wanted? !!!\n'

            # Check the result
            if expect_key_present and result == expect:
                # The result was equal to the value to the 'expect' key in this test case
                output_for_test_case += f'    def test_{description_as_function_name}(self):\n'
                output_for_test_case += f'        # {description}\n'
                if comment:
                    output_for_test_case += f'        # {comment}\n'
                output_for_test_case += f"        assert {code} == {result}\n\n\n"
            else:
                # The result was NOT equal to the value to the 'expect' key in this test case
                if expect_key_present:
                    output_for_test_case += f'# !!! TEST FAILED (RESULT <> EXPECT) !!!\n'
                output_for_test_case += f'# {description}\n'
                if comment:
                    output_for_test_case += f'        # {comment}\n'
                if args:
                    output_for_test_case += f'# args:    {args_rendered}\n'
                if kwargs:
                    output_for_test_case += f'# kwargs:  {kwargs_rendered}\n'
                if expect_key_present:
                    output_for_test_case += f'# expect:  {expect}\n'
                else:
                    output_for_test_case += f'# expect:  [no \'expect\' key in test data]\n'
                output_for_test_case += f'# result:  {result}\n\n'

            # Print this test case to stdout
            print(output_for_test_case)
            # Add the output for this test case to the overall output (for copying to the clipboard if pyperclip available)
            output += output_for_test_case

        except Exception as e:
            # The test function crashed
            output_for_test_case += '# !!! EXECUTION ERROR !!!\n'
            output_for_test_case += f'# {description}\n'
            output_for_test_case += f'# code:    {code}\n'
            if comment:
                output_for_test_case += f'# {comment}\n'
            if args:
               output_for_test_case += f'# args:    {args_rendered}\n'
            if kwargs:
                output_for_test_case += f'# kwargs:  {kwargs_rendered}\n'
            if expect_key_present:
                output_for_test_case += f'# expect:  {expect}\n'
            output_for_test_case += f'# ERROR:   {str(e)}\n'

            # If requested, let it crash (or add the traceback within Python comments)
            if let_crash == True:
                raise
            else:
                tb = traceback.format_exc()
                output_for_test_case += "'''\n"
                output_for_test_case += str(tb)
                output_for_test_case += "'''\n\n"
            print(output_for_test_case)
            output += output_for_test_case

    # Copy all output to the clipboard if pyperclip available
    if use_pyperclip:
        pyperclip.copy(output)
        print('# Results copied to the clipboard (Ctrl-V to paste)')
