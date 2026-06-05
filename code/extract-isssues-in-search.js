/**
 * Extract issues in search results
 * This script is designed to extract issue data from the search results page in Jira. It collects the issue ID and summary for each issue listed in the search results and stores them in an object for easy access and display.
 */

(() => {
  // * Initialize an empty object to store the data
  let data = {};

  $("#issuetable tbody tr").each(function () {
    // ? Extract the issue ID
    let code = $(this).find("td.issuekey").text();
    code = code.trim();
    console.log(`code :>> ${code}`);
    // ? Extract the summary text of the issue
    let summary = $(this).find("td.summary").text();
    summary = summary.trim();
    console.log(`summary :>> ${summary}`);
    // * Store the extracted data
    data[code] = { summary: summary };
  });

  // * Output the collected issue codes and summary data
  console.table(data);
})();
