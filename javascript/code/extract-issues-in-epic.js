(() => {
    const data = {};

    $("tr.issuerow").each(function () {
        const code = $(this).find("td.nav.ghx-minimal").text().trim();
        if (!code) {
            return;
        }

        data[code] = {
            summary: $(this).find("td.nav.ghx-summary").text().trim(),
        };
    });

    console.table(data);
    console.log(Object.keys(data).join(", "));
})();
