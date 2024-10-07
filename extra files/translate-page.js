var deleteTextBtn = document.getElementById("delete-text-btn");

deleteTextBtn.addEventListener("click", deleteText);

function deleteText() {
  document.getElementById("text").value = "";
}
