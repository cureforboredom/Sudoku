document.body.onload = init;

current_board_hash = "";

current_board = [];

have_set_editable = false;

selected_cell = null;

intervalID = null;

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
      cell.onclick = cellClicked;

      row.append(cell);
    }

    dom_board.append(row);
  }

  document.getElementById("picker-closer").onclick = function () {
    document.getElementById("picker-container").style.display = "none";
    selected_cell.classList.remove("selected");
  };

  picker = document.getElementById("picker");

  for (let i = 0; i < 3; i++) {
    row = document.createElement("div");
    row.classList.add("picker-row");
    for (let j = 0; j < 3; j++) {
      cell = document.createElement("div");
      cell.id = i * 3 + j + 1;
      cell.classList.add("choice");
      cell.innerHTML = "<p>" + (i * 3 + j + 1) + "</p>";
      cell.onclick = choose;
      row.append(cell);
    }
    picker.append(row);
  }

  clear = document.createElement("div");
  clear.id = "clear";
  clear.innerHTML = "<p>Clear</p>";
  clear.onclick = choose;

  picker.append(clear);

  intervalID = window.setInterval(update, 1000);
}

function choose() {
  if (this.id == "clear") {
    modifyBoard(selected_cell, 0);
  } else {
    modifyBoard(selected_cell, this.id);
  }
  document.getElementById("picker-container").style.display = "none";
  selected_cell.classList.remove("selected");
  highlight("none");
}

function win() {
  window.clearInterval(intervalID);
  alert("you win!");
}

function highlight(n) {
  divs = document.getElementsByClassName("cell");
  for (let i = 0; i < divs.length; i++) {
    value = divs[i].innerHTML;
    if (value.includes(n) && !value.includes("0")) {
      divs[i].classList.add("highlighted");
    } else {
      divs[i].classList.remove("highlighted");
    }
  }
}

function cellClicked() {
  highlight(this.innerHTML);
  if (this.classList.contains("editable")) {
    document.getElementById("picker-container").style.display = "flex";
    selected_cell = this;
    this.classList.add("selected");
  }
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
  board = document.getElementById("board");
  if (!board.innerHTML.includes("<p>0</p>")) {
    const r = await fetch("/api/check_board");
    if ((await r.text()) == "True") {
      win();
    }
  } else {
    await fetchBoard();
    for (let i = 0; i < 9; i++) {
      for (let j = 0; j < 9; j++) {
        cell = document.getElementById(i * 9 + j);
        if (current_board[i][j][1]) {
          cell.classList.remove("uneditable");
          cell.classList.add("editable");
        } else {
          cell.classList.remove("editable");
          cell.classList.add("uneditable");
        }
        cell.innerHTML = "<p>" + current_board[i][j][0] + "</p>";
      }
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

    response = await r.json();
    key = Object.keys(response)[0];
    if (key != "valid") {
      cells = response[key];
      for (let i = 0; i < 9; i++) {
        function change_color(color) {
          document.getElementById(cells[i]).style.borderColor = color;
        }
        change_color("#99312d");
        setTimeout(function () {
          change_color("#303436");
        }, 300);
        setTimeout(function () {
          change_color("#99312d");
        }, 600);
        setTimeout(function () {
          change_color("#303436");
        }, 900);
        setTimeout(function () {
          change_color("#99312d");
        }, 1200);
        setTimeout(function () {
          change_color("#303436");
        }, 1500);
      }
    }
  }
};
