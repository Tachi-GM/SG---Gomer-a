function toggleDetalle(fila) {
    const filaDetalle = fila.nextElementSibling;
    filaDetalle.classList.toggle('d-none');
}

function cambiarEstado(select, idTrabajo) {
    const nuevoEstado = select.value;

    fetch('/actualizar-estado', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `id_trabajo=${idTrabajo}&estado=${encodeURIComponent(nuevoEstado)}`
    })
    .then(respuesta => {
        if (!respuesta.ok) throw new Error('No se pudo actualizar');
        // Repintamos el color del select según el nuevo estado
        select.classList.remove('select-pendiente', 'select-proceso', 'select-pagado');
        if (nuevoEstado === 'PENDIENTE') select.classList.add('select-pendiente');
        else if (nuevoEstado === 'EN PROCESO') select.classList.add('select-proceso');
        else select.classList.add('select-pagado');
    })
    .catch(err => {
        alert('Hubo un error al actualizar el estado. Probá de nuevo.');
        console.error(err);
    });
}