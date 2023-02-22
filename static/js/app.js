var socket = io.connect();

$(document).ready(function () {
  //receive details from server
  socket.on("updateSensorData", function (msg) {
    console.log("Received sensorData :: " + msg.date + " :: " + msg.object);
    if (msg.object != "Unknown") {
      $("#greeting").removeClass("text-danger");
      $("#greeting").addClass("text-success");
      $("#greeting").text("Welcome");
      $("#name-person").text(msg.object);
    } else {
      $("#greeting").removeClass("text-success");
      $("#greeting").addClass("text-danger");
      $("#greeting").text("Your face is not recognize");
      $("#name-person").text("-");

    }
  });
  socket.on("updateSensorDataEmpty", function (msg) {
    console.log("Received updateSensorDataEmpty :: " + msg.date);
    $("#greeting").text("");
  });

  n = new Date();
  y = n.getFullYear();
  m = n.getMonth() + 1;
  d = n.getDate();
  document.getElementById("date").innerHTML = m + "/" + d + "/" + y;

});
