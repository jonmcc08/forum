let timerHtml = document.getElementById("timer")

for (let i = 3; i > 0; i--)
{
    setTimeout(() => {
        timerHtml.innerHTML = i
    }, (3-i) * 1000) // Fixa
}