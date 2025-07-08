let currentTopicIndex = 0;
    let topics = [];
    let jobDescription = "AI/ML development, focusing on LLMs, LangChain, or Agentic AI.Strong proficiency in Python and AI frameworks like LangChain, Hugging Face, OpenAI, and other LLM APIs.Hands-on experience in NLP, prompt engineering, embeddings, and vector search.Familiarity with multi-agent AI architectures and retrieval-augmented generation (RAG).Experience with database systems (SQL, NoSQL, or vector databases like Pinecone, ChromaDB, or FAISS).Strong problem-solving and analytical skills.Understanding of API development and integration with backend systems.";

    function startInterview() {
      // jobDescription = document.getElementById("jd").value;
      document.getElementById("feedback").innerText = "";
      document.getElementById("feedback").style.backgroundColor = "transparent";

      fetch("/interview/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jd: jobDescription }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.topics && data.topics.length > 0) {
            topics = data.topics;
            askNextQuestion();
          } else {
            speak("No skills found in job description.");
          }
        });
    }

    function askNextQuestion() {
      if (currentTopicIndex >= topics.length) {
        speak("Interview complete. Great job!");
        document.getElementById("question").innerText = "Interview finished.";
        document.getElementById("wave").style.display = "none";
        return;
      }

      const topic = topics[currentTopicIndex];

      fetch("/interview/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: topic }),
      })
        .then((res) => res.json())
        .then((data) => {
          document.getElementById("question").innerText = data.question;
          speak(data.question);
        });
    }

    function recordAnswer() {
      const recognition = new (window.SpeechRecognition ||
        window.webkitSpeechRecognition)();
      recognition.lang = "en-US";
      recognition.start();
      document.getElementById("wave").style.display = "flex";

      recognition.onresult = function (event) {
        document.getElementById("wave").style.display = "none";

        const response = event.results[0][0].transcript;
        const topic = topics[currentTopicIndex];

        fetch("/interview/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ response: response, topic: topic }),
        })
          .then((res) => res.json())
          .then((data) => {
            document.getElementById("feedback").innerText = data.feedback;
            document.getElementById("feedback").style.backgroundColor = "#d1f2eb";
            speak(data.feedback);
            currentTopicIndex += 1;
            setTimeout(() => {
              askNextQuestion();
            }, 3000);
          });
      };

      recognition.onerror = function () {
        document.getElementById("wave").style.display = "none";
      };
    }

    function speak(text) {
      const synth = window.speechSynthesis;
      const utterance = new SpeechSynthesisUtterance(text);
      synth.speak(utterance);
    }

    window.onload = function () {
      const video = document.getElementById("camera-stream");
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices
          .getUserMedia({ video: true })
          .then((stream) => {
            video.srcObject = stream;
          })
          .catch((err) => {
            console.warn("Camera access denied or not available:", err);
          });
      }
    };