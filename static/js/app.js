var socket = io.connect();

$(document).ready(function () {
  //receive details from server
  socket.on("updateSensorData", function (msg) {
    console.log("Received sensorData :: " + msg.date + " :: " + msg.object);
    if (msg.object != "Unknown") {
      $("#greating").removeClass("text-danger")
      $("#greating").addClass("text-success")
      $("#greating").text("Selamat datang " + msg.object);
    }else{
      $("#greating").removeClass("text-success")
      $("#greating").addClass("text-danger")
      $("#greating").text("Anda belum ada pada system");
    }
  });
  socket.on("updateSensorDataEmpty", function (msg) {
    console.log("Received updateSensorDataEmpty :: " + msg.date );
      $("#greating").text("");
  });
});
