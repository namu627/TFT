/*
 * 화면 로직: 입력 폼 구성 → (웹 워커 또는 폴백으로) 탐색 실행 → 결과 렌더링.
 * 탐색 엔진(solver.js)과 데이터(data.js)는 전역으로 이미 로드되어 있습니다.
 */

(function () {
  "use strict";

  // 유연함 모드에서 점수 계산에 넣지 않는 특성 (표시용 — solver.js 와 동일)
  var EXCLUDED = ["바이러스", "영혼 살해자", "군주", "네트워크의 신"];
  var COST_LABEL = { 1: "1", 2: "2", 3: "3", 4: "4", 5: "5" };

  var traitNames = Object.keys(TRAITS);

  var el = {
    modeGroup: document.getElementById("modeGroup"),
    emblemRows: document.getElementById("emblemRows"),
    emblemHint: document.getElementById("emblemHint"),
    addEmblem: document.getElementById("addEmblem"),
    boardSize: document.getElementById("boardSize"),
    run: document.getElementById("run"),
    status: document.getElementById("status"),
    result: document.getElementById("result"),
  };

  /* ---------------------- 입력 폼 ---------------------- */

  function currentMode() {
    var checked = el.modeGroup.querySelector('input[name="mode"]:checked');
    return checked ? checked.value : "specialization";
  }

  function makeEmblemRow() {
    var row = document.createElement("div");
    row.className = "emblem-row";

    var select = document.createElement("select");
    select.className = "trait-select";
    for (var i = 0; i < traitNames.length; i++) {
      var opt = document.createElement("option");
      opt.value = traitNames[i];
      opt.textContent = traitNames[i];
      select.appendChild(opt);
    }

    var count = document.createElement("input");
    count.type = "number";
    count.className = "count-input";
    count.min = "1";
    count.max = "10";
    count.value = "1";
    count.setAttribute("aria-label", "상징 개수");

    var remove = document.createElement("button");
    remove.type = "button";
    remove.className = "remove";
    remove.textContent = "삭제";
    remove.addEventListener("click", function () {
      row.parentNode.removeChild(row);
    });

    row.appendChild(select);
    row.appendChild(count);
    row.appendChild(remove);
    return row;
  }

  function addEmblemRow() {
    el.emblemRows.appendChild(makeEmblemRow());
  }

  function refreshHint() {
    el.emblemHint.textContent =
      currentMode() === "specialization" ? "(하나 이상 선택)" : "(선택 사항)";
  }

  el.addEmblem.addEventListener("click", addEmblemRow);
  el.modeGroup.addEventListener("change", refreshHint);
  addEmblemRow();
  refreshHint();

  /* ---------------------- 입력 수집 / 검증 ---------------------- */

  // 같은 특성 행은 개수를 합쳐 하나로 정리 (첫 등장 순서 유지)
  function gatherSpecs() {
    var rows = el.emblemRows.querySelectorAll(".emblem-row");
    var order = [];
    var byTrait = {};
    for (var i = 0; i < rows.length; i++) {
      var trait = rows[i].querySelector(".trait-select").value;
      var c = parseInt(rows[i].querySelector(".count-input").value, 10);
      if (!c || c < 1) continue;
      if (!(trait in byTrait)) { byTrait[trait] = 0; order.push(trait); }
      byTrait[trait] += c;
    }
    return order.map(function (t) { return { trait: t, count: byTrait[t] }; });
  }

  function readBoardSize() {
    var n = parseInt(el.boardSize.value, 10);
    if (isNaN(n)) n = 8;
    if (n < 1) n = 1;
    if (n > 10) n = 10;
    el.boardSize.value = String(n);
    return n;
  }

  function validate(mode, specs, boardSize) {
    if (mode === "specialization" && specs.length === 0) {
      return "상징을 하나 이상 선택하세요.";
    }
    var totalHolders = specs.reduce(function (s, x) { return s + x.count; }, 0);
    if (totalHolders > boardSize) {
      return "상징 개수의 합(" + totalHolders + ")이 배치 기물 수(" + boardSize + ")보다 많습니다.";
    }
    return null;
  }

  /* ---------------------- 탐색 실행 (워커 + 폴백) ---------------------- */

  var worker = null;
  var workerBroken = false;

  function getWorker() {
    if (workerBroken) return null;
    if (worker) return worker;
    try {
      worker = new Worker("worker.js");
      return worker;
    } catch (e) {
      workerBroken = true;
      return null;
    }
  }

  function mainThreadSolve(mode, specs, boardSize) {
    return new Promise(function (resolve) {
      // 로딩 표시가 먼저 그려지도록 다음 틱으로 미룸
      setTimeout(function () {
        resolve(solve(mode, CHAMPIONS, TRAITS, specs, boardSize));
      }, 0);
    });
  }

  function computeAsync(mode, specs, boardSize) {
    return new Promise(function (resolve) {
      var w = getWorker();
      if (!w) { mainThreadSolve(mode, specs, boardSize).then(resolve); return; }

      var done = false;
      function cleanup() {
        w.removeEventListener("message", onMsg);
        w.removeEventListener("error", onErr);
      }
      function onMsg(ev) {
        if (done) return;
        done = true; cleanup();
        if (ev.data && ev.data.ok) resolve(ev.data.result);
        else mainThreadSolve(mode, specs, boardSize).then(resolve);
      }
      function onErr() {
        if (done) return;
        done = true; cleanup();
        // 워커가 동작하지 않는 환경(파일 직접 열기 등) → 메인 스레드로 전환
        workerBroken = true; worker = null;
        mainThreadSolve(mode, specs, boardSize).then(resolve);
      }
      w.addEventListener("message", onMsg);
      w.addEventListener("error", onErr);
      w.postMessage({ mode: mode, specs: specs, boardSize: boardSize });
    });
  }

  /* ---------------------- 실행 버튼 ---------------------- */

  el.run.addEventListener("click", function () {
    var mode = currentMode();
    var specs = gatherSpecs();
    var boardSize = readBoardSize();

    var err = validate(mode, specs, boardSize);
    if (err) { showStatus(err, false); hide(el.result); return; }

    hide(el.result);
    showStatus("최적 조합을 찾는 중입니다…", true);
    el.run.disabled = true;

    computeAsync(mode, specs, boardSize).then(function (res) {
      el.run.disabled = false;
      hide(el.status);
      renderResult(mode, specs, res);
    }).catch(function (e) {
      el.run.disabled = false;
      showStatus("계산 중 문제가 발생했습니다: " + String(e), false);
    });
  });

  /* ---------------------- 표시 유틸 ---------------------- */

  function hide(node) { node.hidden = true; node.innerHTML = ""; }

  function showStatus(text, busy) {
    el.status.hidden = false;
    el.status.className = busy ? "status busy" : "status warn";
    el.status.textContent = text;
  }

  function computeRawCounts(comp, assignments) {
    var counts = {};
    for (var i = 0; i < comp.length; i++) {
      var name = comp[i];
      var data = CHAMPIONS[name] || { traits: [] };
      var set = {};
      var tr = data.traits || [];
      for (var j = 0; j < tr.length; j++) set[tr[j]] = true;
      var emblem = assignments[name];
      if (emblem) set[emblem] = true;
      for (var t in set) counts[t] = (counts[t] || 0) + 1;
    }
    return counts;
  }

  function renderResult(mode, specs, res) {
    el.result.hidden = false;
    el.result.innerHTML = "";

    if (!res || res.score < 0 || !res.comp || res.comp.length === 0) {
      var empty = document.createElement("p");
      empty.className = "empty";
      empty.textContent = "조건을 만족하는 조합을 찾지 못했습니다. 상징 개수나 배치 기물 수를 조정해 보세요.";
      el.result.appendChild(empty);
      return;
    }

    var inputTraits = {};
    specs.forEach(function (s) { inputTraits[s.trait] = true; });
    var rawCounts = computeRawCounts(res.comp, res.assignments || {});

    /* --- 요약 --- */
    var summary = document.createElement("p");
    summary.className = "summary";
    if (mode === "flexibility") {
      summary.textContent = "활성 시너지 " + res.score + "종을 만드는 조합입니다.";
    } else {
      var primary = specs[0].trait;
      summary.textContent = primary + " 시너지를 " + (rawCounts[primary] || 0) + "까지 올리는 조합입니다.";
    }
    el.result.appendChild(summary);

    /* --- 챔피언 --- */
    var champSection = document.createElement("section");
    champSection.className = "block";
    champSection.appendChild(heading("챔피언 " + res.comp.length + "기"));

    var list = document.createElement("ul");
    list.className = "champ-list";

    var sorted = res.comp.slice().sort(function (a, b) {
      var ca = (CHAMPIONS[a] || {}).cost || 0;
      var cb = (CHAMPIONS[b] || {}).cost || 0;
      if (cb !== ca) return cb - ca;
      return a < b ? -1 : a > b ? 1 : 0;
    });

    sorted.forEach(function (name) {
      var data = CHAMPIONS[name] || { cost: 0, traits: [] };
      var li = document.createElement("li");
      li.className = "champ cost-" + (data.cost || 0);

      var cost = document.createElement("span");
      cost.className = "cost-badge";
      cost.textContent = COST_LABEL[data.cost] || String(data.cost || "");
      li.appendChild(cost);

      var nm = document.createElement("span");
      nm.className = "champ-name";
      nm.textContent = name;
      li.appendChild(nm);

      var traits = document.createElement("span");
      traits.className = "champ-traits";
      traits.textContent = (data.traits || []).join(", ");
      li.appendChild(traits);

      var emblem = (res.assignments || {})[name];
      if (emblem) {
        var badge = document.createElement("span");
        badge.className = "emblem-badge";
        badge.textContent = "상징 " + emblem;
        li.appendChild(badge);
      }

      list.appendChild(li);
    });
    champSection.appendChild(list);
    el.result.appendChild(champSection);

    /* --- 활성 시너지 --- */
    var synSection = document.createElement("section");
    synSection.className = "block";
    synSection.appendChild(heading("활성 시너지"));

    var synList = document.createElement("ul");
    synList.className = "syn-list";

    var synEntries = Object.keys(res.syn || {}).map(function (t) {
      return { trait: t, level: res.syn[t], count: rawCounts[t] || res.syn[t] };
    });
    synEntries.sort(function (a, b) {
      if (b.count !== a.count) return b.count - a.count;
      return a.trait < b.trait ? -1 : a.trait > b.trait ? 1 : 0;
    });

    synEntries.forEach(function (e) {
      var li = document.createElement("li");
      li.className = "syn";
      if (inputTraits[e.trait]) li.className += " syn-input";

      var count = document.createElement("span");
      count.className = "syn-count";
      count.textContent = e.count;
      li.appendChild(count);

      var nm = document.createElement("span");
      nm.className = "syn-name";
      nm.textContent = e.trait;
      li.appendChild(nm);

      var tags = [];
      if (inputTraits[e.trait]) tags.push("입력 상징");
      if (mode === "flexibility" && EXCLUDED.indexOf(e.trait) !== -1) tags.push("점수 제외");
      if (tags.length) {
        var tag = document.createElement("span");
        tag.className = "syn-tag";
        tag.textContent = tags.join(" · ");
        li.appendChild(tag);
      }

      synList.appendChild(li);
    });
    synSection.appendChild(synList);
    el.result.appendChild(synSection);

    /* --- 상징 배치 --- */
    var assigns = res.assignments || {};
    var assignKeys = Object.keys(assigns);
    if (assignKeys.length) {
      var placeSection = document.createElement("section");
      placeSection.className = "block";
      placeSection.appendChild(heading("상징 배치"));

      var pList = document.createElement("ul");
      pList.className = "place-list";
      assignKeys.forEach(function (champ) {
        var li = document.createElement("li");
        li.textContent = champ + " → " + assigns[champ];
        pList.appendChild(li);
      });
      placeSection.appendChild(pList);
      el.result.appendChild(placeSection);
    }
  }

  function heading(text) {
    var h = document.createElement("h2");
    h.className = "block-title";
    h.textContent = text;
    return h;
  }
})();
