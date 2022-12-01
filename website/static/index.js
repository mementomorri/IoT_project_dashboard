function deleteThermostat(serial_num) {
  fetch("/delete-thermostat", {
    method: "POST",
    body: JSON.stringify({ serial_num: serial_num }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function incrementSetpoint(serial_num) {
  fetch("/increment-setpoint", {
    method: "POST",
    body: JSON.stringify({ serial_num: serial_num }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function decrementSetpoint(serial_num) {
  fetch("/decrement-setpoint", {
    method: "POST",
    body: JSON.stringify({ serial_num: serial_num }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function incrementBrightness(serial_num) {
  fetch("/increment-brightness", {
    method: "POST",
    body: JSON.stringify({ serial_num: serial_num }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function decrementBrightness(serial_num) {
  fetch("/decrement-brightness", {
    method: "POST",
    body: JSON.stringify({ serial_num: serial_num }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function switchPower(serial_num) {
  fetch("/switch-power", {
    method: "POST",
    body: JSON.stringify({ serial_num: serial_num }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function switchWifi(serial_num) {
  fetch("/switch-wifi", {
    method: "POST",
    body: JSON.stringify({ serial_num: serial_num }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function switchMode(serial_num) {
  fetch("/switch-mode", {
    method: "POST",
    body: JSON.stringify({ serial_num: serial_num }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function switchLock(serial_num) {
  fetch("/switch-lock", {
    method: "POST",
    body: JSON.stringify({ serial_num: serial_num }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function switchRelay(serial_num) {
  fetch("/switch-relay", {
    method: "POST",
    body: JSON.stringify({ serial_num: serial_num }),
  }).then((_res) => {
    window.location.href = "/";
  });
}
