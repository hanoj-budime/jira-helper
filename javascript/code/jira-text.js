(() => {
    const summaries = [];

    $(".nav.ghx-summary").each(function () {
        const value = $(this).text().trim();
        if (value) {
            summaries.push(value);
        }
    });

    console.log(summaries.join(", "));
})();
