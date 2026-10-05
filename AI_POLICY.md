# AI Policy

**Effective Starting from: 5 October 2026**

This is the policy for how AI-generated code is treated in this project. It applies to every commit made on or after the effective date.

## 1. Flag it in the commit message

Any commit that contains AI-generated code must include this flag in its commit message:

```
**CONTAINS AI GENERATED CODE**
```

Example:

```
add word-alignment fallback for short clips

**CONTAINS AI GENERATED CODE**
```

## 2. Provide the prompt after the code

The prompt that was used to generate the code must be included as a comment directly after the AI-generated code.

Example:

```python
def merge_short_segments(segments, min_len=0.3):
    ...

# AI PROMPT: "write a function that merges whisperx segments
# shorter than min_len seconds into the previous segment"
```

## Scope

- Commits made before 5 October 2026 are not covered by this policy.
- Code written entirely by hand needs no flag and no prompt comment.
