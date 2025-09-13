let codes = [];
let summary_data = [];
$("tr.issuerow").each(function() {
    // ? Extract the issue ID
    let code = $(this).find("td.nav.ghx-minimal").text();
    code = code.trim();
    // ? Extract the summary text of the issue
    let summary = $(this).find("td.nav.ghx-summary").text();
    summary = summary.trim();
    // ?
    codes.push(code);
    console.log(`${code} ${summary}`);
    // * Store the extracted data in the 'data' object
    summary_data[code] = {
        summary: summary,
    };
});
console.log(codes.join(", "))
console.table(summary_data, ["code", "summary"]);
