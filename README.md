# README: Jira Helper

## Overview
Jira Helper is a JavaScript snippet designed to extract active sprint data from a Jira board. When run in the browser console, it gathers details such as the issue ID, summary, type, priority, and story points for each issue in the active sprint and outputs this data in a table format in the console.

## Prerequisites
- Access to a Jira board with an active sprint.
- Basic knowledge of how to use browser developer tools, particularly the console.

## Steps

### 1. Open Jira Board
Navigate to the Jira board that contains the active sprint data you wish to extract.

### 2. Open Developer Tools
- Right-click on the Jira page and select "Inspect" or press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac) to open the Developer Tools.
- Navigate to the "Console" tab within the Developer Tools.

### 3. Paste and Run the Script
Copy the provided JavaScript snippet and paste it into the console, then press `Enter` to execute it.

### JavaScript Snippet
[code](./code/extract-sprint-data.js)
```js
let data = {};

$(".ghx-sprint-active .ghx-row").each(function () {
  let id = $(this).find(".ghx-key").text();
  let text = $(this).find(".ghx-inner").text();
  let type = $(this).find(".ghx-type").attr("title");
  let priority = $(this).find(".ghx-priority").attr("title");
  let points = $(this).find(".ghx-statistic-badge").text();
  let code = id.trim();
  
  data[code] = {
    summary: text.trim(),
    type: type.trim(),
    priority: priority.trim(),
    points: Number(points.trim()),
  };
});

console.table(data);
```

### 4. View Extracted Data
After running the script, the console will display a table with the extracted data. Each row represents an issue from the active sprint, with columns for the issue ID, summary, type, priority, and story points.

## Example Output
``` powershell
┌─────────────┬───────────────────────────────┬──────────────┬──────────────┬────────┐
│ (index)     │ summary                       │ type         │ priority     │ points │
├─────────────┼───────────────────────────────┼──────────────┼──────────────┼────────┤
│ "ISSUE-123" │ "Fix login bug"               │ "Bug"        │ "High"       │ 3      │
│ "ISSUE-124" │ "Add new feature"             │ "Story"      │ "Medium"     │ 5      │
│ "ISSUE-125" │ "Update documentation"        │ "Task"       │ "Low"        │ 2      │
└─────────────┴───────────────────────────────┴──────────────┴──────────────┴────────┘
```

## Notes
- Ensure you are viewing the active sprint on the Jira board when running the script.
- This script uses jQuery to select and extract data from the DOM. If your Jira instance does not support jQuery, you may need to adjust the selectors and methods accordingly.
- The script assumes that the DOM structure of the Jira board matches the selectors used (`.ghx-sprint-active .ghx-row`, `.ghx-key`, `.ghx-inner`, `.ghx-type`, `.ghx-priority`, `.ghx-statistic-badge`). If your Jira instance has a different structure, you will need to update the selectors accordingly.

By following these steps, you should be able to extract and view active sprint data from your Jira board in a convenient table format using Jira Helper.