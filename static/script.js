document.addEventListener("DOMContentLoaded", function () {

    const askBtn = document.getElementById("askBtn");
    const questionInput = document.getElementById("question");
    const answerDiv = document.getElementById("answer");

    askBtn.addEventListener("click", askBot);

    async function askBot() {
        const question = questionInput.value.trim();

        if (question === "") {
            answerDiv.innerText = "⚠ Please enter a question.";
            return;
        }

        answerDiv.innerText = "⏳ Thinking...";

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: question })
            });

            const data = await response.json();
            answerDiv.innerText = "🤖 " + data.response;

        } catch (error) {
            answerDiv.innerText = "❌ Error connecting to server.";
            console.error("Error:", error);
        }
    }

});
