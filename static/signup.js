const firstname = document.getElementById("firstname");
const lastname = document.getElementById("lastname");
const email = document.getElementById("email");
const username = document.getElementById("username");
const password = document.getElementById("password");

const submit = document.getElementById("submit");
submit.disabled = true;
pictureContainer.style.display = "none";

const conditionsList = [firstname, lastname, email, username, password];

function allLoaded()
{
    let enabled = true;
    conditionsList.forEach(condition =>
    {
        if (condition.value.trim() === "") 
        {
        enabled = false; 
        }
    }
    )
    submit.disabled = !enabled;
}


conditionsList.forEach(condition => 
{
    condition.addEventListener("change", allLoaded);
});