const ANSWER_WORDS = window.ANSWER_WORDS;
const VALID_WORDS = window.VALID_WORDS;

const ROWS = 6;
const COLS = 5;
const KEY_ROWS = [["Q","W","E","R","T","Y","U","I","O","P"], ["A","S","D","F","G","H","J","K","L"], ["ENTER","Z","X","C","V","B","N","M","⌫"]];
const STATE_RANK = { absent: 1, present: 2, correct: 3 };

const state = {
  answer: "",
  row: 0,
  col: 0,
  guesses: Array.from({ length: ROWS }, () => Array(COLS).fill("")),
  keyStates: {},
  locked: false,
  over: false
};

const board = document.querySelector("#board");
const keyboard = document.querySelector("#keyboard");
const message = document.querySelector("#message");
const modalBackdrop = document.querySelector("#modalBackdrop");
const modalContent = document.querySelector("#modalContent");

function buildBoard() {
  board.innerHTML = "";
  for (let row = 0; row < ROWS; row++) {
    const rowEl = document.createElement("div");
    rowEl.className = "board-row";
    rowEl.dataset.row = row;
    rowEl.setAttribute("role", "row");
    for (let col = 0; col < COLS; col++) {
      const tile = document.createElement("div");
      tile.className = "tile";
      tile.dataset.row = row;
      tile.dataset.col = col;
      tile.setAttribute("role", "gridcell");
      rowEl.append(tile);
    }
    board.append(rowEl);
  }
}

function buildKeyboard() {
  keyboard.innerHTML = "";
  KEY_ROWS.forEach(keys => {
    const row = document.createElement("div");
    row.className = "key-row";
    keys.forEach(letter => {
      const key = document.createElement("button");
      key.className = `key${letter.length > 1 ? " wide" : ""}`;
      key.dataset.key = letter;
      key.textContent = letter;
      key.setAttribute("aria-label", letter === "⌫" ? "Backspace" : letter);
      key.addEventListener("click", () => handleKey(letter));
      row.append(key);
    });
    keyboard.append(row);
  });
}

function chooseWord() {
  return ANSWER_WORDS[Math.floor(Math.random() * ANSWER_WORDS.length)];
}

function startGame() {
  state.answer = chooseWord();
  state.row = 0;
  state.col = 0;
  state.guesses = Array.from({ length: ROWS }, () => Array(COLS).fill(""));
  state.keyStates = {};
  state.locked = false;
  state.over = false;
  message.textContent = "";
  buildBoard();
  buildKeyboard();
}

function handleKey(rawKey) {
  if (state.locked || state.over) return;
  const key = rawKey.toUpperCase();
  if (key === "BACKSPACE" || key === "DELETE" || key === "⌫") return removeLetter();
  if (key === "ENTER") return submitGuess();
  if (/^[A-Z]$/.test(key)) addLetter(key);
}

function addLetter(letter) {
  if (state.col >= COLS) return;
  state.guesses[state.row][state.col] = letter;
  const tile = getTile(state.row, state.col);
  tile.textContent = letter;
  tile.classList.add("filled");
  state.col++;
}

function removeLetter() {
  if (state.col === 0) return;
  state.col--;
  state.guesses[state.row][state.col] = "";
  const tile = getTile(state.row, state.col);
  tile.textContent = "";
  tile.classList.remove("filled");
}

function scoreGuess(guess, answer) {
  const result = Array(COLS).fill("absent");
  const remaining = {};
  for (let i = 0; i < COLS; i++) {
    if (guess[i] === answer[i]) result[i] = "correct";
    else remaining[answer[i]] = (remaining[answer[i]] || 0) + 1;
  }
  for (let i = 0; i < COLS; i++) {
    if (result[i] === "correct") continue;
    if (remaining[guess[i]] > 0) {
      result[i] = "present";
      remaining[guess[i]]--;
    }
  }
  return result;
}

function submitGuess() {
  if (state.col < COLS) return notify("Not enough letters", true);
  const guess = state.guesses[state.row].join("");
  if (!VALID_WORDS.has(guess)) return notify("Try another word", true);

  state.locked = true;
  const result = scoreGuess(guess, state.answer);
  result.forEach((status, index) => {
    const tile = getTile(state.row, index);
    setTimeout(() => {
      tile.classList.add("reveal");
      setTimeout(() => tile.classList.add(status), 245);
      updateKey(guess[index], status);
    }, index * 230);
  });

  setTimeout(() => finishTurn(guess), COLS * 230 + 350);
}

function finishTurn(guess) {
  state.row++;
  state.col = 0;
  state.locked = false;
  if (guess === state.answer) {
    state.over = true;
    message.textContent = ["Beautiful!", "Excellent!", "Splendid!", "Well played!"][Math.min(state.row - 1, 3)];
    recordResult(true, state.row);
    setTimeout(() => showResult(true), 650);
  } else if (state.row === ROWS) {
    state.over = true;
    message.textContent = `The word was ${state.answer}`;
    recordResult(false);
    setTimeout(() => showResult(false), 650);
  } else {
    message.textContent = "Keep going";
    setTimeout(() => { if (!state.over) message.textContent = ""; }, 1000);
  }
}

function updateKey(letter, status) {
  if (!state.keyStates[letter] || STATE_RANK[status] > STATE_RANK[state.keyStates[letter]]) {
    state.keyStates[letter] = status;
  }
  const key = document.querySelector(`[data-key="${letter}"]`);
  key.classList.remove("absent", "present", "correct");
  key.classList.add(state.keyStates[letter]);
}

function notify(text, shake) {
  message.textContent = text;
  if (shake) {
    const row = document.querySelector(`.board-row[data-row="${state.row}"]`);
    row.classList.remove("shake");
    void row.offsetWidth;
    row.classList.add("shake");
  }
  setTimeout(() => { if (!state.locked && !state.over) message.textContent = ""; }, 1200);
}

function getTile(row, col) {
  return document.querySelector(`.tile[data-row="${row}"][data-col="${col}"]`);
}

function getStats() {
  try { return JSON.parse(localStorage.getItem("letterly-stats")) || { played: 0, wins: 0, streak: 0, best: 0 }; }
  catch { return { played: 0, wins: 0, streak: 0, best: 0 }; }
}

function recordResult(won) {
  const stats = getStats();
  stats.played++;
  if (won) {
    stats.wins++;
    stats.streak++;
    stats.best = Math.max(stats.best, stats.streak);
  } else stats.streak = 0;
  localStorage.setItem("letterly-stats", JSON.stringify(stats));
}

function openModal(html) {
  modalContent.innerHTML = html;
  modalBackdrop.hidden = false;
  document.body.style.overflow = "hidden";
  document.querySelector("#modalClose").focus();
}

function closeModal() {
  modalBackdrop.hidden = true;
  document.body.style.overflow = "";
}

function showHelp() {
  openModal(`
    <p class="eyebrow">THE BASICS</p>
    <h2 id="modalTitle">How to play</h2>
    <p class="modal-lead">Guess the hidden word in six tries. Each guess must be a valid five-letter word.</p>
    <div class="examples">
      <div class="example-row"><span class="example-tile correct">C</span><span class="example-tile">R</span><span class="example-tile">A</span><span class="example-tile">N</span><span class="example-tile">E</span></div>
      <p class="explanation"><strong>C</strong> is in the word and in the right spot.</p>
      <div class="example-row"><span class="example-tile">P</span><span class="example-tile present">L</span><span class="example-tile">A</span><span class="example-tile">N</span><span class="example-tile">T</span></div>
      <p class="explanation"><strong>L</strong> is in the word but in the wrong spot.</p>
      <div class="example-row"><span class="example-tile">B</span><span class="example-tile">R</span><span class="example-tile absent">I</span><span class="example-tile">C</span><span class="example-tile">K</span></div>
      <p class="explanation"><strong>I</strong> is not in the word.</p>
    </div>`);
}

function showStats() {
  const stats = getStats();
  const rate = stats.played ? Math.round(stats.wins / stats.played * 100) : 0;
  openModal(`
    <p class="eyebrow">YOUR JOURNEY</p>
    <h2 id="modalTitle">Statistics</h2>
    <p class="modal-lead">A little record of every word you've chased.</p>
    <div class="modal-stats">
      <div><strong>${stats.played}</strong><span>PLAYED</span></div>
      <div><strong>${rate}%</strong><span>WIN RATE</span></div>
      <div><strong>${stats.best}</strong><span>BEST STREAK</span></div>
    </div>
    <button class="primary-button" data-action="close">BACK TO PUZZLE</button>`);
}

function showResult(won) {
  const stats = getStats();
  openModal(`
    <p class="eyebrow">${won ? "PUZZLE COMPLETE" : "SO CLOSE"}</p>
    <h2 id="modalTitle">${won ? "Wonderfully done." : "Another word awaits."}</h2>
    <p class="modal-lead">${won ? `You found <strong>${state.answer}</strong> in ${state.row} ${state.row === 1 ? "try" : "tries"}.` : `The hidden word was <strong>${state.answer}</strong>.`}</p>
    <div class="modal-stats">
      <div><strong>${stats.played}</strong><span>PLAYED</span></div>
      <div><strong>${stats.streak}</strong><span>STREAK</span></div>
      <div><strong>${stats.best}</strong><span>BEST</span></div>
    </div>
    <button class="primary-button" data-action="new">PLAY ANOTHER WORD</button>`);
}

document.addEventListener("keydown", event => {
  if (!modalBackdrop.hidden) {
    if (event.key === "Escape") closeModal();
    return;
  }
  handleKey(event.key);
});
document.querySelector("#helpButton").addEventListener("click", showHelp);
document.querySelector("#statsButton").addEventListener("click", showStats);
document.querySelector("#modalClose").addEventListener("click", closeModal);
modalBackdrop.addEventListener("click", event => { if (event.target === modalBackdrop) closeModal(); });
modalContent.addEventListener("click", event => {
  if (event.target.dataset.action === "close") closeModal();
  if (event.target.dataset.action === "new") { closeModal(); startGame(); }
});

document.querySelector("#todayDate").textContent = new Intl.DateTimeFormat("en-US", { month: "long", day: "numeric", year: "numeric" }).format(new Date()).toUpperCase();
startGame();
