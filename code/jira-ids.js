let stories = [];

// From a Epic
$('.nav.ghx-minimal a').each(function() {
    var value = $(this).text();
    console.log(value);
    stories.push(value);
});

console.log("stories :>>", stories.join(","));
console.log(stories.join(", ")); // ? XXX-XXX, XXX-XXX,
