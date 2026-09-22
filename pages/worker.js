/*
 * 웹 워커: 무거운 탐색을 메인 스레드 밖에서 실행해 화면이 멈추지 않게 합니다.
 * data.js 와 solver.js 를 그대로 불러와 solve() 를 호출합니다.
 */

importScripts("data.js", "solver.js");

self.onmessage = function (e) {
  const { mode, specs, boardSize } = e.data || {};
  try {
    const result = solve(mode, CHAMPIONS, TRAITS, specs, boardSize);
    self.postMessage({ ok: true, result });
  } catch (err) {
    self.postMessage({ ok: false, error: String((err && err.message) || err) });
  }
};
