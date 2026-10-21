
let usuarios = [];

// ENVIAR DATOS A PYTHON
async function enviar(ruta, datos) {
    const respuesta = await fetch(ruta, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(datos)
    });

    const resultado = await respuesta.json();

    if (!respuesta.ok) {
        throw new Error(resultado.error || "Ocurrió un error");
    }

    return resultado;
}

// OBTENER DATOS DEL FORMULARIO
function obtenerDatos() {
    return {
        usuario: document.getElementById("usuario").value,
        nombre: document.getElementById("nombre").value,
        direccion: document.getElementById("direccion").value,
        telefono: document.getElementById("telefono").value
    };
}

// REGISTRAR DESDE REGISTRO.HTML
const formRegistro = document.getElementById("formRegistro");

if (formRegistro) {
    formRegistro.addEventListener("submit", async function(e) {
        e.preventDefault();

        const datos = obtenerDatos();
        datos.clave = document.getElementById("clave").value;

        try {
            const resultado = await enviar("/registrar", datos);
            alert(resultado.mensaje);
            window.location.href = "/";
        } catch (error) {
            document.getElementById("mensaje").textContent = error.message;
        }
    });
}

// INICIO DE SESIÓN
const formLogin = document.getElementById("formLogin");

if (formLogin) {
    formLogin.addEventListener("submit", async function(e) {
        e.preventDefault();

        const datos = {
            usuario: document.getElementById("usuario").value,
            clave: document.getElementById("clave").value
        };

        try {
            const resultado = await enviar("/login", datos);

            if (resultado.acceso) {
                window.location.href = "/index.html";
            } else {
                document.getElementById("mensaje").textContent =
                    "Usuario o contraseña incorrectos";
            }
        } catch (error) {
            document.getElementById("mensaje").textContent = error.message;
        }
    });
}

// GUARDAR Y EDITAR USUARIOS
const formUsuario = document.getElementById("formUsuario");

if (formUsuario) {
    formUsuario.addEventListener("submit", async function(e) {
        e.preventDefault();

        const datos = obtenerDatos();
        const id = document.getElementById("idUsuario").value;

        try {
            let resultado;

            if (id) {
                datos.idUsuario = id;
                resultado = await enviar("/editar", datos);
            } else {
                datos.clave = document.getElementById("clave").value;

                if (!datos.clave) {
                    alert("Ingresa una contraseña");
                    return;
                }

                resultado = await enviar("/registrar", datos);
            }

            alert(resultado.mensaje);
            limpiar();
            cargarUsuarios();

        } catch (error) {
            alert(error.message);
        }
    });

    cargarUsuarios();
}

// CONSULTAR USUARIOS
async function cargarUsuarios() {
    try {
        const respuesta = await fetch("/buscar");

        if (!respuesta.ok) {
            throw new Error("No se pudo consultar");
        }

        usuarios = await respuesta.json();
        mostrarUsuarios(usuarios);

    } catch (error) {
        alert(error.message);
    }
}

// MOSTRAR USUARIOS EN LA TABLA
function mostrarUsuarios(lista) {
    const tabla = document.getElementById("listaUsuarios");
    tabla.innerHTML = "";

    lista.forEach(function(u) {
        const fila = document.createElement("tr");

        [
            u.idUsuario,
            u.usuario,
            u.nombre,
            u.direccion,
            u.telefono
        ].forEach(function(valor) {
            const celda = document.createElement("td");
            celda.textContent = valor;
            fila.appendChild(celda);
        });

        const acciones = document.createElement("td");

        const botonEditar = document.createElement("button");
        botonEditar.textContent = "Editar";
        botonEditar.onclick = () => editarUsuario(u.idUsuario);

        const botonEliminar = document.createElement("button");
        botonEliminar.textContent = "Eliminar";
        botonEliminar.className = "eliminar";
        botonEliminar.onclick = () => eliminarUsuario(u.idUsuario);

        acciones.appendChild(botonEditar);
        acciones.appendChild(botonEliminar);

        fila.appendChild(acciones);
        tabla.appendChild(fila);
    });
}

// BUSCAR USUARIOS POR NOMBRE
function filtrarUsuarios() {
    const texto = document.getElementById("filtro").value.toLowerCase();

    const filtrados = usuarios.filter(u =>
        u.usuario.toLowerCase().includes(texto) ||
        u.nombre.toLowerCase().includes(texto)
    );

    mostrarUsuarios(filtrados);
}

// EDITAR USUARIO
function editarUsuario(id) {
    const u = usuarios.find(x => x.idUsuario === id);

    if (!u) return;

    document.getElementById("idUsuario").value = u.idUsuario;
    document.getElementById("usuario").value = u.usuario;
    document.getElementById("nombre").value = u.nombre;
    document.getElementById("direccion").value = u.direccion;
    document.getElementById("telefono").value = u.telefono;

    window.scrollTo(0, 0);
}

// ELIMINAR USUARIO
async function eliminarUsuario(id) {
    if (!confirm("¿Deseas eliminar este usuario?")) {
        return;
    }

    try {
        const resultado = await enviar("/eliminar", {
            idUsuario: id
        });

        alert(resultado.mensaje);
        cargarUsuarios();

    } catch (error) {
        alert(error.message);
    }
}

// LIMPIAR FORMULARIO
function limpiar() {
    document.getElementById("formUsuario").reset();
    document.getElementById("idUsuario").value = "";
}
