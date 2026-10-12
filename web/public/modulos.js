// ============================================================
// MODULOS 2 y 3
// Cada modulo recibe el texto que escribe el usuario y devuelve el
// resultado como texto. Corre en el navegador, sin servidor.
//
//   id          identificador unico (sin espacios)
//   titulo      nombre que aparece en el menu
//   descripcion una linea que explica el modulo
//   video       URL para incrustar (YouTube "embed", SharePoint, Stream...).
//               Dejalo vacio ("") para mostrar un recuadro "aqui ira el video".
//   entrada     texto de ayuda dentro del cuadro de entrada
//   ejecutar    function (texto) { ...; return "resultado"; }
// ============================================================

const MODULOS = [
  {
    id: 'mod2',
    titulo: 'Módulo 2',
    descripcion: 'Pega el código o texto, y el módulo extrae y acomoda la información.',
    video: '',
    entrada: 'Pega aquí el texto de entrada…',
    ejecutar: function (texto) {
      // TODO: aqui va la logica del modulo 2 (port del Python a JavaScript).
      throw new Error('La lógica de este módulo todavía no está conectada.');
    }
  },
  {
    id: 'mod3',
    titulo: 'Módulo 3',
    descripcion: 'Pega el texto de entrada, y el módulo devuelve el resultado ordenado.',
    video: '',
    entrada: 'Pega aquí el texto de entrada…',
    ejecutar: function (texto) {
      // TODO: aqui va la logica del modulo 3 (port del Python a JavaScript).
      throw new Error('La lógica de este módulo todavía no está conectada.');
    }
  }
];
