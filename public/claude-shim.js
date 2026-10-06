/* Compatibility layer: the prototype was written against the claude.ai
   artifact runtime (window.claude.use("db") / ("downloads")). This provides
   the same two calls on top of the real backend, so that code runs unchanged:

     db:        collection(name).onSnapshot(cb) / .get(), doc("col/id").get/set/update/delete
     downloads: save({filename, data})

   Access rules are enforced by the server (src/lib/rules.ts), not here. */
(function () {
  "use strict";
  if (window.claude && window.claude.use) return;
  // Public share viewer: no account, so no database or downloads - the page
  // must never try to reach the signed-in APIs (they would bounce to /login).
  if (window.__HTL_SHARE_TOKEN__) {
    window.claude = { use: function () { return Promise.resolve(null); } };
    return;
  }

  var POLL_MS = 5000;

  function request(method, url, body, etag) {
    var headers = {};
    if (body !== undefined) headers["Content-Type"] = "application/json";
    if (etag) headers["If-None-Match"] = etag;
    return fetch(url, {
      method: method,
      credentials: "same-origin",
      headers: headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    }).then(function (r) {
      if (r.status === 401) {
        window.location.href = "/login";
        return Promise.reject(Object.assign(new Error("Not signed in"), { code: "unauthenticated" }));
      }
      return r;
    });
  }

  function fail(r) {
    return r.json().catch(function () { return {}; }).then(function (j) {
      var code = r.status === 403 ? "permission-denied" : r.status === 404 ? "not-found" : "error";
      return Promise.reject(Object.assign(new Error(j.error || "Request failed (" + r.status + ")"), { code: code, status: r.status }));
    });
  }

  var watchers = {}; // collection -> { etag, subs: [{cb, err}], timer, busy }

  function snapshotOf(list) {
    var docs = list.map(function (d) {
      return { id: d.id, data: function () { return d.data; }, exists: true };
    });
    return { docs: docs, size: docs.length, empty: docs.length === 0, forEach: function (f) { docs.forEach(f); } };
  }

  function refresh(col) {
    var w = watchers[col];
    if (!w) return Promise.resolve();
    if (w.busy) { w.again = true; return Promise.resolve(); }
    w.busy = true;
    return request("GET", "/api/db/" + encodeURIComponent(col), undefined, w.etag)
      .then(function (r) {
        if (r.status === 304) return;
        if (!r.ok) return fail(r);
        w.etag = r.headers.get("ETag");
        return r.json().then(function (j) {
          var snap = snapshotOf(j.docs);
          w.subs.slice().forEach(function (s) { try { s.cb(snap); } catch (e) { console.error(e); } });
        });
      })
      .catch(function (e) {
        w.subs.slice().forEach(function (s) { if (s.err) try { s.err(e); } catch (x) {} });
      })
      .then(function () { w.busy = false; if (w.again) { w.again = false; refresh(col); } });
  }

  // after a write: refresh soon (debounced, and never awaited, so a burst of
  // writes - e.g. loading the whole register - isn't slowed by redrawing)
  var pending = {};
  function scheduleRefresh(col) {
    clearTimeout(pending[col]);
    pending[col] = setTimeout(function () { refresh(col); }, 200);
  }

  function watch(col, cb, err) {
    var w = (watchers[col] = watchers[col] || { etag: null, subs: [], timer: null, busy: false });
    var sub = { cb: cb, err: err };
    w.subs.push(sub);
    w.etag = null; // new subscriber: force a full first delivery
    refresh(col);
    if (!w.timer) {
      w.timer = setInterval(function () { if (!document.hidden) refresh(col); }, POLL_MS);
    }
    return function () {
      w.subs = w.subs.filter(function (s) { return s !== sub; });
      if (!w.subs.length) { clearInterval(w.timer); w.timer = null; }
    };
  }

  function splitPath(p) {
    var i = String(p).indexOf("/");
    return [p.slice(0, i), p.slice(i + 1)];
  }
  var url = function (col, id) { return "/api/db/" + encodeURIComponent(col) + "/" + encodeURIComponent(id); };

  function docRef(path) {
    var parts = splitPath(path), col = parts[0], id = parts[1];
    var ref = {
      id: id,
      get: function () {
        return request("GET", url(col, id)).then(function (r) {
          if (r.status === 404) return { id: id, exists: false, data: function () { return undefined; } };
          if (!r.ok) return fail(r);
          return r.json().then(function (j) { return { id: id, exists: true, data: function () { return j.data; } }; });
        });
      },
      set: function (data) {
        return request("PUT", url(col, id), data).then(function (r) {
          if (!r.ok) return fail(r);
          scheduleRefresh(col);
        });
      },
      update: function (patch) {
        return ref.get().then(function (cur) {
          return ref.set(Object.assign({}, cur.exists ? cur.data() : {}, patch));
        });
      },
      delete: function () {
        return request("DELETE", url(col, id)).then(function (r) {
          if (!r.ok) return fail(r);
          scheduleRefresh(col);
        });
      },
    };
    return ref;
  }

  var db = {
    doc: docRef,
    collection: function (col) {
      return {
        onSnapshot: function (cb, err) { return watch(col, cb, err); },
        get: function () {
          return request("GET", "/api/db/" + encodeURIComponent(col)).then(function (r) {
            if (!r.ok) return fail(r);
            return r.json().then(function (j) { return snapshotOf(j.docs); });
          });
        },
        doc: function (id) { return docRef(col + "/" + id); },
      };
    },
  };

  var downloads = {
    save: function (opts) {
      var blob = opts.data instanceof Blob ? opts.data : new Blob([opts.data], { type: "text/plain" });
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = opts.filename || "download";
      document.body.appendChild(a);
      a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
      return Promise.resolve();
    },
  };

  window.claude = {
    use: function (name) {
      if (name === "db") return Promise.resolve(db);
      if (name === "downloads") return Promise.resolve(downloads);
      return Promise.resolve(null);
    },
  };
})();
