
import sys
import io
import time
import statistics
import tokenize
import tracemalloc
import token

ITERATIONS = 1000

def lex_python(source):
    result = []

    tokens = tokenize.generate_tokens(io.StringIO(source).readline)

    ignored = {
        tokenize.ENCODING,
        tokenize.ENDMARKER,
        tokenize.NL,
        tokenize.NEWLINE,
        tokenize.INDENT,
        tokenize.DEDENT,
    }

    for tok in tokens:
        if tok.type in ignored:
            continue

        if tok.type == tokenize.NAME:
            kind = "name"
        elif tok.type == tokenize.NUMBER:
            kind = "num"
        elif tok.type == tokenize.OP:
            kind = tok.string if tok.string not in "+-*/" else "+/-"
        elif tok.type == tokenize.STRING:
            kind = "string"
        elif tok.type == tokenize.COMMENT:
            kind = "comment"
        else:
            kind = token.tok_name.get(tok.type, str(tok.type))

        result.append((kind, tok.string))

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python harness.py <python-file>")
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            source = file.read()
    except (OSError, UnicodeError) as error:
        print(f"Error reading file: {error}")
        sys.exit(1)

    # Warm-up
    lex_python(source)

    times = []

    tracemalloc.start()
    baseline_current, _ = tracemalloc.get_traced_memory()

    for _ in range(ITERATIONS):
        start = time.perf_counter_ns()
        tokens = lex_python(source)
        end = time.perf_counter_ns()

        times.append((end - start) / 1_000_000)
        del tokens

    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Display tokens
    tokens = lex_python(source)

    for index, (kind, value) in enumerate(tokens, start=1):
        print(f"{index} {kind} {value!r}")

    median_time = statistics.median(times)
    memory_increase = max(0, peak_memory - baseline_current)

    print(f"\nIterations: {ITERATIONS}")
    print(f"Median time (ms): {median_time:.4f}")
    print(f"Peak traced memory increase (MB): "
          f"{memory_increase / (1024 * 1024):.4f}")


if __name__ == "__main__":
    main()
