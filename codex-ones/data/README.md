# Synthetic data only

[applications.csv](../src/codex_ones/sample_data/applications.csv) is invented for this repository. Its IDs, dates, faculties, statuses, and counts do not describe University of Auckland or any person. It lives inside the package so installed wheels and the MCP service use the same single fixture.

The file intentionally contains:

- one duplicate application ID in `2026-S1`;
- one unknown status in each period;
- mixed freshness in `2026-S2`;
- one decision date before its submission date in `2026-S2`.

Those are not mistakes to clean away. They are eval fixtures for exception handling.

Never replace that file with an export from work. Create an approved connector outside this learning repository and retain the same aggregate evidence contract.
