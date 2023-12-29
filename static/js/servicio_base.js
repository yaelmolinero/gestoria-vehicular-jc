// Fuera de las paginas principales de cada estado no hay sección de contacto, ni nosotros
// Este es un pequeño script para cambiar el url de "Nosotros" y "Contacto" en la barra de navegación.
document.querySelector("#nosotros").href = "http://127.0.0.1:5000/nosotros";
document.querySelector("#contacto-nav").href = "http://127.0.0.1:5000/#contacto";

// Establece el id para cada pregunta
if (document.getElementById("contenedor-preguntas")) {
    let numero_pregunta = 1;
    document.querySelectorAll("h2.accordion-header").forEach(item => {
        boton = item.firstElementChild;
        boton.setAttribute("data-bs-target", `#pregunta${numero_pregunta}`);
        boton.setAttribute("aria-controls", `pregunta${numero_pregunta}`);

        item.nextElementSibling.setAttribute("id", `pregunta${numero_pregunta}`);
        ++numero_pregunta
    });
}
