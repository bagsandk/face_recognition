var socket = io.connect();
var modalClose = 5;
let speakData = new SpeechSynthesisUtterance();

$(document).ready(function () {
  var date = "00";
  var date1 = "00";
  var date2 = "00";
  var waiting = 0;
  socket.on("updateSensorData", function (msg) {
    if (msg.object != "Unknown") {
      if (msg.date != date) {
        if (waiting == 0) {
          waiting = modalClose + 1;
          $("#greeting").removeClass("text-danger");
          $("#greeting").addClass("text-success");
          $("#greeting").text("Welcome");
          $("#name-person").text(msg.object);
          var contnt = `<tr>
        <td><img id="wajah" src="data:image/png;base64,${msg.img}"
        style="width:50px; height:50px;" class="rounded-circle"></td>
        <td class="m-0 mt-1 text-center">${msg.object}</td>
        <td class="m-0 mt-1 text-end ">${msg.date}</td>
        </tr>`;

          $("#content-modal").html(`<div class="col-md-8">
        <img class="img-fluid"
            src="data:image/png;base64,${msg.img2}" />
    </div>
    <div class="col-md-4 d-flex flex-column justify-content-between">
            <h6 class="text mt-5">Welcome</h6>
            <h2 class="fw-bold" id="name-person">${msg.object}</h2>
            <p class="fs-7">${msg.date}</p>
    </div>`);

          if ("speechSynthesis" in window) {
            let voices = getVoices();
            let rate = 1,
              pitch = 2,
              volume = 1;
            let text = `Welcome ${msg.object}`;
            // setTimeout(() => {
              // speak(text, voices[5], rate, pitch, volume);
            // }, 1000);
          } else {
            console.log(" Speech Synthesis Not Supported 😞");
          }

          $("#faceModal").modal("show");
          $("#table-history").prepend(contnt);
          setTimeout(() => {
            $("#faceModal").modal("hide");
          }, modalClose * 1000);
        } else {
          waiting = waiting - 1;
        }
      }
    } else {
      $("#greeting").removeClass("text-success");
      $("#greeting").addClass("text-danger");
      $("#greeting").text("Your face is not recognize");
      $("#name-person").text("-");
      $("#faceModal").modal("hide");
    }
    date = msg.date;
  });
  socket.on("updateSensorDataEmpty", function (msg) {
    if (msg.date != date1) {
      $("#greeting").text("Please show your face");
      $("#name-person").text("-");
    }
    date1 = msg.date;
  });
  socket.on("updateSensorDataDevice", function (msg) {
    if (msg.date != date2) {
      $("#memory").text(`${msg.memory} MiB`);
      $("#cpu").text(`${msg.cpu}%`);
      $("#fps").text(`${msg.fps}`);
    }
    date2 = msg.date;
  });

  n = new Date();
  y = n.getFullYear();
  m = n.getMonth() + 1;
  d = n.getDate();
  document.getElementById("date").innerHTML = m + "/" + d + "/" + y;
});

function speak(text, voice, rate, pitch, volume) {
  // create a SpeechSynthesisUtterance to configure the how text to be spoken
  speakData.volume = volume; // From 0 to 1
  speakData.rate = rate; // From 0.1 to 10
  speakData.pitch = pitch; // From 0 to 2
  speakData.text = text;
  speakData.lang = "en";
  speakData.voice = voice;

  // pass the SpeechSynthesisUtterance to speechSynthesis.speak to start speaking
  speechSynthesis.speak(speakData);
}

function getVoices() {
  let voices = speechSynthesis.getVoices();
  if (!voices.length) {
    // some time the voice will not be initialized so we can call spaek with empty string
    // this will initialize the voices
    let utterance = new SpeechSynthesisUtterance("");
    speechSynthesis.speak(utterance);
    voices = speechSynthesis.getVoices();
  }
  return voices;
}
