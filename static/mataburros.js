function agregarFilaTarea() {
    const contenedor = document.getElementById('contenedor-tareas');
    const primerFila = contenedor.querySelector('.fila-tarea');
    
    const nuevaFila = primerFila.cloneNode(true);
    nuevaFila.querySelector('select').selectedIndex = 0;
    
    // 1️⃣ PRIMERO insertamos la fila en la página
    contenedor.appendChild(nuevaFila);
    
    // 2️⃣ RECIÉN AHORA tocamos su valor, cuando ya está "conectada" y visible
    const inputCantidad = nuevaFila.querySelector('.input-cantidad');
    inputCantidad.value = 1;
    
    calcularTotal();
}

function quitarFilaTarea() {
    const contenedor = document.getElementById('contenedor-tareas');
    const filas = contenedor.querySelectorAll('.fila-tarea');
    if (filas.length > 1) {
        contenedor.removeChild(filas[filas.length - 1]);
    }

    calcularTotal();
}

function cambiarLista(numeroLista) {
    document.getElementById('tipo_lista').value = numeroLista;
    const contenedor = document.querySelectorAll('#contenedor-tareas select');
    for (let select of contenedor) {
        for (let opcion of select.options) {
            const precio1 = opcion.getAttribute('data-precio1');
            const precio2 = opcion.getAttribute('data-precio2');
            const precio3 = opcion.getAttribute('data-precio3');
            const nombre = opcion.getAttribute('data-nombre');
            if (numeroLista === 1) {
                opcion.textContent = `${nombre} — $${parseFloat(precio1).toFixed(2)}`;
            } else if (numeroLista === 2) {
                opcion.textContent = `${nombre} — $${parseFloat(precio2).toFixed(2)}`;
            } else if (numeroLista === 3) {
                opcion.textContent = `${nombre} — $${parseFloat(precio3).toFixed(2)}`;
            }
            if (opcion.value === "") {
                opcion.textContent = "Selecciona una tarea realizada...";
            }
        }
    }
    // 1. A todos los botones de lista les quitamos el azul relleno y les ponemos el borde
    document.querySelectorAll('.btn-lista').forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-primary');
    });
    // 2. Al botón presionado le ponemos el azul relleno
    const botonActivo = document.getElementById(`btn-l${numeroLista}`);
    botonActivo.classList.remove('btn-outline-primary');
    botonActivo.classList.add('btn-primary');

    calcularTotal();
}

function modificarCantidad(boton, cambio) {
    // Buscamos el input de cantidad que está al lado de este botón
    const input = boton.parentElement.querySelector('.input-cantidad');
    let valorActual = parseInt(input.value) || 1;
    let nuevoValor = valorActual + cambio;
    
    // Evitamos que baje de 1
    if (nuevoValor >= 1) {
        input.value = nuevoValor;
    }
    calcularTotal();
}

function calcularTotal() {
    const filas = document.querySelectorAll('#contenedor-tareas .fila-tarea');
    const listaActual = document.getElementById('tipo_lista').value; // "1", "2" o "3"
    let total = 0;

    filas.forEach(fila => {
        const select = fila.querySelector('select');
        const cantidadInput = fila.querySelector('.input-cantidad');
        const opcionSeleccionada = select.options[select.selectedIndex];

        const precio = parseFloat(opcionSeleccionada.getAttribute(`data-precio${listaActual}`)) || 0;
        const cantidad = parseInt(cantidadInput.value) || 0;

        total += precio * cantidad;
    });

    document.getElementById('total-parcial').textContent =
        `$${total.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

document.getElementById('contenedor-tareas').addEventListener('change', function(e) {
if (e.target.tagName === 'SELECT') {
    calcularTotal();
}
});