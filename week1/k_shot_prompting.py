from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 5

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """
You are a strict, deterministic character-by-character reversing machine.

GOAL
Given an input telling you a string S, output exactly reverse(S) at the CHARACTER level.

NON-NEGOTIABLE RULES
1) Treat S as raw characters. Do NOT split into words/tokens/substrings (e.g., "httpstatus" is NOT "http"+"status").
2) Do NOT add, remove, substitute, or normalize characters. Preserve every character exactly once.
3) Output must be EXACTLY ONE LINE containing ONLY the reversed string. No quotes. No extra spaces. No punctuation.
4) Output length must equal input length.

MANDATORY INTERNAL PROCEDURE (do NOT print any steps)
A) Copy S exactly as considered characters c0 c1 c2 ... c(n-1).
B) Construct output by writing c(n-1) c(n-2) ... c0.
C) Self-check before answering:
   - first(output) == last(S)
   - last(output) == first(S)
   - len(output) == len(S)
   If any check fails, redo steps A-B.

EXAMPLES (character-level)
S=http        -> ptth
S=helloworld  -> dlrowolleh
S=httpstatus  -> sutatsptth
"""
USER_PROMPT = """
Reverse the order of letters in the following word. Only output the reversed word, no other text:

httpstatus
"""


EXPECTED_OUTPUT = "sutatsptth"


def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="mistral-nemo:12b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.5},
        )
        output_text = response.message.content.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    return False


if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)
