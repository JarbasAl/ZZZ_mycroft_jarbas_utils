process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0"
const WebSocket = require('ws');
const utf8 = require('utf8');
const url = require('url');
const util = require('util');
var source = "";
var platform = "";
var username = "";
console.log('opening web socket');
const ws = new WebSocket('wss://<USERNAME>:<KEY>@<URL>:<PORT>');

ws.on('connection', function connection(ws, req){
     console.log("connection established");
});

ws.on('open', function open() {
  
   message = "Hello World";
     //console.log(util.inspect(ws,false,null));
   msg = {"data": {"utterances": [message], "lang": "en-us"},
                   "type": "recognizer_loop:utterance",
                   "context": {"destinatary":
                       "jarbas_server", "platform": "javascript", "user": username}}
   ws.send(JSON.stringify(msg));
});

ws.on('message', function incoming(data) {
  response = JSON.parse(data);
  if(response.type == "speak" )
  {
      source = response.context.destinatary;
      platform = response.context.platform;
      username = response.context.username;
      console.log("source: " + source + " platform: " + platform + " username: " + username);
      utterance = response.data.utterance;
      console.log("Response: " + utterance)
       //ws.send(JSON.stringify(msg));
   
  }
  //console.log(data);
});
