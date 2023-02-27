var socket = io.connect();

$(document).ready(function () {
  //receive details from server
  socket.on("updateSensorData", function (msg) {
    console.log("Received sensorData :: " + msg.date + " :: " + msg.img);
    if (msg.object != "Unknown") {
      $("#greeting").removeClass("text-danger");
      $("#greeting").addClass("text-success");
      $("#greeting").text("Welcome");
      $("#name-person").text(msg.object);
      var contnt = `<tr>
      <td><img id="wajah" src="data:image/png;base64,${msg.img}"
              style="width:50px; height:50px;" class="rounded-circle"></td>
      <td class="m-0 mt-1 text-center">${msg.object}</td>
      <td class="m-0 mt-1 text-end ">${msg.date}</td>
  </tr>`

      $("#table-history").prepend(contnt);
    } else {
      $("#greeting").removeClass("text-success");
      $("#greeting").addClass("text-danger");
      $("#greeting").text("Your face is not recognize");
      $("#name-person").text("-");
    }
  });
  socket.on("updateSensorDataEmpty", function (msg) {
    console.log("Received updateSensorDataEmpty :: " + msg.date);
    $("#greeting").text("Welcome");
    $("#name-person").text("-");

  });

  socket.on("updateSensorDataDevice", function (msg) {
    console.log("Received updateSensorDataDevice :: " + msg.date);
    $("#memory").text(`${msg.memory} MiB`);
    $("#cpu").text(`${msg.cpu}%`);
    $("#fps").text(`${msg.fps}`);
  });

  n = new Date();
  y = n.getFullYear();
  m = n.getMonth() + 1;
  d = n.getDate();
  document.getElementById("date").innerHTML = m + "/" + d + "/" + y;
});

function _arrayBufferToBase64(buffer) {
  var binary = "";
  var bytes = new Uint8Array(buffer);
  var len = bytes.byteLength;
  for (var i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}
