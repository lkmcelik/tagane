// Tagane website: closes the language menu on Escape or a click outside it.
// The menu is a <details> element, so it works without this script too.
(function () {
  var menus = document.querySelectorAll("details.lang-menu");
  if (!menus.length) return;
  document.addEventListener("click", function (event) {
    menus.forEach(function (menu) {
      if (menu.open && !menu.contains(event.target)) menu.open = false;
    });
  });
  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") return;
    menus.forEach(function (menu) {
      if (!menu.open) return;
      menu.open = false;
      var summary = menu.querySelector("summary");
      if (summary) summary.focus();
    });
  });
})();
