<!doctype html>
<html>
  <head>
    <title>شهد وعدي - Chat App</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/2.3.0/socket.io.js"></script>
    <style>
      body {
        background: url('images/heart.jpg') no-repeat center center fixed;
        background-size: cover;
        color: #fff;
        font-family: Arial, sans-serif;
        min-height: 100vh;
        margin: 0;
        padding: 0;
      }
      body::before {
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(32, 32, 32, 0.08); /* very light overlay for clarity */
        z-index: 0;
        pointer-events: none;
      }
      h2 {
        color: #fff;
        position: relative;
        z-index: 2;
      }
      #messages {
        background: rgba(0,0,0,0.10);
        padding: 10px;
        border-radius: 8px;
        height: 300px;
        overflow-y: auto;
        margin-bottom: 10px;
        list-style: none;
        position: relative;
        z-index: 2;
      }
      input, button {
        padding: 8px;
        border-radius: 4px;
        border: none;
        margin-top: 10px;
      }
      button {
        background: #15660a;
        color: #fff;
        cursor: pointer;
        margin-left: 5px;
      }
      input {
        width: 70%;
      }
      .chat-container {
        position: relative;
        z-index: 1;
        max-width: 440px;
        margin: 8vh auto;
        background: rgba(0,0,0,0.12); /* subtle card background for readability */
        border-radius: 18px;
        padding: 2rem 1.5rem 1.5rem 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(31,38,135,0.18);
        overflow: hidden;
        text-align: center;
      }
      .food-photo {
        display: block;
        margin: 0 auto 20px auto;
        max-width: 350px;
        width: 85%;
        border-radius: 18px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.20);
        border: 4px solid #fff;
        background: #eee;
        position: relative;
        z-index: 2;
        image-rendering: auto; /* Let browser choose best quality */
      }
      @media (max-width: 480px) {
        .chat-container {
          max-width: 98vw;
          padding: 1rem 2vw;
        }
        .food-photo {
          max-width: 98vw;
          width: 98vw;
        }
      }
    </style>
  </head>
  <body>
    <div class="chat-container">
      <!-- Large, crisp food photo with frame -->
      <img src="images/food.jpg" alt="Food Photo" class="food-photo" loading="eager" />
      <h2>!اهلا بكم في دردشة شهد وعدي</h2>
      <ul id="messages"></ul>
      <input id="myMessage" autocomplete="off" placeholder="اكتب رسالتك..." />
      <button onclick="sendMessage()">إرسال</button>
    </div>
    <script type="text/javascript">
      var socket = io();
      socket.on('message', function(msg) {
        var item = document.createElement('li');
        item.textContent = msg;
        document.getElementById('messages').appendChild(item);
        window.scrollTo(0, document.body.scrollHeight);
      });
      function sendMessage() {
        var input = document.getElementById("myMessage");
        socket.send(input.value);
        input.value = "";
      }
      document.getElementById("myMessage").addEventListener("keyup", function(event) {
        if (event.key === "Enter") sendMessage();
      });
    </script>
  </body>
</html>
