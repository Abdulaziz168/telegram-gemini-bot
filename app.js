// Telegram Mini App: Russian learning + games + profile. No backend: progress lives in
// Telegram CloudStorage (synced across devices) with a localStorage fallback.
(function () {
  'use strict';

  const tg = window.Telegram && window.Telegram.WebApp;
  if (tg) { tg.ready(); tg.expand(); }

  const app = document.getElementById('app');
  const TOPICS = window.TOPICS;
  const ALL_WORDS = Object.entries(TOPICS).flatMap(([topic, t]) =>
    t.words.map(([ru, uz, reading], i) => ({ id: topic + ':' + i, topic, ru, uz, reading })));

  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const rand = (n) => Math.floor(Math.random() * n);
  const shuffle = (arr) => { const a = arr.slice(); for (let i = a.length - 1; i > 0; i--) { const j = rand(i + 1); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const today = () => new Date().toISOString().slice(0, 10);

  // ---------- Haptics and toast ----------
  const haptic = {
    tap: () => { try { tg.HapticFeedback.impactOccurred('light'); } catch (e) {} },
    ok: () => { try { tg.HapticFeedback.notificationOccurred('success'); } catch (e) {} },
    err: () => { try { tg.HapticFeedback.notificationOccurred('error'); } catch (e) {} },
  };
  let toastTimer;
  function toast(msg) {
    const el = document.getElementById('toast');
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('show'), 1800);
  }

  // ---------- Storage ----------
  const DEFAULTS = () => ({
    updated: 0,
    points: 0,
    known: [],
    stats: {
      rps: { plays: 0, wins: 0, bestStreak: 0 },
      guess: { plays: 0, wins: 0, bestTries: 0 },
      memory: { plays: 0, bestMoves: 0 },
      test: { plays: 0, correct: 0, perfect: 0 },
    },
    streak: { count: 0, last: '' },
  });

  function merge(base, extra) {
    for (const k of Object.keys(extra || {})) {
      if (base[k] && typeof base[k] === 'object' && !Array.isArray(base[k])) merge(base[k], extra[k]);
      else base[k] = extra[k];
    }
    return base;
  }

  const Store = {
    state: DEFAULTS(),
    hasCloud: !!(tg && tg.CloudStorage && tg.isVersionAtLeast && tg.isVersionAtLeast('6.9')),
    parse(raw) { try { return raw ? JSON.parse(raw) : null; } catch (e) { return null; } },
    async load() {
      let local = null;
      try { local = this.parse(localStorage.getItem('state')); } catch (e) {}
      let cloud = null;
      if (this.hasCloud) {
        cloud = await new Promise((res) => {
          const timer = setTimeout(() => res(null), 2500);
          tg.CloudStorage.getItem('state', (err, v) => { clearTimeout(timer); res(err ? null : this.parse(v)); });
        });
      }
      const newest = [local, cloud].filter(Boolean).sort((a, b) => (b.updated || 0) - (a.updated || 0))[0];
      if (newest) this.state = merge(DEFAULTS(), newest);
      this.touchStreak();
    },
    touchStreak() {
      const s = this.state.streak;
      const t = today();
      if (s.last === t) return;
      const y = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
      s.count = s.last === y ? s.count + 1 : 1;
      s.last = t;
      this.save();
    },
    save() {
      this.state.updated = Date.now();
      const raw = JSON.stringify(this.state);
      try { localStorage.setItem('state', raw); } catch (e) {}
      clearTimeout(this.timer);
      if (this.hasCloud) this.timer = setTimeout(() => tg.CloudStorage.setItem('state', raw, () => {}), 500);
    },
  };

  const S = () => Store.state;
  function addPoints(n) {
    if (n <= 0) return;
    S().points += n;
    Store.save();
    renderChips();
  }
  const level = () => Math.floor(S().points / 50) + 1;
  const isKnown = (id) => S().known.includes(id);

  // ---------- Router ----------
  const view = { name: 'home', params: {} };
  const stack = [];
  const TABS = ['home', 'ru', 'games', 'profile'];

  function go(name, params) {
    stack.push({ name: view.name, params: view.params });
    view.name = name;
    view.params = params || {};
    render();
  }
  function back() {
    const prev = stack.pop();
    if (!prev) return;
    view.name = prev.name;
    view.params = prev.params;
    render();
  }
  function tab(name) {
    stack.length = 0;
    view.name = name;
    view.params = {};
    render();
  }

  function renderChips() {
    document.getElementById('chip-points').textContent = '⭐ ' + S().points;
    document.getElementById('chip-streak').textContent = '🔥 ' + S().streak.count;
  }

  function render() {
    const fn = VIEWS[view.name];
    app.innerHTML = fn(view.params);
    window.scrollTo(0, 0);
    const activeTab = stack.length ? (stack[0].name) : view.name;
    document.querySelectorAll('#tabbar button').forEach((b) =>
      b.classList.toggle('active', b.dataset.tab === (TABS.includes(activeTab) ? activeTab : 'home')));
    renderChips();
    if (tg && tg.BackButton) { stack.length ? tg.BackButton.show() : tg.BackButton.hide(); }
  }

  // ---------- Views ----------
  function bar(pct) { return '<div class="bar"><i style="width:' + Math.round(pct) + '%"></i></div>'; }

  function topicProgress(topic) {
    const words = TOPICS[topic].words;
    const known = words.filter((_, i) => isKnown(topic + ':' + i)).length;
    return { known, total: words.length };
  }

  const ACHIEVEMENTS = [
    { icon: '🌱', name: "Birinchi so'z", ok: () => S().known.length >= 1 },
    { icon: '📚', name: "10 ta so'z", ok: () => S().known.length >= 10 },
    { icon: '🎓', name: "30 ta so'z", ok: () => S().known.length >= 30 },
    { icon: '🏅', name: 'Mavzu tugatildi', ok: () => Object.keys(TOPICS).some((t) => topicProgress(t).known === topicProgress(t).total) },
    { icon: '🎯', name: 'Testda 10/10', ok: () => S().stats.test.perfect >= 1 },
    { icon: '🔥', name: '3 kunlik streak', ok: () => S().streak.count >= 3 },
    { icon: '🧠', name: 'Xotira: 12 yurishda', ok: () => S().stats.memory.bestMoves > 0 && S().stats.memory.bestMoves <= 12 },
    { icon: '🏆', name: '100 ball', ok: () => S().points >= 100 },
  ];

  const VIEWS = {
    home() {
      const total = ALL_WORDS.length;
      const known = S().known.length;
      const lvlPct = (S().points % 50) * 2;
      return `
        <h1>Xush kelibsiz! 👋</h1>
        <div class="card">
          <div class="row"><div class="grow"><div class="title">Daraja ${level()}</div>
            <div class="hint">Keyingi darajagacha ${50 - (S().points % 50)} ball</div></div><div class="big-emoji">⭐</div></div>
          ${bar(lvlPct)}
        </div>
        <div class="card tap" data-act="tab" data-tab="ru">
          <div class="row"><div class="big-emoji">📖</div><div class="grow"><div class="title">Rus tilini o'rganish</div>
            <div class="hint">${known}/${total} so'z yodlandi</div></div></div>
          ${bar(known / total * 100)}
        </div>
        <div class="card tap" data-act="open-quiz">
          <div class="row"><div class="big-emoji">🧠</div><div class="grow"><div class="title">Tezkor test</div>
            <div class="hint">10 ta savol, har to'g'ri javob +1 ball</div></div></div>
        </div>
        <div class="card tap" data-act="tab" data-tab="games">
          <div class="row"><div class="big-emoji">🎮</div><div class="grow"><div class="title">O'yinlar</div>
            <div class="hint">Tosh-qaychi-qog'oz, sonni top, xotira</div></div></div>
        </div>`;
    },

    ru() {
      const rows = Object.entries(TOPICS).map(([key, t]) => {
        const p = topicProgress(key);
        return `<div class="card tap" data-act="cards" data-topic="${key}">
          <div class="row"><div class="grow"><div class="title">${esc(t.title)}</div>
          <div class="hint">${p.known}/${p.total} yodlandi</div></div><div class="hint">›</div></div>
          ${bar(p.known / p.total * 100)}</div>`;
      }).join('');
      return `<h1>📖 Rus tili</h1>
        <button class="btn" data-act="open-quiz">🧠 Aralash test (10 savol)</button>
        <h2>So'z kartochkalari</h2>${rows}`;
    },

    cards(p) {
      const t = TOPICS[p.topic];
      if (p.pos >= p.queue.length) {
        const pr = topicProgress(p.topic);
        return `<h1>${esc(t.title)}</h1><div class="card center">
          <div class="big-emoji">🎉</div><p class="title">Barakalla!</p>
          <p class="hint">Yodlangan: ${pr.known}/${pr.total}</p></div>
          <button class="btn" data-act="cards" data-topic="${p.topic}">🔄 Qayta boshlash</button>
          <div class="btn-row"><button class="btn secondary" data-act="tab" data-tab="ru">Mavzular</button></div>`;
      }
      const w = t.words[p.queue[p.pos]];
      const [ru, uz, reading] = w;
      return `<h1>${esc(t.title)}</h1>
        <div class="hint center">${p.pos + 1} / ${p.queue.length}</div>
        <div class="flash" data-act="flip">
          <div class="ru">${esc(ru)}</div>
          <div class="reading">🔊 ${esc(reading)}</div>
          ${p.flipped ? `<div class="uz">${esc(uz)}</div>` : '<div class="tip">Tarjimasini ko\'rish uchun bosing</div>'}
        </div>
        <div class="center"><button class="speak" data-act="speak" data-text="${esc(ru)}">🔊</button></div>
        ${p.flipped ? `<div class="btn-row">
          <button class="btn bad" data-act="again">🔁 Takrorlayman</button>
          <button class="btn good" data-act="know">✅ Bildim</button></div>` : ''}`;
    },

    quiz(p) {
      if (p.pos >= p.qs.length) {
        return `<h1>🧠 Test tugadi</h1><div class="card center">
          <div class="big-emoji">${p.score >= 8 ? '🏆' : p.score >= 5 ? '👍' : '💪'}</div>
          <p class="title">${p.score} / ${p.qs.length} to'g'ri</p>
          <p class="hint">+${p.score} ball${p.score === p.qs.length ? ' · Mukammal!' : ''}</p></div>
          <button class="btn" data-act="open-quiz-new">🔄 Yana</button>
          <div class="btn-row"><button class="btn secondary" data-act="tab" data-tab="ru">Rus tili</button></div>`;
      }
      const q = p.qs[p.pos];
      const opts = q.options.map((o, i) => {
        let cls = '';
        if (p.picked !== null) cls = i === q.answer ? 'good' : (i === p.picked ? 'bad' : '');
        return `<button class="opt ${cls}" data-act="answer" data-i="${i}" ${p.picked !== null ? 'disabled' : ''}>${esc(o)}</button>`;
      }).join('');
      return `<div class="hint center">Savol ${p.pos + 1} / ${p.qs.length} · ${p.score} ball</div>
        ${bar(p.pos / p.qs.length * 100)}
        <div class="question">${q.toUz
          ? `<b>${esc(q.word.ru)}</b> <span class="hint">(${esc(q.word.reading)})</span> — o'zbekchasi?`
          : `<b>${esc(q.word.uz)}</b> — ruscha qanday aytiladi?`}</div>
        ${opts}
        ${p.picked !== null ? `<button class="btn" data-act="next-q">${p.pos + 1 >= p.qs.length ? '🏁 Natija' : '➡️ Keyingi'}</button>` : ''}`;
    },

    games() {
      const st = S().stats;
      return `<h1>🎮 O'yinlar</h1>
        <div class="card tap" data-act="game" data-game="rps"><div class="row"><div class="big-emoji">✂️</div>
          <div class="grow"><div class="title">Tosh-qaychi-qog'oz</div>
          <div class="hint">${st.rps.wins} g'alaba / ${st.rps.plays} o'yin</div></div></div></div>
        <div class="card tap" data-act="game" data-game="guess"><div class="row"><div class="big-emoji">🔢</div>
          <div class="grow"><div class="title">Sonni top</div>
          <div class="hint">${st.guess.wins} g'alaba${st.guess.bestTries ? ' · eng yaxshi: ' + st.guess.bestTries + ' urinish' : ''}</div></div></div></div>
        <div class="card tap" data-act="game" data-game="memory"><div class="row"><div class="big-emoji">🧠</div>
          <div class="grow"><div class="title">Xotira</div>
          <div class="hint">${st.memory.bestMoves ? 'Rekord: ' + st.memory.bestMoves + ' yurish' : 'Juft kartalarni toping'}</div></div></div></div>`;
    },

    rps(p) {
      const E = { rock: '🪨', paper: '📄', scissors: '✂️' };
      return `<h1>✂️ Tosh-qaychi-qog'oz</h1>
        ${p.res ? `<div class="versus"><div>${E[p.res.me]}<small>Siz</small></div><div>${E[p.res.bot]}<small>Bot</small></div></div>
          <div class="result">${p.res.text}</div>` : '<p class="hint center">Tanlang 👇</p>'}
        <div class="rps">
          <button data-act="rps" data-c="rock">🪨</button>
          <button data-act="rps" data-c="paper">📄</button>
          <button data-act="rps" data-c="scissors">✂️</button></div>
        <p class="hint center">Ketma-ket g'alaba: ${p.streak || 0} · Rekord: ${S().stats.rps.bestStreak}</p>`;
    },

    guess(p) {
      const left = 7 - p.tries;
      return `<h1>🔢 Sonni top</h1>
        <div class="card center"><p>1 dan 100 gacha son o'yladim.</p>
          <p class="hint">Qolgan urinishlar: <b>${left}</b></p>
          ${p.msg ? `<div class="result">${p.msg}</div>` : ''}</div>
        ${p.over
          ? `<button class="btn" data-act="game" data-game="guess-new">🔄 Yana o'ynash</button>`
          : `<input class="num-input" id="guess-input" type="number" inputmode="numeric" min="1" max="100" placeholder="?">
             <div class="btn-row"><button class="btn" data-act="guess">Tekshirish</button></div>`}`;
    },

    memory(p) {
      const cards = p.cards.map((c, i) =>
        `<button class="${c.matched ? 'done' : c.open ? 'open' : ''}" data-act="mem" data-i="${i}">${c.e}</button>`).join('');
      const done = p.cards.every((c) => c.matched);
      return `<h1>🧠 Xotira</h1>
        <p class="hint center">Yurishlar: <b>${p.moves}</b>${S().stats.memory.bestMoves ? ' · Rekord: ' + S().stats.memory.bestMoves : ''}</p>
        <div class="mem">${cards}</div>
        ${done ? `<div class="result">🎉 ${p.moves} yurishda topdingiz! +${p.reward} ball</div>
          <button class="btn" data-act="game" data-game="memory-new">🔄 Yana</button>` : ''}`;
    },

    profile() {
      const st = S().stats;
      const unlocked = ACHIEVEMENTS.filter((a) => a.ok()).length;
      const name = tg && tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user.first_name : 'Mehmon';
      return `<h1>👤 ${esc(name)}</h1>
        <div class="card"><div class="row"><div class="grow"><div class="title">Daraja ${level()}</div>
          <div class="hint">${S().points} ball</div></div><div class="big-emoji">⭐</div></div>${bar((S().points % 50) * 2)}</div>
        <div class="grid2">
          <div class="stat"><b>🔥 ${S().streak.count}</b><span>kunlik streak</span></div>
          <div class="stat"><b>${S().known.length}/${ALL_WORDS.length}</b><span>yodlangan so'z</span></div>
          <div class="stat"><b>${st.test.correct}</b><span>test: to'g'ri javob</span></div>
          <div class="stat"><b>${st.rps.wins + st.guess.wins}</b><span>o'yinlarda g'alaba</span></div>
        </div>
        <h2>Yutuqlar (${unlocked}/${ACHIEVEMENTS.length})</h2>
        <div class="ach">${ACHIEVEMENTS.map((a) => `<div class="${a.ok() ? '' : 'locked'}"><b>${a.icon}</b>${esc(a.name)}</div>`).join('')}</div>
        <p class="hint center" style="margin-top:16px">Progress Telegram hisobingizga saqlanadi va barcha qurilmalarda bir xil bo'ladi.</p>
        <button class="btn secondary" data-act="reset" style="margin-top:8px">🗑 Progressni o'chirish</button>`;
    },
  };

  // ---------- Russian: flashcards and quiz ----------
  function startCards(topic) {
    const words = TOPICS[topic].words;
    let queue = words.map((_, i) => i).filter((i) => !isKnown(topic + ':' + i));
    if (!queue.length) { queue = words.map((_, i) => i); toast("Hammasini bilasiz — takrorlash rejimi"); }
    const params = { topic, queue: shuffle(queue), pos: 0, flipped: false };
    if (view.name === 'cards') { view.params = params; render(); } else go('cards', params);
  }

  function makeQuestion() {
    const word = ALL_WORDS[rand(ALL_WORDS.length)];
    const toUz = Math.random() < 0.5;
    const key = toUz ? 'uz' : 'ru';
    const pool = [...new Set(ALL_WORDS.map((w) => w[key]))].filter((o) => o !== word[key]);
    const options = shuffle([...shuffle(pool).slice(0, 3), word[key]]);
    return { word, toUz, options, answer: options.indexOf(word[key]) };
  }

  function startQuiz() {
    const qs = Array.from({ length: 10 }, makeQuestion);
    const params = { qs, pos: 0, score: 0, picked: null };
    if (view.name === 'quiz') { view.params = params; render(); } else go('quiz', params);
  }

  function speak(text) {
    try {
      const u = new SpeechSynthesisUtterance(text);
      u.lang = 'ru-RU';
      u.rate = 0.85;
      speechSynthesis.cancel();
      speechSynthesis.speak(u);
    } catch (e) { toast("Bu qurilmada ovoz qo'llab-quvvatlanmaydi"); }
  }

  // ---------- Games ----------
  const BEATS = { rock: 'scissors', scissors: 'paper', paper: 'rock' };

  function playRps(choice) {
    const p = view.params;
    const bot = ['rock', 'paper', 'scissors'][rand(3)];
    const st = S().stats.rps;
    st.plays++;
    let text;
    if (choice === bot) { text = '🤝 Durang!'; haptic.tap(); }
    else if (BEATS[choice] === bot) {
      text = '🎉 Siz yutdingiz! +1 ball';
      st.wins++; p.streak = (p.streak || 0) + 1;
      st.bestStreak = Math.max(st.bestStreak, p.streak);
      addPoints(1); haptic.ok();
    } else { text = '😅 Bot yutdi'; p.streak = 0; haptic.err(); }
    p.res = { me: choice, bot, text };
    Store.save();
    render();
  }

  function newGuess() { return { target: 1 + rand(100), tries: 0, msg: '', over: false }; }

  function checkGuess() {
    const p = view.params;
    const input = document.getElementById('guess-input');
    const n = parseInt(input && input.value, 10);
    if (!(n >= 1 && n <= 100)) { toast('1 dan 100 gacha son yozing'); haptic.err(); return; }
    p.tries++;
    const st = S().stats.guess;
    if (n === p.target) {
      const pts = Math.max(1, 9 - p.tries);
      st.plays++; st.wins++;
      st.bestTries = st.bestTries ? Math.min(st.bestTries, p.tries) : p.tries;
      addPoints(pts); p.over = true; p.msg = `🎉 To'g'ri! ${p.tries} urinishda · +${pts} ball`; haptic.ok();
    } else if (p.tries >= 7) {
      st.plays++; p.over = true; p.msg = `😔 Tugadi. Men ${p.target} ni o'ylagandim`; haptic.err();
    } else {
      p.msg = n < p.target ? '⬆️ Kattaroq son' : '⬇️ Kichikroq son'; haptic.tap();
    }
    Store.save();
    render();
  }

  const MEM_EMOJI = ['🍎', '🚀', '🎸', '🐱', '🌙', '⚽', '🍕', '🎲'];
  function newMemory() {
    return { cards: shuffle([...MEM_EMOJI, ...MEM_EMOJI]).map((e) => ({ e, open: false, matched: false })), first: null, moves: 0, lock: false, reward: 0 };
  }

  function flipMemory(i) {
    const p = view.params;
    const c = p.cards[i];
    if (p.lock || c.open || c.matched) return;
    c.open = true;
    haptic.tap();
    if (p.first === null) { p.first = i; render(); return; }

    p.moves++;
    const other = p.cards[p.first];
    if (other.e === c.e) {
      other.matched = c.matched = true;
      p.first = null;
      if (p.cards.every((x) => x.matched)) finishMemory(p);
      render();
      return;
    }
    p.lock = true;
    render();
    const ref = p;
    setTimeout(() => {
      other.open = c.open = false;
      ref.first = null; ref.lock = false;
      if (view.params === ref) render();
    }, 800);
  }

  function finishMemory(p) {
    const st = S().stats.memory;
    p.reward = p.moves <= 12 ? 10 : p.moves <= 16 ? 7 : p.moves <= 20 ? 5 : 3;
    st.plays++;
    st.bestMoves = st.bestMoves ? Math.min(st.bestMoves, p.moves) : p.moves;
    addPoints(p.reward);
    haptic.ok();
  }

  // ---------- Actions (event delegation) ----------
  const ACTIONS = {
    tab: (d) => tab(d.tab),
    cards: (d) => startCards(d.topic),
    flip: () => { view.params.flipped = !view.params.flipped; haptic.tap(); render(); },
    speak: (d) => speak(d.text),
    know: () => {
      const p = view.params;
      const id = p.topic + ':' + p.queue[p.pos];
      if (!isKnown(id)) { S().known.push(id); Store.save(); addPoints(1); toast("✅ Yodlandi! +1 ball"); }
      haptic.ok();
      p.pos++; p.flipped = false; render();
    },
    again: () => {
      const p = view.params;
      p.queue.push(p.queue[p.pos]);
      haptic.tap();
      p.pos++; p.flipped = false; render();
    },
    'open-quiz': startQuiz,
    'open-quiz-new': startQuiz,
    answer: (d) => {
      const p = view.params;
      if (p.picked !== null) return;
      p.picked = +d.i;
      if (p.picked === p.qs[p.pos].answer) { p.score++; S().stats.test.correct++; addPoints(1); haptic.ok(); } else haptic.err();
      Store.save();
      render();
    },
    'next-q': () => {
      const p = view.params;
      p.pos++; p.picked = null;
      if (p.pos >= p.qs.length) {
        const t = S().stats.test;
        t.plays++;
        if (p.score === p.qs.length) t.perfect++;
        Store.save();
      }
      render();
    },
    game: (d) => {
      const g = d.game;
      if (g === 'rps') go('rps', { res: null, streak: 0 });
      else if (g === 'guess') go('guess', newGuess());
      else if (g === 'memory') go('memory', newMemory());
      else if (g === 'guess-new') { view.params = newGuess(); render(); }
      else if (g === 'memory-new') { view.params = newMemory(); render(); }
    },
    rps: (d) => playRps(d.c),
    guess: checkGuess,
    mem: (d) => flipMemory(+d.i),
    reset: () => {
      const doReset = () => { Store.state = DEFAULTS(); Store.touchStreak(); Store.save(); toast("Progress o'chirildi"); render(); };
      if (tg && tg.showConfirm) tg.showConfirm("Hamma progress o'chiriladi. Davom etasizmi?", (ok) => ok && doReset());
      else if (confirm("Hamma progress o'chiriladi. Davom etasizmi?")) doReset();
    },
  };

  document.addEventListener('click', (e) => {
    const el = e.target.closest('[data-act]');
    if (!el || el.disabled) return;
    const fn = ACTIONS[el.dataset.act];
    if (fn) fn(el.dataset, el);
  });

  // ---------- Init ----------
  (async function init() {
    const user = tg && tg.initDataUnsafe && tg.initDataUnsafe.user;
    if (user) {
      document.getElementById('hello').textContent = user.first_name;
      document.getElementById('avatar').textContent = (user.first_name || '🙂').charAt(0).toUpperCase();
    }
    if (tg && tg.BackButton) tg.BackButton.onClick(back);
    await Store.load();
    render();
  })();
})();
