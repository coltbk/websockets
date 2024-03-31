

const testSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/test/'
);

    testSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log(data['message'])
        // alert(data['message']);
    };

// The event object for the onmessage event supports the following properties:

// data - Contains the actual message
// origin - The URL of the document that invoked the event
// lastEventId - the identifier of the last message seen in the event stream

    document.addEventListener('keydown', function(event) {
        if (event.code == 'KeyZ') {
        alert('Undo!')
        message = "key: z"
        console.log("z was pressed")
        testSocket.send(JSON.stringify({
            'message': message
        }))
        }
    });

    document.addEventListener('keydown', function(event) {
       if (event.code == 'KeyA') {
        message = "key: a"
        console.log("a was pressed")
        testSocket.send(JSON.stringify({
            'message': message
        }));
       }
    });

window.addEventListener("DOMContentLoaded", () => {
sendKeys(testSocket)
});