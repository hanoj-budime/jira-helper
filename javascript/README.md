# JavaScript Jira Snippets

Browser-console snippets to extract issue data from Jira pages.

## Usage

1. Open the Jira page that matches the script.
2. Open browser developer tools console.
3. Paste script content from `code/`.
4. Press Enter and inspect the `console.table(...)` output.

## Scripts

- `code/extract-sprint-active-data.js`: active sprint issues with points.
- `code/extract-sprint-planned-data.js`: planned sprint issues with points.
- `code/extract-epics-data.js`: board column issues and committed flag.
- `code/extract-issues-in-epic.js`: issues listed in an epic/detail table.
- `code/extract-issues-in-search.js`: issues from Jira search results table.
- `code/jira-ids.js`: quickly collect issue keys from current table/page.
- `code/jira-text.js`: quickly collect issue summaries from current table/page.

## Compatibility Notes

- Selectors are tuned for Jira Cloud classic board/table DOM.
- If your Jira theme/layout differs, update selectors in the snippet.
- Scripts assume jQuery is available on the Jira page.