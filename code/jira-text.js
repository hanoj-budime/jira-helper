let texts = [];

$('.nav.ghx-summary').each(function() {
    var value = $(this).text();
    console.log((value).trim());
    texts.push((value).trim());
});

console.log("texts :>>", texts.join(","));
console.log(stories.join(", "));
