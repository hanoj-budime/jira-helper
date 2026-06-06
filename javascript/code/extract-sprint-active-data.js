(() => {
  const data = {};

  $(".ghx-sprint-active .ghx-row").each(function () {
    const code = $(this).find(".ghx-key").text().trim();
    if (!code) {
      return;
    }

    const pointsRaw = $(this).find(".ghx-statistic-badge").text().trim();
    data[code] = {
      summary: $(this).find(".ghx-inner").text().trim(),
      type: ($(this).find(".ghx-type").attr("title") || "").trim(),
      priority: ($(this).find(".ghx-priority").attr("title") || "").trim(),
      points: pointsRaw ? Number(pointsRaw) : null,
    };
  });

  console.table(data);
})();
