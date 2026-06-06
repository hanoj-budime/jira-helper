(() => {
  const data = {};

  $(".ghx-column .ghx-issue").each(function () {
    const code = $(this).find(".ghx-key").text().trim();
    if (!code) {
      return;
    }

    const labelsText = $(this).find(".ghx-extra-field").text().trim();
    data[code] = {
      summary: $(this).find(".ghx-inner").text().trim(),
      type: ($(this).find(".ghx-type").attr("title") || "").trim(),
      priority: ($(this).find(".ghx-priority").attr("title") || "").trim(),
      committed: labelsText.includes("uncommitted_") ? "No" : "Yes",
    };
  });

  console.table(data);
})();
