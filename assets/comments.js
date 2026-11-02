/* Blog comments: loads approved comments and sends new ones to the Apex comments service.
   The section is only on the page when the comments service is set up (source/comments-endpoint.txt). */
(function () {
  'use strict';
  var box = document.getElementById('comments');
  if (!box) return;
  var api = box.getAttribute('data-api'), post = box.getAttribute('data-post');
  var list = box.querySelector('.cm-list'), form = box.querySelector('form'), msg = box.querySelector('.cm-msg'), count = box.querySelector('.cm-count');
  var started = Date.now();
  function el(t, c, x) { var e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; }
  function when(iso) { try { return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }); } catch (e) { return ''; } }
  function initials(n) { return (n || '?').trim().split(/\s+/).slice(0, 2).map(function (w) { return w.charAt(0).toUpperCase(); }).join(''); }
  function one(c) {
    var d = el('div', 'cm' + (c.owner ? ' cm-own' : ''));
    var av = el('span', 'cm-av', c.owner ? 'A' : initials(c.name));
    var main = el('div', 'cm-main');
    var head = el('div', 'cm-head');
    head.appendChild(el('b', null, c.name));
    if (c.owner) head.appendChild(el('span', 'cm-badge', 'Apex team'));
    head.appendChild(el('span', 'cm-date', when(c.created_at)));
    main.appendChild(head);
    main.appendChild(el('p', 'cm-body', c.body));
    d.appendChild(av); d.appendChild(main);
    return d;
  }
  function render(cs) {
    list.innerHTML = '';
    var top = cs.filter(function (c) { return !c.parent_id; });
    if (count) count.textContent = top.length ? '(' + top.length + ')' : '';
    if (!top.length) { list.appendChild(el('p', 'cm-empty', 'No comments yet. Ask a question or share your experience.')); return; }
    top.forEach(function (c) {
      var wrap = el('div', 'cm-thread');
      wrap.appendChild(one(c));
      cs.filter(function (r) { return r.parent_id === c.id; }).forEach(function (r) { var x = one(r); x.classList.add('cm-reply'); wrap.appendChild(x); });
      list.appendChild(wrap);
    });
  }
  function load() {
    fetch(api + '/api/comments?post=' + encodeURIComponent(post)).then(function (r) { return r.json(); })
      .then(function (j) { render(j.comments || []); })
      .catch(function () { list.innerHTML = ''; list.appendChild(el('p', 'cm-empty', 'Comments could not be loaded right now.')); });
  }
  try { var saved = localStorage.getItem('apexCommentName'); if (saved) form.elements.name.value = saved; } catch (e) {}
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var btn = form.querySelector('button[type=submit]');
    var name = form.elements.name.value.trim(), body = form.elements.body.value.trim();
    msg.className = 'cm-msg'; msg.textContent = '';
    if (name.length < 2) { msg.className = 'cm-msg err'; msg.textContent = 'Please enter your name.'; return; }
    if (body.length < 3) { msg.className = 'cm-msg err'; msg.textContent = 'Please write a comment.'; return; }
    btn.disabled = true; btn.textContent = 'Sending…';
    fetch(api + '/api/comments', { method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ post: post, name: name, body: body, website: form.elements.website.value, elapsed: Date.now() - started }) })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error || 'Something went wrong.'); return j; }); })
      .then(function () {
        try { localStorage.setItem('apexCommentName', name); } catch (e2) {}
        form.elements.body.value = '';
        msg.className = 'cm-msg ok'; msg.textContent = 'Thank you! Your comment will appear here after the Apex team approves it.';
      })
      .catch(function (err) { msg.className = 'cm-msg err'; msg.textContent = err.message; })
      .then(function () { btn.disabled = false; btn.textContent = 'Post comment'; });
  });
  load();
})();
