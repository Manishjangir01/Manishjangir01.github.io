/* Progressive enhancement only. The page is complete without this file.
   1) theme toggle  2) repository details from the GitHub API */
(function () {
  "use strict";

  var USER = "Manishjangir01";
  var root = document.documentElement;

  /* ---------- theme ---------- */
  var button = document.getElementById("theme-toggle");

  function currentTheme() {
    var set = root.getAttribute("data-theme");
    if (set === "light" || set === "dark") return set;
    return "dark"; // default theme
  }

  function paintButton() {
    if (!button) return;
    var next = currentTheme() === "dark" ? "light" : "dark";
    button.textContent = next === "dark" ? "Dark theme" : "Light theme";
    button.setAttribute("aria-label", "Switch to " + next + " theme");
  }

  if (button) {
    paintButton();
    button.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) { /* storage can be blocked */ }
      paintButton();
    });
  }

  /* ---------- repositories ---------- */
  var list = document.getElementById("repo-list");
  var status = document.getElementById("repo-status");
  if (!list || !window.fetch) return;

  var CACHE_KEY = "repos-v1";
  var CACHE_MS = 30 * 60 * 1000;

  function readCache() {
    try {
      var raw = sessionStorage.getItem(CACHE_KEY);
      if (!raw) return null;
      var obj = JSON.parse(raw);
      return Date.now() - obj.at < CACHE_MS ? obj.data : null;
    } catch (e) { return null; }
  }

  function writeCache(data) {
    try { sessionStorage.setItem(CACHE_KEY, JSON.stringify({ at: Date.now(), data: data })); } catch (e) { /* ignore */ }
  }

  function getRepos() {
    var cached = readCache();
    if (cached) return Promise.resolve(cached);
    var url = "https://api.github.com/users/" + USER + "/repos?per_page=100&sort=updated";
    return fetch(url, { headers: { Accept: "application/vnd.github+json" } }).then(function (res) {
      if (!res.ok) throw new Error("GitHub API answered " + res.status);
      return res.json();
    }).then(function (data) {
      writeCache(data);
      return data;
    });
  }

  function monthYear(iso) {
    var d = new Date(iso);
    if (isNaN(d)) return "";
    return new Intl.DateTimeFormat("en", { month: "short", year: "numeric" }).format(d);
  }

  function describe(repo) {
    var parts = [];
    if (repo.language) parts.push(repo.language);
    if (repo.stargazers_count > 0) parts.push(repo.stargazers_count + (repo.stargazers_count === 1 ? " star" : " stars"));
    if (repo.pushed_at) parts.push("Updated " + monthYear(repo.pushed_at));
    return parts.join(", ");
  }

  function fill(li, repo) {
    var meta = li.querySelector(".meta");
    if (meta) meta.textContent = describe(repo);
    var desc = li.querySelector(".desc");
    if (desc && repo.description) desc.textContent = repo.description;
  }

  function addNew(repo) {
    var li = document.createElement("li");
    li.setAttribute("data-repo", repo.name);
    var a = document.createElement("a");
    a.href = repo.html_url;
    a.textContent = repo.name;
    var p = document.createElement("p");
    p.className = "desc";
    p.textContent = repo.description || "";
    var m = document.createElement("p");
    m.className = "meta";
    li.appendChild(a);
    li.appendChild(p);
    li.appendChild(m);
    list.appendChild(li);
    fill(li, repo);
  }

  getRepos().then(function (repos) {
    var known = {};
    Array.prototype.forEach.call(list.querySelectorAll("li[data-repo]"), function (li) {
      known[li.getAttribute("data-repo")] = li;
    });
    repos.forEach(function (repo) {
      if (repo.fork || repo.archived) return;
      if (known[repo.name]) fill(known[repo.name], repo);
      else addNew(repo);
    });
    if (status) status.textContent = list.children.length + " repositories. Details from the GitHub API.";
  }).catch(function () {
    if (status) status.textContent = "Live details are not available right now. This list is the saved copy.";
  });
})();
