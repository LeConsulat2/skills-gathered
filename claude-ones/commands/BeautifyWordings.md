Please update the AI note-generation prompt so the generated clinical note sounds like it was written by the practitioner, not like an outside observer describing the practitioner.

Current issue:

- The notes are clinically good, but the voice is slightly wrong.
- It says things like “The counsellor utilised…” or “The counsellor encouraged…”
- It also keeps saying “the client” repeatedly, even when `client_name` is already available.
- This makes the note feel less natural and less like the counsellor/practitioner authored it.

Desired behaviour:

- Use a practitioner-authored clinical note voice.
- Avoid first person “I”.
- Avoid third-party wording like “the counsellor provided” / “the practitioner explored”.
- Prefer clinical note phrasing like:
  - “Provided psychoeducation…”
  - “Explored safety planning…”
  - “Supported Jen to…”
  - “Reviewed coping strategies…”
  - “Discussed next steps…”
- If `client_name` is provided, use the client/student’s first name naturally in narrative sections, especially at the first reference in a section.
- Do not overuse the full legal name in the body.
- After the first name is used, use pronouns or “the student/client” where clearer.
- Avoid repeatedly starting sentences with “The client…”

Suggested implementation:

Add a helper near `_build_beautify_messages`:

```python
def _client_reference_instruction(client_name: Optional[str]) -> str:
    if client_name and client_name.strip():
        first_name = client_name.strip().split()[0]
        return (
            f'- **Client/student wording**: Use "{first_name}" naturally in narrative sections, '
            'especially at the first reference in a section. After that, use pronouns, '
            '"the student", or "the client" only where clearer. Avoid repeatedly starting '
            'sentences with "the client". Do not use the full legal name in the note body '
            'unless the template field specifically asks for it.\n'
        )

    return (
        '- **Client/student wording**: Use "the client" or "the student" naturally, but avoid '
        'repeating it at the start of every sentence.\n'
    )
```

Then inside `_build_beautify_messages`, after `counsellor_instruction`, add:

```python
participant_instruction = _client_reference_instruction(client_name)

practitioner_voice_instruction = (
    "- **Author voice**: Write as a practitioner-authored clinical note, not as an external observer's report.\n"
    "- Avoid phrases like \"the counsellor utilised\", \"the counsellor provided\", "
    "\"the counsellor encouraged\", or \"the practitioner explored\".\n"
    "- Prefer concise clinical note phrasing such as: \"Provided psychoeducation...\", "
    "\"Explored...\", \"Supported...\", \"Reviewed...\", \"Discussed...\", "
    "\"Safety plan developed...\".\n"
    "- Do not use first person \"I\" unless the template explicitly asks for a personal reflection.\n"
)
```

Then change `no_header_rule`.

Current:

```python
no_header_rule = (
    "- Do NOT write a document title, 'Session Notes' heading, or metadata block at the start. "
    "Start immediately with the first section heading.\n"
    "- Do NOT repeat the counsellor name, date, client name, or session number anywhere except inside their designated section (if one exists).\n"
)
```

Replace with:

```python
no_header_rule = (
    "- Do NOT write a document title, 'Session Notes' heading, or metadata block at the start. "
    "Start immediately with the first section heading.\n"
    "- Do NOT repeat the counsellor name, date, full client name, or session number as a metadata block in the note body.\n"
    "- If a client/student name is provided, you may use their first/preferred name naturally in narrative clinical sections.\n"
)
```

Then include the new instructions in both the free-form and structured prompt.

For the free-form `system` prompt, add these two lines inside `"GUIDELINES:\n"` after `f"{no_header_rule}"`:

```python
f"{participant_instruction}"
f"{practitioner_voice_instruction}"
```

So this part becomes:

```python
"GUIDELINES:\n"
f"{no_header_rule}"
f"{participant_instruction}"
f"{practitioner_voice_instruction}"
"- Do not impose a fixed template — let the content guide the structure.\n"
```

For the structured `system` prompt, add the same two lines after `f"{no_header_rule}"`:

```python
"IMPORTANT GUIDELINES:\n"
f"{no_header_rule}"
f"{participant_instruction}"
f"{practitioner_voice_instruction}"
"- Write clinical, professional, and objective content under each heading.\n"
```

Also change the fallback follow-up wording.

Current:

```python
"- **Follow-up**: Summarise agreed follow-up actions. If none, write \"Counsellor to follow up as needed.\"\n"
```

Replace with:

```python
"- **Follow-up**: Summarise agreed follow-up actions. If none, write \"Follow up as clinically indicated.\"\n"
```

Also apply the same idea to `_build_template_mapping_messages`, because organisation-specific templates may have narrative fields too.

Inside `_build_template_mapping_messages`, after `context_block`, add:

```python
participant_instruction = _client_reference_instruction(client_name)

practitioner_voice_instruction = (
    "- Write narrative clinical fields as if authored by the practitioner, not as an external observer's report.\n"
    "- Avoid phrases like \"the counsellor utilised\", \"the counsellor provided\", or \"the practitioner encouraged\".\n"
    "- Prefer concise clinical note phrasing such as \"Provided...\", \"Explored...\", \"Supported...\", \"Reviewed...\", or \"Discussed...\".\n"
    "- Do not use first person \"I\" unless the template field explicitly asks for personal reflection.\n"
)
```

Then add this into the `system` prompt rules:

```python
f"{participant_instruction}"
f"{practitioner_voice_instruction}"
```

For example, in the `_build_template_mapping_messages` system prompt, after:

```python
"- Use objective, professional, clinically appropriate language.\n"
```

add:

```python
f"{participant_instruction}"
f"{practitioner_voice_instruction}"
```

Expected example output style:

Instead of:

“The counsellor utilised psychoeducation to validate the client's reactions. The client was encouraged to develop a simple affirmation.”

Prefer:

“Provided psychoeducation to validate Jen’s emotional and physical stress responses as understandable responses to ongoing bullying. Explored a simple personal affirmation to support Jen in challenging self-doubt and recognising the seriousness of the situation.”

The key goal is:

- use the client/student first name naturally when available;
- reduce repetitive “the client” wording;
- remove “the counsellor did X” observer-style phrasing;
- keep the note objective, professional, and clinically appropriate.
