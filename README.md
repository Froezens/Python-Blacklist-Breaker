# Parselmouth

Parselmouth is an automated Python sandbox-escape payload bypass framework that helps security researchers discover viable payload variants under strict character blacklist constraints.
It automates Python sandbox bypassing by exploring AST-level transformations, minimizing payload length, and enumerating bypass strategies under character restrictions.


## Highlights

* **Automated AST Visitors**: Breaks payloads into AST components and assembles multiple bypass strategies.
* **Character Blacklist/Whitelist**: Supports both per-character rules and regular-expression–based rules.
* **Multi-dimensional Optimal Search**: Can simultaneously seek the shortest expression (`--minlen`) and the smallest character set (`--minset`).
* **Pluggable Bypass Toolkit**: Extend `by_*` strategies easily through `bypass_tools.py`.
* **Highly Visual Debugging**: Multiple verbosity levels (`-v`) to inspect each attempt in detail.
* **Built-in Testing Framework**: Use `test_case.py` + `run_test.py` for quick regression tests.

---

## Quick Start

### Requirements

* Python `>= 3.10`

### Installation

```bash
pip install -r requirements.txt
```

---

## CLI Usage

Display help:

```bash
python parselmouth.py -h
```

Typical usage:

```bash
python parselmouth.py \
  --payload "__import__('os').popen('whoami').read()" \
  --rule "__" "." "'" '"' "read" "chr" \
  --minlen \
  -v
```

Key parameters:

* `--rule`: List characters to blacklist; mutually exclusive with `--re-rule`.
* `--re-rule`: Define blacklist using regular expressions (e.g., `--re-rule '[0-9]'` to block all digits).
* `--specify-bypass`: Fine-grained bypass class/method blacklisting or whitelisting, e.g.
  `--specify-bypass '{"black":{"Bypass_Int":["by_unicode"]}}'`
* `--minlen` / `--minset`: Search for shortest expression / minimal character set.
* `-v`, `-vv`: Verbosity levels; `-vv` shows debug-level logs.

> ⚠️ On Windows terminals, double quotes must be passed as `"\\""` to avoid shell-parsing issues.

### Testing Custom Strategies

Add your payload, rules, and expected results in `test_case.py`, then run:

```bash
python run_test.py
```

---

## Library Usage

```python
import parselmouth as p9h

p9h.BLACK_CHAR = {"kwd": [".", "'", '"', "chr", "dict"]}
# or using regex:
# p9h.BLACK_CHAR = {"re_kwd": r"\.|'|\"|chr|dict"}

runner = p9h.P9H(
    "__import__('os').popen('whoami').read()",
    specify_bypass_map={"black": {"Bypass_Name": ["by_unicode"]}},
    min_len=True,
    versbose=0,
)

result = runner.visit()
status, colored = p9h.color_check(result)
print(status, colored, result)
```

`P9H` key parameters:

* `source_code`: Payload to bypass.
* `specify_bypass_map`: Blacklist/whitelist for bypass classes/methods.
* `min_len`: Search for shortest expression.
* `versbose`: Log level (`0`–`3`, default 0).
* `depth`: Indentation control for printing; usually no need to modify.
* `bypass_history`: Cache for known success/failure results, e.g.
  `{"success": {}, "failed": []}`.

---

## Customization

Before extending the framework, it is strongly recommended to read
[this detailed explanation](https://www.tr0y.wang/2024/03/04/parselmouth/)
as well as `parselmouth.py` and `bypass_tools.py`.

1. **Guide**: [Customization Tutorial](https://www.tr0y.wang/2024/03/04/parselmouth/#%E5%AE%9A%E5%88%B6%E5%8C%96%E5%BC%80%E5%8F%91)
2. **Add New AST Types**: Implement new `visit_*` methods inside `P9H` in `parselmouth.py`.
3. **Custom Checkers**: Override `check` to interact with the target.
   Returning an empty list `[]` means success; non-empty means failure.
4. **Extend Bypass Strategies**: Add new `by_*` methods inside the corresponding class in `bypass_tools.py`.
   The ordering determines priority.

---

## Bypass Catalog

> This table preserves the original content for quick reference.
> More combinations can be found in the CLI output.

### Integer Bypass

| Class      | Method     | Payload | Bypass        | Description    |
| ---------- | ---------- | ------- | ------------- | -------------- |
| Bypass_Int | by_trans   | `0`     | `len(())`     |                |
| Bypass_Int | by_bin     | `10`    | `0b1010`      | binary         |
| Bypass_Int | by_hex     | `10`    | `0xa`         | hex            |
| Bypass_Int | by_cal     | `10`    | `5*2`         | arithmetic     |
| Bypass_Int | by_unicode | `10`    | `int('𝟣𝟢')` | unicode digits |
| Bypass_Int | by_ord     | `10`    | `ord('\n')`   | ord-based      |

### String Bypass

| Class         | Method            | Payload        | Bypass                              | Description      |
| ------------- | ----------------- | -------------- | ----------------------------------- | ---------------- |
| Bypass_String | by_empty_str      | `""`           | `str()`                             | empty string     |
| Bypass_String | by_quote_trans    | `"macr0phag3"` | `'macr0phag3'`                      | quote swap       |
| Bypass_String | by_reverse        | `"macr0phag3"` | `"3gahp0rcam"[::-1]`                | reverse          |
| Bypass_String | by_char           | `"macr0phag3"` | `chr` concatenation                 | per-char         |
| Bypass_String | by_dict           | `"macr0phag3"` | `list(dict(amacr0phag3=()))[0][1:]` | dict trick       |
| Bypass_String | by_bytes_single   | `"macr0phag3"` | `str(bytes([109]))[2] + ...`        | single-byte      |
| Bypass_String | by_bytes_full     | `"macr0phag3"` | `bytes([...])`                      | full bytes       |
| Bypass_String | by_join_map_str   | `"macr0phag3"` | `str().join(map(chr, [...] ))`      | join + map       |
| Bypass_String | by_format         | `"macr0phag3"` | `'{}...'.format(...)`               | format           |
| Bypass_String | by_hex_encode     | `"macr0phag3"` | `"\x6d..."`                         | hex encoding     |
| Bypass_String | by_unicode_encode | `"macr0phag3"` | `"\u006d..."`                       | unicode encoding |
| Bypass_String | by_char_format    | `"macr0phag3"` | `"%c%c..." % (...)`                 | `%c` formatting  |
| Bypass_String | by_char_add       | `"macr0phag3"` | `'m'+'a'+...`                       | string addition  |

### Name Bypass

| Class       | Method      | Payload      | Bypass                    | Description         |
| ----------- | ----------- | ------------ | ------------------------- | ------------------- |
| Bypass_Name | by_unicode  | `__import__` | `_＿import_＿`              | unicode identifiers |
| Bypass_Name | by_builtins | `__import__` | `__builtins__.__import__` | via builtins        |

### Attribute Bypass

| Class            | Method     | Payload    | Bypass                 | Description |
| ---------------- | ---------- | ---------- | ---------------------- | ----------- |
| Bypass_Attribute | by_getattr | `str.find` | `getattr(str, 'find')` | `getattr`   |
| Bypass_Attribute | by_getattr | `str.find` | `vars(str)["find"]`    | `vars`      |
| Bypass_Attribute | by_getattr | `str.find` | `str.__dict__["find"]` | `__dict__`  |

### Keyword Bypass

| Class          | Method     | Payload         | Bypass          | Description     |
| -------------- | ---------- | --------------- | --------------- | --------------- |
| Bypass_Keyword | by_unicode | `str(object=1)` | `str(ᵒbject=1)` | unicode keyword |

### Boolean Operation Bypass

| Class         | Method        | Payload                | Bypass                        | Description |   |
| ------------- | ------------- | ---------------------- | ----------------------------- | ----------- | - |
| Bypass_BoolOp | by_bitwise    | `1 and (2 or 3)`       | `1&(2\|3)`                    | `and/or → & | ` |
| Bypass_BoolOp | by_arithmetic | `(__import__ and ...)` | `bool(bool(__imp𝒐rt__)*...)` | arithmetic  |   |

More combinations and contributions are collected in `challenges` and issue discussions.

## Contributing

If you would like to contribute to this project, please leave a star in the repo.

## Roadmap

* [x] `--re-rule` regex blacklist
* [x] Payload character-set minimization (greedy)
* [x] Display available bypass techniques
* [x] Unit-test improvements
* [ ] `exec` / `eval` + `open` to run library code
* [x] `'__builtins__'` → hex/Unicode encoding
* [x] `"os"` → `"o" + "s"`
* [ ] `'__buil''tins__'` → `str.__add__('__buil', 'tins__')`
* [x] `'__buil''tins__'` → `%c` formatting
* [x] `__import__` → `getattr(__builtins__, "__import__")`
* [ ] `__import__` → `__loader__().load_module`
* [x] `str.find` → `vars(str)["find"]`
* [x] `str.find` → `str.__dict__["find"]`
* [ ] `",".join("123")` → `str.join(",", "123")`
* [ ] `"123"[0]` → `"123".__getitem__(0)`
* [ ] `"0123456789"` → `sorted(set(str(hash(()))))`
* [ ] `{"a": 1}["a"]` → `{"a": 1}.pop("a")`
* [ ] More operator/iterator/boolean/generator equivalents…

(The original TODO list is preserved for community tracking.)

## License
This project is licensed under the **MIT License**. See the `LICENSE` file for details.

