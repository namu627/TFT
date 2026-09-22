/*
 * 롤토체스 최적 조합 탐색 엔진
 *
 * 원본 파이썬 스크립트 두 개를 그대로 옮긴 것입니다.
 *   - solveSpecialization : tft.py  (입력 상징 특성의 레벨을 최대화 = 상징 특화)
 *   - solveFlexibility    : tft2.py (활성 시너지 "종류 수"를 최대화 = 유연함)
 *
 * 원본과 동일한 결과를 내되, 탐색의 병목인 "그리디 채우기" 단계의 점수 계산을
 * 증분(delta) 방식으로 바꿔 속도를 크게 높였습니다. 최종적으로 기록되는 조합의
 * 점수는 원본과 동일한 함수로 다시 계산하므로 결과가 원본과 완전히 일치합니다.
 *
 * 모든 함수는 데이터(champions, traits)를 인자로 받아 순수하게 동작하므로
 * 메인 스레드에서도, 웹 워커에서도 동일하게 사용할 수 있습니다.
 */

const PRIORITY_TRAIT_WEIGHT = 100;
const EXCLUDED_TRAITS_FOR_DIVERSITY = new Set([
  "바이러스", "영혼 살해자", "군주", "네트워크의 신",
]);

/* ------------------------------------------------------------------ */
/* 조합 / 순열 유틸                                                    */
/* ------------------------------------------------------------------ */

// itertools.combinations 와 동일한 순서로 조합을 생성
function* combinations(arr, k) {
  const n = arr.length;
  if (k < 0 || k > n) return;
  if (k === 0) { yield []; return; }
  const idx = Array.from({ length: k }, (_, i) => i);
  while (true) {
    yield idx.map((i) => arr[i]);
    let i = k - 1;
    while (i >= 0 && idx[i] === i + n - k) i--;
    if (i < 0) return;
    idx[i]++;
    for (let j = i + 1; j < k; j++) idx[j] = idx[j - 1] + 1;
  }
}

// set(itertools.permutations(seq)) 와 동일 — 중복 없는 순열
function uniquePermutations(arr) {
  const counts = new Map();
  for (const x of arr) counts.set(x, (counts.get(x) || 0) + 1);
  const items = [...counts.keys()];
  const n = arr.length;
  const res = [];
  const cur = [];
  (function rec() {
    if (cur.length === n) { res.push(cur.slice()); return; }
    for (const it of items) {
      if (counts.get(it) > 0) {
        counts.set(it, counts.get(it) - 1);
        cur.push(it);
        rec();
        cur.pop();
        counts.set(it, counts.get(it) + 1);
      }
    }
  })();
  return res;
}

// 파이썬 튜플 비교(내림차순 정렬용). a > b 이면 -1, a < b 이면 1, 같으면 0
function cmpTupleDesc(a, b) {
  const len = Math.min(a.length, b.length);
  for (let i = 0; i < len; i++) {
    if (a[i] < b[i]) return 1;
    if (a[i] > b[i]) return -1;
  }
  return 0;
}
function tupleGT(a, b) { return cmpTupleDesc(a, b) < 0; }

/* ------------------------------------------------------------------ */
/* 시너지 계산 (공통) — 최종 결과 확정용, 원본과 동일                   */
/* ------------------------------------------------------------------ */

function calcActiveSynergies(team, assignments, champions, traits) {
  const counts = {};
  for (const name of team) {
    const champ = champions[name] || {};
    const all = (champ.traits || []).slice();
    const emblem = assignments[name];
    if (emblem && !all.includes(emblem)) all.push(emblem);
    for (const t of new Set(all)) counts[t] = (counts[t] || 0) + 1;
  }
  const active = {};
  for (const t of Object.keys(counts)) {
    const td = traits[t];
    if (td && td.breakpoints && td.breakpoints.length) {
      const bps = td.breakpoints.slice().sort((x, y) => y - x);
      for (const bp of bps) {
        if (counts[t] >= bp) { active[t] = bp; break; }
      }
    }
  }
  return active;
}

/* ------------------------------------------------------------------ */
/* 점수 함수 — 최종 결과 확정용, 원본과 동일                            */
/* ------------------------------------------------------------------ */

// tft.py: 입력 상징 특성에 가중치 100, 그 외 특성은 소량 보너스
function scoreSpecialization(active, traits, priorityTraits) {
  let priority = 0;
  let other = 0;
  for (const trait of Object.keys(active)) {
    const level = active[trait];
    if (priorityTraits.includes(trait)) {
      priority += level * PRIORITY_TRAIT_WEIGHT;
    } else {
      other += level;
      const info = traits[trait];
      if (info && info.breakpoints && info.breakpoints.length) {
        // 원본 tft.py 는 60% 문턱을 넘긴 특성에만 level*0.2 보너스를 준다.
        // (원본의 `elif level>0 → 0.1` 분기는 들여쓰기상 breakpoints가 비었을 때만
        //  실행되는데, 모든 특성이 breakpoints를 가지므로 실제로는 발동하지 않는다.
        //  동일한 결과를 내기 위해 그 분기는 재현하지 않는다.)
        const maxBp = Math.max(...info.breakpoints);
        const minLevelForBonus = maxBp <= 3 ? 2 : 3;
        if (level >= maxBp * 0.6 && level >= minLevelForBonus) {
          other += level * 0.2;
        }
      }
    }
  }
  return priority + other;
}

// tft2.py: 제외 특성을 뺀 활성 시너지 "종류 수"
function scoreDiversity(active) {
  let s = 0;
  for (const trait of Object.keys(active)) {
    if (active[trait] > 0 && !EXCLUDED_TRAITS_FOR_DIVERSITY.has(trait)) s += 1;
  }
  return s;
}

/* ------------------------------------------------------------------ */
/* 빠른 탐색을 위한 정수 모델 (그리디 채우기 내부 전용)                 */
/* ------------------------------------------------------------------ */

// 특성을 정수 인덱스로 바꾸고, 브레이크포인트/제외여부를 배열로 정리
function buildTraitModel(traits) {
  const traitList = Object.keys(traits);
  const n = traitList.length;
  const idx = new Map();
  const minBp = new Int16Array(n);
  const maxBp = new Int16Array(n);
  const excluded = new Uint8Array(n);
  const sortedBps = [];
  for (let i = 0; i < n; i++) {
    const t = traitList[i];
    idx.set(t, i);
    const bps = (traits[t].breakpoints || []).slice();
    if (bps.length) {
      minBp[i] = Math.min(...bps);
      maxBp[i] = Math.max(...bps);
    }
    sortedBps.push(bps.slice().sort((a, b) => b - a)); // 내림차순
    excluded[i] = EXCLUDED_TRAITS_FOR_DIVERSITY.has(t) ? 1 : 0;
  }
  return { traitList, idx, n, minBp, maxBp, excluded, sortedBps };
}

// 특성 인덱스 ti 의 원소 수가 count 일 때 활성 레벨(달성한 최대 브레이크포인트)
function activeLevelOf(model, ti, count) {
  const bps = model.sortedBps[ti];
  for (let k = 0; k < bps.length; k++) {
    if (count >= bps[k]) return bps[k];
  }
  return 0;
}

// 챔피언 이름 → 고유 특성 인덱스 배열(Int16Array)
function buildChampIndices(model, champions) {
  const m = new Map();
  for (const name of Object.keys(champions)) {
    const seen = new Set();
    const arr = [];
    for (const t of (champions[name].traits || [])) {
      const ti = model.idx.get(t);
      if (ti !== undefined && !seen.has(ti)) { seen.add(ti); arr.push(ti); }
    }
    m.set(name, Int16Array.from(arr));
  }
  return m;
}

// 상징 특화용 특성별 기여도표: contrib[ti][count]
function buildContribSpec(model, priorityIdxSet, maxCount) {
  const contrib = [];
  for (let ti = 0; ti < model.n; ti++) {
    const row = new Float64Array(maxCount + 1);
    const isPriority = priorityIdxSet.has(ti);
    const mb = model.maxBp[ti];
    const minLevelForBonus = mb <= 3 ? 2 : 3;
    for (let c = 0; c <= maxCount; c++) {
      const level = activeLevelOf(model, ti, c);
      if (level === 0) { row[c] = 0; continue; }
      if (isPriority) { row[c] = level * PRIORITY_TRAIT_WEIGHT; continue; }
      let v = level;
      if (level >= mb * 0.6 && level >= minLevelForBonus) v += level * 0.2;
      row[c] = v;
    }
    contrib.push(row);
  }
  return contrib;
}

// 다양성용 특성별 기여도표: 0 또는 1
function buildContribDiv(model, maxCount) {
  const contrib = [];
  for (let ti = 0; ti < model.n; ti++) {
    const row = new Int16Array(maxCount + 1);
    const active = model.excluded[ti] ? 0 : 1;
    for (let c = 0; c <= maxCount; c++) {
      row[c] = (activeLevelOf(model, ti, c) > 0) ? active : 0;
    }
    contrib.push(row);
  }
  return contrib;
}

// team + assignments 로부터 특성별 원소 수(Int16Array) 계산
function countsFromTeam(model, champIdx, champions, team, assignments) {
  const counts = new Int16Array(model.n);
  for (const name of team) {
    const idxs = champIdx.get(name);
    if (idxs) for (let j = 0; j < idxs.length; j++) counts[idxs[j]]++;
    const emblem = assignments && assignments[name];
    if (emblem) {
      const eti = model.idx.get(emblem);
      if (eti !== undefined) {
        // 챔피언 고유 특성에 이미 있으면 중복으로 세지 않음
        let native = false;
        if (idxs) for (let j = 0; j < idxs.length; j++) if (idxs[j] === eti) { native = true; break; }
        if (!native) counts[eti]++;
      }
    }
  }
  return counts;
}

/* ------------------------------------------------------------------ */
/* 모드 A : 상징 특화 (tft.py 포팅)                                     */
/* ------------------------------------------------------------------ */

function solveSpecialization(champions, traits, specs, boardSize) {
  const MAX_CORE = 10;
  const MAX_PRIMARY_HOLDER = 12;
  const MAX_SECONDARY_HOLDER = 12;

  let best = { comp: [], syn: {}, score: -1, assignments: {} };
  if (!specs || specs.length === 0) return best;

  const allNames = Object.keys(champions);
  const sortH = (name) => {
    const d = champions[name] || { cost: 0, traits: [] };
    return [d.cost, (d.traits || []).length];
  };

  const primary = specs[0];
  const primaryTrait = primary.trait;
  const primaryCount = primary.count;
  const secondarySpecs = specs.slice(1);
  const inputEmblemTraits = specs.map((s) => s.trait);

  if (!traits[primaryTrait]) return best;

  // --- 정수 모델 및 기여도표 준비 (그리디 가속용) ---
  const model = buildTraitModel(traits);
  const champIdx = buildChampIndices(model, champions);
  const maxCount = boardSize + 1;
  const priorityIdxSet = new Set(
    inputEmblemTraits.map((t) => model.idx.get(t)).filter((v) => v !== undefined)
  );
  const contribSpec = buildContribSpec(model, priorityIdxSet, maxCount);

  const rawNative = allNames
    .filter((n) => (champions[n].traits || []).includes(primaryTrait))
    .sort((a, b) => cmpTupleDesc(sortH(a), sortH(b)));
  const nativePool = rawNative.slice(0, MAX_CORE);

  const sortedAllForHolders = allNames
    .slice()
    .sort((a, b) => cmpTupleDesc(sortH(a), sortH(b)));

  const targetBps = traits[primaryTrait].breakpoints.slice().sort((a, b) => b - a);

  for (const targetBp of targetBps) {
    if (targetBp === 0) continue;

    let naturalUnits = targetBp - primaryCount;
    if (naturalUnits < 0) naturalUnits = 0;

    let coreCandidates = nativePool;
    if (nativePool.length < naturalUnits) {
      if (rawNative.length >= naturalUnits) coreCandidates = rawNative;
      else continue;
    }

    for (const coreCombo of combinations(coreCandidates, naturalUnits)) {
      const coreSet = new Set(coreCombo);

      const potentialPrimaryHolders = sortedAllForHolders
        .filter((c) => !coreSet.has(c) && !(champions[c].traits || []).includes(primaryTrait))
        .slice(0, MAX_PRIMARY_HOLDER);
      if (potentialPrimaryHolders.length < primaryCount) continue;

      for (const primaryHolders of combinations(potentialPrimaryHolders, primaryCount)) {
        const assignAfterPrimary = {};
        for (const h of primaryHolders) assignAfterPrimary[h] = primaryTrait;

        const teamAfterPrimary = coreCombo.concat(primaryHolders);
        const teamAfterPrimarySet = new Set(teamAfterPrimary);

        const individualSecondary = [];
        for (const s of secondarySpecs) {
          for (let i = 0; i < s.count; i++) individualSecondary.push(s.trait);
        }
        const numSecondaryNeeded = individualSecondary.length;

        const potentialSecondaryPool = sortedAllForHolders
          .filter((c) => !teamAfterPrimarySet.has(c))
          .slice(0, MAX_SECONDARY_HOLDER);

        if (potentialSecondaryPool.length < numSecondaryNeeded && numSecondaryNeeded > 0) continue;

        const secondaryHolderCombos = numSecondaryNeeded > 0
          ? combinations(potentialSecondaryPool, numSecondaryNeeded)
          : [[]];

        for (const secondaryHolders of secondaryHolderCombos) {
          const emblemPerms = numSecondaryNeeded > 0
            ? uniquePermutations(individualSecondary)
            : [[]];

          for (const perm of emblemPerms) {
            const assignments = Object.assign({}, assignAfterPrimary);
            let valid = true;
            for (let i = 0; i < secondaryHolders.length; i++) {
              const ch = secondaryHolders[i];
              const tr = perm[i];
              if (ch in assignments && assignments[ch] !== tr) { valid = false; break; }
              assignments[ch] = tr;
            }
            if (!valid) continue;

            const team = coreCombo.concat(primaryHolders, secondaryHolders);
            const numFillers = boardSize - team.length;
            if (numFillers < 0) continue;

            // --- 그리디 채우기 (증분 점수) ---
            const teamSet = new Set(team);
            const counts = countsFromTeam(model, champIdx, champions, team, assignments);
            for (let f = 0; f < numFillers; f++) {
              let bestFiller = null;
              let bestDelta = -1;
              for (const cand of allNames) {
                if (teamSet.has(cand)) continue;
                const idxs = champIdx.get(cand);
                let delta = 0;
                for (let j = 0; j < idxs.length; j++) {
                  const ti = idxs[j];
                  const c = counts[ti];
                  delta += contribSpec[ti][c + 1] - contribSpec[ti][c];
                }
                if (delta > bestDelta) { bestDelta = delta; bestFiller = cand; }
              }
              if (bestFiller) {
                team.push(bestFiller);
                teamSet.add(bestFiller);
                const idxs = champIdx.get(bestFiller);
                for (let j = 0; j < idxs.length; j++) counts[idxs[j]]++;
              } else break;
            }

            if (team.length === boardSize) {
              // 값싼 사전점수(counts 기반)로 현재 최고점을 넘을 가능성이 있는
              // 잎(leaf)만 걸러낸다. 점수 간 최소 간격(0.2)보다 훨씬 작은 여유(1e-6)를
              // 두므로 진짜 개선/동점 잎은 절대 건너뛰지 않는다.
              let scFast = 0;
              for (let ti = 0; ti < model.n; ti++) scFast += contribSpec[ti][counts[ti]];
              if (scFast > best.score - 1e-6) {
                // 최종 점수/시너지는 원본과 동일한 함수로 확정 (결과 완전 일치 보장)
                const syns = calcActiveSynergies(team, assignments, champions, traits);
                const sc = scoreSpecialization(syns, traits, inputEmblemTraits);
                if (sc > best.score) {
                  best = {
                    comp: team.slice().sort(),
                    syn: syns,
                    score: sc,
                    assignments: Object.assign({}, assignments),
                  };
                }
              }
            }
          }
        }
      }
    }
  }
  return best;
}

/* ------------------------------------------------------------------ */
/* 모드 B : 유연함 / 다양성 (tft2.py 포팅)                              */
/* ------------------------------------------------------------------ */

function solveFlexibility(champions, traits, specs, boardSize) {
  const MAX_HOLDER_CAND = 15;
  const MAX_LOCAL_ITER = 5;

  let best = { comp: [], syn: {}, score: -1, assignments: {} };
  const allNames = Object.keys(champions);
  const sortH = (name) => {
    const d = champions[name] || { cost: 0, traits: [] };
    return [d.cost, (d.traits || []).length, name];
  };
  const teamCost = (t) => t.reduce((s, c) => s + ((champions[c] || {}).cost || 0), 0);

  /* --- 상징이 없는 경우: 그리디 + 지역 탐색 (원본 그대로) --- */
  if (!specs || specs.length === 0) {
    let team = [];
    const teamSet = new Set();
    for (let slot = 0; slot < boardSize; slot++) {
      let bestFiller = null;
      let bestDiv = -1;
      const candidates = allNames.filter((c) => !teamSet.has(c));
      if (candidates.length === 0) break;
      for (const cand of candidates) {
        const syns = calcActiveSynergies(team.concat([cand]), {}, champions, traits);
        const div = scoreDiversity(syns);
        if (div > bestDiv) { bestDiv = div; bestFiller = cand; }
        else if (div === bestDiv && bestFiller && tupleGT(sortH(cand), sortH(bestFiller))) {
          bestFiller = cand;
        }
      }
      if (bestFiller) { team.push(bestFiller); teamSet.add(bestFiller); }
      else if (team.length < boardSize && candidates.length) {
        candidates.sort((a, b) => cmpTupleDesc(sortH(a), sortH(b)));
        team.push(candidates[0]); teamSet.add(candidates[0]);
      } else break;
    }

    if (team.length === boardSize) {
      let curSyn = calcActiveSynergies(team, {}, champions, traits);
      let curDiv = scoreDiversity(curSyn);

      for (let it = 0; it < MAX_LOCAL_ITER; it++) {
        let improved = false;
        let teamToImprove = team.slice();
        for (let i = 0; i < teamToImprove.length; i++) {
          const original = teamToImprove[i];
          const baseTeam = teamToImprove.slice(0, i).concat(teamToImprove.slice(i + 1));
          const baseSet = new Set(baseTeam);
          const swapCandidates = allNames.filter((c) => !baseSet.has(c));
          for (const nc of swapCandidates) {
            if (nc === original) continue;
            const swapped = baseTeam.concat([nc]);
            if (new Set(swapped).size !== boardSize) continue;
            const sSyn = calcActiveSynergies(swapped, {}, champions, traits);
            const sDiv = scoreDiversity(sSyn);
            if (sDiv > curDiv || (sDiv === curDiv && teamCost(swapped) > teamCost(teamToImprove))) {
              teamToImprove = swapped.slice().sort();
              curDiv = sDiv;
              curSyn = sSyn;
              improved = true;
            }
          }
        }
        if (improved) team = teamToImprove;
        else break;
      }

      if (curDiv > best.score ||
          (curDiv === best.score && (best.comp.length === 0 || teamCost(team) > teamCost(best.comp)))) {
        best = { comp: team.slice().sort(), syn: curSyn, score: curDiv, assignments: {} };
      }
    }
    return best;
  }

  /* --- 상징이 있는 경우: 보유자 조합 + 그리디 채우기 (증분 점수) --- */
  const model = buildTraitModel(traits);
  const champIdx = buildChampIndices(model, champions);
  const maxCount = boardSize + 1;
  const contribDiv = buildContribDiv(model, maxCount);

  const individualEmblems = [];
  for (const s of specs) for (let i = 0; i < s.count; i++) individualEmblems.push(s.trait);
  const numHolders = individualEmblems.length;

  if (numHolders > boardSize) return best;
  const numFillers = boardSize - numHolders;

  let holderPool = allNames
    .slice()
    .sort((a, b) => cmpTupleDesc(sortH(a), sortH(b)))
    .slice(0, MAX_HOLDER_CAND);
  if (holderPool.length < numHolders) {
    holderPool = allNames.slice().sort((a, b) => cmpTupleDesc(sortH(a), sortH(b)));
    if (holderPool.length < numHolders) return best;
  }

  // sortH 튜플을 미리 계산해 그리디 타이브레이크에 사용
  const sortKey = new Map(allNames.map((n) => [n, sortH(n)]));

  for (const holders of combinations(holderPool, numHolders)) {
    const emblemSeqs = uniquePermutations(individualEmblems);
    for (const perm of emblemSeqs) {
      const assignments = {};
      for (let i = 0; i < holders.length; i++) assignments[holders[i]] = perm[i];

      const team = holders.slice();
      const teamSet = new Set(team);
      const counts = countsFromTeam(model, champIdx, champions, team, assignments);

      for (let f = 0; f < numFillers; f++) {
        // 현재 팀의 다양성 점수(기준)
        let curDivBase = 0;
        for (let ti = 0; ti < model.n; ti++) curDivBase += contribDiv[ti][counts[ti]];

        let bestFiller = null;
        let bestDiv = -1;
        let bestKey = null;
        let anyCand = false;
        for (const cand of allNames) {
          if (teamSet.has(cand)) continue;
          anyCand = true;
          const idxs = champIdx.get(cand);
          let delta = 0;
          for (let j = 0; j < idxs.length; j++) {
            const ti = idxs[j];
            const c = counts[ti];
            delta += contribDiv[ti][c + 1] - contribDiv[ti][c];
          }
          const div = curDivBase + delta;
          const key = sortKey.get(cand);
          if (div > bestDiv) { bestDiv = div; bestFiller = cand; bestKey = key; }
          else if (div === bestDiv && bestFiller && tupleGT(key, bestKey)) {
            bestFiller = cand; bestKey = key;
          }
        }
        if (bestFiller) {
          team.push(bestFiller);
          teamSet.add(bestFiller);
          const idxs = champIdx.get(bestFiller);
          for (let j = 0; j < idxs.length; j++) counts[idxs[j]]++;
        } else if (team.length < boardSize && anyCand) {
          // (원본 재현용 폴백 — 실제로는 위에서 항상 bestFiller가 정해진다)
          const remaining = allNames.filter((c) => !teamSet.has(c));
          remaining.sort((a, b) => cmpTupleDesc(sortH(a), sortH(b)));
          const pick = remaining[0];
          team.push(pick); teamSet.add(pick);
          const idxs = champIdx.get(pick);
          for (let j = 0; j < idxs.length; j++) counts[idxs[j]]++;
        } else break;
      }

      if (team.length === boardSize) {
        // 다양성 점수는 정수이므로 counts 기반 사전점수가 최종 점수와 정확히 같다.
        // 현재 최고점보다 낮은 잎은 동점 타이브레이크 대상도 아니므로 건너뛴다.
        let scFast = 0;
        for (let ti = 0; ti < model.n; ti++) scFast += contribDiv[ti][counts[ti]];
        if (scFast >= best.score) {
          // 최종 점수/시너지는 원본과 동일한 함수로 확정
          const syns = calcActiveSynergies(team, assignments, champions, traits);
          const sc = scoreDiversity(syns);
          if (sc > best.score ||
              (sc === best.score && best.comp.length && teamCost(team) > teamCost(best.comp))) {
            best = {
              comp: team.slice().sort(),
              syn: syns,
              score: sc,
              assignments: Object.assign({}, assignments),
            };
          }
        }
      }
    }
  }
  return best;
}

/* ------------------------------------------------------------------ */

function solve(mode, champions, traits, specs, boardSize) {
  return mode === "flexibility"
    ? solveFlexibility(champions, traits, specs, boardSize)
    : solveSpecialization(champions, traits, specs, boardSize);
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    solve, solveSpecialization, solveFlexibility,
    calcActiveSynergies, scoreSpecialization, scoreDiversity,
  };
}
