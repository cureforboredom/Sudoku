document.body.onload = init;

current_board_hash = "";

current_board = [];

have_set_editable = false;

selected_cell = null;

function init() {
  dom_board = document.getElementById("board");

  for (let i = 0; i < 9; i++) {
    row = document.createElement("div");
    row.classList.add("row");

    for (let j = 0; j < 9; j++) {
      cell = document.createElement("div");
      cell.classList.add("cell");
      if (i == 2 || i == 5) {
        cell.classList.add("border-bottom");
      }
      if (j == 2 || j == 5) {
        cell.classList.add("border-right");
      }
      cell.id = i * 9 + j;
      cell.innerHTML = "<p>0</p>";
      cell.onclick = function () {
        document.getElementById("picker-container").style.display = "flex";
        selected_cell = this;
      };

      row.append(cell);
    }

    dom_board.append(row);
  }

  document.getElementById("picker-closer").onclick = function () {
    document.getElementById("picker-container").style.display = "none";
  };

  picker = document.getElementById("picker");

  for (let i = 0; i < 3; i++) {
    row = document.createElement("div");
    for (let j = 0; j < 3; j++) {
      cell = document.createElement("div");
      cell.id = i * 3 + j + 1;
      cell.classList.add("choice");
      cell.innerHTML = "<p>" + (i * 3 + j + 1) + "</p>";
      cell.onclick = function () {
        modifyBoard(selected_cell, this.id);
        document.getElementById("picker-container").style.display = "none";
      };
      row.append(cell);
    }
    picker.append(row);
  }

  clear = document.createElement("div");
  clear.id = "clear";
  clear.innerHTML = "<p>Clear</p>";
  clear.onclick = function () {
    modifyBoard(selected_cell, 0);
    document.getElementById("picker-container").style.display = "none";
  };

  picker.append(clear);

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
      cell = document.getElementById(i * 9 + j);
      if (!have_set_editable) {
        if (current_board[i][j][1]) {
          cell.classList.add("editable");
        } else {
          cell.classList.add("uneditable");
        }
      }
      cell.innerHTML = "<p>" + current_board[i][j][0] + "</p>";
    }
  }
};

const modifyBoard = async (cell, value) => {
  if (cell.classList.contains("editable")) {
    const r = await fetch("/api/modify_board", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify([parseInt(cell.id, 10), value]),
    });
  }
};
