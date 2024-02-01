// Establece el id para cada pregunta
if (document.getElementById("contenedor-preguntas")) {
    let numero_pregunta = 1;
    document.querySelectorAll("h3.accordion-header").forEach(item => {
        boton = item.firstElementChild;
        boton.setAttribute("data-bs-target", `#pregunta${numero_pregunta}`);
        boton.setAttribute("aria-controls", `pregunta${numero_pregunta}`);

        item.nextElementSibling.setAttribute("id", `pregunta${numero_pregunta}`);
        ++numero_pregunta
    });
}
