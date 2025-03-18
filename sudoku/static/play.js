document.body.onload = init;

current_board_hash = "";

current_board = [];

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
  const r = await fetch("/api/get_board?hash=" + current_board_hash);
  if ((await r.status) != 204) {
    const data = await r.json();
    current_board_hash = data["hash"];
    current_board = data["board"];
  }
};

const update = async () => {
  await fetchBoard();
  for (let i = 0; i < 9; i++) {
    for (let j = 0; j < 9; j++) {
      document.getElementById(i * 9 + j).innerHTML =
        "<p>" + current_board[i][j][0] + "</p>";
    }
  }
};
