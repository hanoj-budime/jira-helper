(() => {
    const issueKeys = [];

    $(".nav.ghx-minimal a").each(function () {
        const value = $(this).text().trim();
        if (value) {
            issueKeys.push(value);
        }
    });

    console.log(issueKeys.join(", "));
})();
