# Behaviour ledger for the synthetic insights workflow

This is a compact example of turning product empathy into testable behaviour.

| Situation | Observable behaviour | Product obligation | Falsifiable check |
|---|---|---|---|
| An analyst sees two totals for the same period | They open both definitions and export dates before trusting either | Show scope, definition, source, and freshness beside every total | A new analyst can name the difference without asking the builder |
| A source row has an unknown status | The analyst asks the definition owner instead of guessing a mapping | Put the row class in an exception queue; do not silently coerce it | Unknown values never enter a known status count |
| A senior needs a figure in a meeting | They need a usable answer quickly but also need to know whether it is provisional | Lead with the number, then caveat and verification status | The figure is understandable in 30 seconds and its limitations in 60 |
| A job runs longer than the page visit | The user navigates elsewhere and later returns | Persist status and result references outside the browser process | Refreshing or closing the page does not lose the job |
| A model drafts an interpretation | The analyst edits, rejects, or asks for another check | Preserve model draft and human-authored final separately | The final artifact identifies its reviewer and review state |
| Publication would make a draft visible to others | The user expects to preview exactly what will be published | Pause at a previewable approval boundary | No publication occurs from model intent alone |

