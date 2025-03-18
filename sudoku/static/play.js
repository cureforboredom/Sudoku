document.body.onload = init;

function init() {
  board = document.getElementById("board");

  for (let i = 0; i < 9; i++) {
    row = document.createElement("div");
    row.classList.add("row");

    for (let j = 0; j < 9; j++) {
      cell = document.createElement("div");
      cell.classList.add("cell");
      cell.id = i * 9 + j;
      cell.innerHTML = "<p>0</p>";

      row.append(cell);
    }

    board.append(row);
  }

  window.setInterval(update, 1000);
}

const fetchBoard = async () => {
  const r = await fetch("/api/get_board");
  const data = await r.json();
  return data;
};

const update = async () => {
  board = await fetchBoard();
  for (let i = 0; i < 9; i++) {
    for (let j = 0; j < 9; j++) {
      document.getElementById(i * 9 + j).innerHTML =
        "<p>" + board[i][j][0] + "</p>";
    }
  }
};
