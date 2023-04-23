//import * as openai from "./node_modules/openai";

const speechResult = document.querySelector("#speech_result");

speechResult.insertAdjacentHTML(
  "afterend",
  `
    <button type="button" id="start-record">
        Start Record
    </button>
    <button type="button" id="stop-record">
        Stop Record
    </button>
`
);

const startRecordButton = document.querySelector("#start-record");
const stopRecordButton = document.querySelector("#stop-record");

let recognition = null;

startRecordButton.onclick = startSpeechRecognition;
stopRecordButton.onclick = endSpeechRecognition;

// ChatGPT API 키
const API_KEY = "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";

// API 호출 URL
const API_URL = "https://api.openai.com/v1/chat/completions";

// 요청 헤더
const headers = {
  "Content-Type": "application/json",
  Authorization: `Bearer ${API_KEY}`,
};

function checkCompatibility() {
  recognition = new (window.SpeechRecognition ||
    window.webkitSpeechRecognition)();
  recognition.lang = "ko";
  recognition.maxAlternatives = 5;

  if (!recognition) {
    alert("You cannot use speech api.");
  }
}

function startSpeechRecognition() {
  console.log("Start");

  checkCompatibility();

  recognition.addEventListener("speechStart", () => {
    console.log("Speech Start");
  });

  recognition.addEventListener("speechend", () => {
    console.log("Speech End");
  });

  recognition.addEventListener("result", async (event) => {
    const text = event.results[0][0].transcript;
    console.log("Speech Result", event.results);

    speechResult.innerHTML = text;

    const response = await getGPTResponse(text);
    console.log(response);
    //   document.getElementById("speech_result").value = text;
  });

  recognition.start();
}

function endSpeechRecognition() {
  recognition.stop();
}

async function getGPTResponse(prompt) {
  const question = `"간단한 자기소개를 해주십시오." 라는 질문에 대한 답변인 "${prompt}"에 대해 네가 면접관이라고 생각하고 0점~10점 중 하나의 점수를 매기고 그 이유를 상세하게 설명해줘`;

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: headers,
      body: JSON.stringify({
        model: "gpt-3.5-turbo",
        messages: [{ role: "user", content: question }],
      }),
    });

    const data = await response.json();

    document.querySelector("#gpt-response").innerHTML =
      data.choices[0].message.content.replaceAll(".", "<br/>");

    return data;
  } catch {
    return "Sorry, I could not generate a response at this time.";
  }
}
