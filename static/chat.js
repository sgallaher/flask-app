const socket = io();
const username = prompt("Enter your name:");
const room = document.getElementById("chat-box").dataset.token;

socket.emit("join", { room, username });

socket.on("message", data => {
  const chatBox = document.getElementById("chat-box");
  chatBox.innerHTML += `<p><strong>${data.username || "System"}:</strong> ${data.msg}</p>`;
});

function sendMessage() {
  const msg = document.getElementById("message").value;
  socket.emit("message", { msg, room, username });
  document.getElementById("message").value = "";
}
