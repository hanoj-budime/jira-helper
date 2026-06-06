(() => {
  const data = {};

  $(".ghx-sprint-planned .ghx-row").each(function () {
    const code = $(this).find(".ghx-key").text().trim();
    if (!code) {
      return;
    }

    const summary = $(this).find(".ghx-inner").text().trim();
    const pointsRaw = $(this).find(".ghx-statistic-badge").text().trim();

    data[code] = {
      summary,
      type: ($(this).find(".ghx-type").attr("title") || "").trim(),
      priority: ($(this).find(".ghx-priority").attr("title") || "").trim(),
      points: pointsRaw ? Number(pointsRaw) : null,
    };
  });

  console.table(data);
})();
