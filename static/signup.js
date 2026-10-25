const firstname = document.getElementById("firstname");
const lastname = document.getElementById("lastname");
const email = document.getElementById("email");
const username = document.getElementById("username");
const password = document.getElementById("password");

const file = document.getElementById("picture");
const imagefile = document.getElementById("uploaded-file");
const pictureContainer = document.getElementById("picture-container")

const submit = document.getElementById("submit");
submit.disabled = true;

const conditionsList = [firstname, lastname, email, username, password];
pictureContainer.style.display = "none";

function loadImage(e) 
{
    console.log(e)
    /** @type {File} */
    const image = e.target.files[0];
    
    console.log(image);
    console.log("Fixed");
    
    if (image) 
    {
        const imageurl = URL.createObjectURL(image);
        imagefile.src = imageurl;
        pictureContainer.style.display = "block";
    } 
    else 
    {
        pictureContainer.style.display = "none";
    };
}

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

file.addEventListener("change", loadImage);