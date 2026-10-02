/*
 * Mounts a simulation inline in a docs page.
 *
 * A simulation is a standalone page (see docs/source/_extra/demos). The build
 * puts its markup and styles in a <template> next to the host element. This
 * script moves them into a shadow root, so that the simulation CSS and the
 * docs theme CSS do not affect each other. It then gives the simulation script
 * a "document" that finds elements in the shadow root.
 */
(function () {
  "use strict";

  function syncTheme(host) {
    var html = document.documentElement;
    function apply() {
      var dark = html.getAttribute("data-theme") === "dark" || html.classList.contains("dark");
      host.setAttribute("data-theme", dark ? "dark" : "light");
    }
    apply();
    new MutationObserver(apply).observe(html, {
      attributes: true,
      attributeFilter: ["class", "data-theme"],
    });
  }

  function scopedDocument(host, root, body) {
    var overrides = {
      getElementById: function (id) { return root.getElementById(id); },
      querySelector: function (s) { return root.querySelector(s); },
      querySelectorAll: function (s) { return root.querySelectorAll(s); },
    };
    return new Proxy(document, {
      get: function (target, prop) {
        if (prop in overrides) return overrides[prop];
        if (prop === "documentElement") return host;
        if (prop === "body") return body;
        if (prop === "activeElement") return root.activeElement || document.activeElement;
        var value = Reflect.get(target, prop, target);
        return typeof value === "function" ? value.bind(target) : value;
      },
    });
  }

  window.mountSimulation = function (id, run) {
    var host = document.getElementById(id);
    var template = host.querySelector("template");
    var root = host.attachShadow({ mode: "open" });
    root.appendChild(template.content.cloneNode(true));
    template.remove();
    syncTheme(host);
    var body = root.querySelector(".sim-body");
    run(scopedDocument(host, root, body));
  };
})();
