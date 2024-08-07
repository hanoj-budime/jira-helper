// * Initialize an empty object to store the data
let data = {};

// * Iterate over each issue in the active sprint
$(".ghx-sprint-active .ghx-row").each(function () {
  // Extract the issue ID
  let id = $(this).find(".ghx-key").text();
  // Extract the summary text of the issue
  let text = $(this).find(".ghx-inner").text();
  // Extract the issue type (e.g., Bug, Story)
  let type = $(this).find(".ghx-type").attr("title");
  // Extract the priority of the issue
  let priority = $(this).find(".ghx-priority").attr("title");
  // Extract the story points of the issue
  let points = $(this).find(".ghx-statistic-badge").text();
  // Clean up the ID by trimming any extra whitespace
  let code = id.trim();

  // Store the extracted data in the 'data' object
  data[code] = {
    // Store the cleaned-up ID
    // code: id.trim(),
    // Store the cleaned-up summary text
    summary: text.trim(),
    // Store the cleaned-up issue type
    type: type.trim(),
    // Store the cleaned-up priority
    priority: priority.trim(),
    // Store the cleaned-up and converted story points
    points: Number(points.trim()),
  };
});

// Output the data in a table format in the console
console.table(data);
