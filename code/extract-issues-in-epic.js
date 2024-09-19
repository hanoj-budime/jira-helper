let summary_data = [];
$("tr.issuerow").each(function() {
    // ? Extract the issue ID
    let code = $(this).find("td.nav.ghx-minimal").text();
    code = code.trim();
    // ? Extract the summary text of the issue
    let summary = $(this).find("td.nav.ghx-summary").text();
    summary = summary.trim();
    // ? Log
    console.log(`${code} ${summary}`);
    summary_data.push({code, summary});
});
console.table(summary_data);
