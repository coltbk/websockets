
const testSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/test/'
);

// const chatSocket = new WebSocket(
//     'ws://'
//     + window.location.host
//     + '/ws/chat/test/'
// );

    testSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        // alert('message');
    };

    document.addEventListener('keydown', function(event) {
        if (event.code == 'KeyZ') {
        //   alert('Undo!')
        console.log("z was pressed")
        message = "test message"
        testSocket.send(JSON.stringify({
            'message': message
        }))
        }
    });

// document.addEventListener('keydown', function(event) {
// if (event.code == 'KeyZ') {
//     alert('Undo!')
//     message = "test message"
//     chatSocket.send(JSON.stringify({
//     'message': message
// }))
// }
// });
  function sendKeys(websocket) {
    document.addEventListener('keydown', function(event) {
       if (event.code == 'KeyA') {
          const event = {
             key: "a_down",
          };
          console.log("a was pressed")
          websocket.send(JSON.stringify(event));
       }
    });
 }

//  window.addEventListener("DOMContentLoaded", () => {
//     sendKeys(testSocket)
//   });