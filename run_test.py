import doctest
import test_case
import re
import ast

import parselmouth as p9h


def evaluate_test_case(runner: doctest.DocTestRunner):
    """
    Evaluate a single doctest runner instance, summarize results,
    and compute coverage for bypass functions.
    """
    # Test examples: example[0] contains bypass_class name, others contain tests
    test_examples = runner.test.examples[1:]
    first_case_source = runner.test.examples[0].source

    # Extract class and function names from doctest source
    bypass_class = re.findall(r"(Bypass_\w+)", first_case_source)[0]
    bypass_functions_called = {
        re.findall(r"(by_\w+)", example.source)[0]
        for example in test_examples
    }

    # Retrieve all bypass functions from corresponding class
    class_attributes = vars(getattr(p9h.bypass_tools, bypass_class, dict))
    all_bypass_functions = {
        name for name in class_attributes if name.startswith("by_")
    }

    # Print summary header
    print(f"\n[*] {bypass_class}")

    total_tests = runner.tries - 1
    successful_tests = total_tests - runner.failures

    # Accuracy output
    accuracy_msg = (
        f"{successful_tests}/{total_tests}="
        f"{100 * round(successful_tests / total_tests, 2)}%"
    )
    if runner.failures:
        accuracy_msg += f", failed {runner.failures} cases"

    print(
        "  [-] Bypass accuracy: "
        + p9h.put_color(
            accuracy_msg,
            "yellow" if runner.failures else "green"
        )
    )

    # Coverage output (skip for "Bypass_Combo")
    if bypass_class != "Bypass_Combo":
        coverage_msg = (
            f"{len(bypass_functions_called)}/{len(all_bypass_functions)}="
            f"{100 * round(len(bypass_functions_called) / len(all_bypass_functions), 2)}%"
        )
        missing_tests = all_bypass_functions - bypass_functions_called
        if missing_tests:
            coverage_msg += f", untested: {missing_tests}"

        print(
            "  [-] Bypass test coverage: "
            + p9h.put_color(
                coverage_msg,
                "yellow" if bypass_functions_called != all_bypass_functions else "green",
            )
        )

    return successful_tests, runner.failures, total_tests


# Display logo
print(p9h.logo)

# Discover doctest tests
finder = doctest.DocTestFinder()
test_suites = finder.find(test_case)

total_success = total_failures = total_attempts = 0
collected_cases = []

# Run tests in reverse order (original behavior)
for test in test_suites[::-1]:
    runner = doctest.DocTestRunner()
    runner.run(test)

    success, failed, attempts = evaluate_test_case(runner)
    total_success += success
    total_failures += failed
    total_attempts += attempts

    # Extract detailed case records for final summary output
    for example in runner.test.examples[1:]:
        expected_output = example.want.strip()
        parsed_source = ast.parse(example.source).body

        args = parsed_source[-1].value.args

        # Determine bypass map (assignment or direct argument)
        if isinstance(parsed_source[0], ast.Assign):
            bypass_map = ast.unparse(parsed_source[0].value)
        else:
            bypass_map = args[0].value

        collected_cases.append([args[1].value, args[3].value, bypass_map, expected_output])

# Print summary of all recorded cases
print()
for index, case in enumerate(collected_cases):
    print(
        f"[{index + 1}]",
        p9h.put_color(case[0], "blue"),
        "with",
        p9h.put_color(case[1], "cyan"),
        "by",
        p9h.put_color(case[2], "white"),
        "=>",
        p9h.put_color(case[3], "green"),
    )

# Print total summary
print(f"\n[*] Total number of test cases: {p9h.put_color(total_attempts, 'cyan')}")
if total_failures:
    print(p9h.put_color(f"[!] {total_failures} case(s) failed", "yellow"))
else:
    print(p9h.put_color("[*] All test cases passed successfully", "green"))

# print(collected_cases)  # Debug option
