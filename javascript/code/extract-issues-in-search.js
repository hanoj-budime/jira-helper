/**
 * Extract issues from Jira search results table.
 */
(() => {
  const data = {};

  $("#issuetable tbody tr").each(function () {
    const code = $(this).find("td.issuekey").text().trim();
    if (!code) {
      return;
    }

    data[code] = {
      summary: $(this).find("td.summary").text().trim(),
    };
  });

  console.table(data);
  console.log(Object.keys(data).join(", "));
})();
