var iconCode = "icon-code";

document.querySelector("#icon").addEventListener('keyup', function() {
    let elemento = document.querySelector("#icono");

    try {
        elemento.classList.remove(iconCode);
        iconCode = "bi-" + this.value;
        elemento.classList.add(iconCode);
    } catch (DOMException) {
        iconCode = "icon-code";
    }
});

// Muestra los caracteres restantes en la descripción
let caracteres = document.createElement("span");
caracteres.textContent = "(Caracteres restantes: 230)";
document.getElementById("descripcion").before(caracteres);

document.getElementById("descripcion").addEventListener("keyup", function() {
    if (this.value.length > 230) return;
    caracteres.textContent = `(Caracteres restantes: ${230 - this.value.length})`;
});

// Edita el nombre de la pregunta.
document.querySelectorAll("button.edit").forEach(element => {
    element.addEventListener("click", () => {
        let parent = element.parentElement;
        let currentElement = parent.firstElementChild;
        element.setAttribute("disabled", "")

        let newInput = document.createElement("input");
        newInput.setAttribute("class", "form-control-plaintext");
        newInput.setAttribute("type", "text");
        newInput.setAttribute("value", currentElement.textContent);

        newInput.addEventListener("keydown", (event) => {
            if (event.keyCode === 13 && event.targe !== document.getElementById("submit")) {
                currentElement.textContent = newInput.value;
                parent.replaceChild(currentElement, newInput);
                document.querySelector(`#pregunta${currentElement.id.split("-")[1]}`).value = newInput.value;
                element.removeAttribute("disabled")
            }
        });

        parent.replaceChild(newInput, currentElement);
        newInput.focus();
    });
});

// Seleccionar las preguntas que quiera llenar
document.querySelectorAll("input.select").forEach(element => {
    element.addEventListener("click", () => {
        element.previousElementSibling.classList.toggle("hide-element");
    });
});
