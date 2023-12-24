document.getElementById('date').innerHTML = new Date().toDateString();

const button_1 = document.getElementById('button_1')

button_1.addEventListener("click", backToRed);


function backToRed() {
    document.body.style.background = 'red';
    button_1.removeEventListener("click", backToRed);
    button_1.addEventListener("click", backToTan); 
 }
 function backToTan() {
    document.body.style.background = '#f0e8c5';
    button_1.removeEventListener("click", backToTan);
    button_1.addEventListener("click", backToRed);
 }
 
 function makeButton() {
    const new_button = document.createElement('button')
    document.body.appendChild(new_button)
 }

 function test() {
    alert ("Test Event");
 }

 document.addEventListener('keydown', function(event) {
   if (event.code == 'KeyZ') {
     alert('Undo!')
   }
 });

var connection_status = document.getElementById("connection_status")  

function manage_websocket(websocket) {
   websocket.onopen = function(event) {
      alert("Connection Established");
      connection_status.style.backgroundColor = "green"
    };

    websocket.onclose = function(event) {
      // alert("Connection Lost");
      connection_status.style.color = "red"
      connection_status.innerHTML = "Connection Lost"
    };
}

 function sendKeys(websocket) {
   document.addEventListener('keydown', function(event) {
      if (event.code == 'KeyA') {
         const event = {
            key: "a_down",
         };
         websocket.send(JSON.stringify(event));
      }
   });
}
 

 window.addEventListener("DOMContentLoaded", () => {
   const websocket = new WebSocket("ws://localhost:8765/");
   manage_websocket(websocket)
   sendKeys(websocket)
 });