async function askThanatos(question) {
  const res = await fetch("/api/thanatos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });

  const data = await res.json();
  console.log(data.answer || data.error);
  document.getElementById("answer").innerText = data.answer || data.error;
}

document.getElementById("askButton").addEventListener("click", () => {
    const question = document.getElementById("queryInput").value.trim();
    if(question){
        askThanatos(question);
    }
});