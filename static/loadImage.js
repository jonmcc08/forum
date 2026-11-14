const pictureContainer = document.getElementById("picture-container")
const file = document.getElementById("picture");
const imagefile = document.getElementById("uploaded-file");

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
file.addEventListener("change", loadImage);