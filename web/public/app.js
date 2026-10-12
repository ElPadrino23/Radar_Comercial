(function () {
  'use strict';

  firebase.initializeApp(FIREBASE_CONFIG);
  const auth = firebase.auth();
  const db = firebase.firestore();

  const $ = function (id) { return document.getElementById(id); };
  const sleep = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
  const POLL_MS = typeof POLL_INTERVAL_MS === 'number' ? POLL_INTERVAL_MS : 10000;
  const MAX_ESPERA_MS = 40 * 60 * 1000;

  let registros = [];
  let buscando = false;

  // ------------------------------------------------------------------
  // Login
  // ------------------------------------------------------------------
  function mensajeLogin(err) {
    const codigo = (err && err.code) || '';
    if (codigo === 'auth/too-many-requests') return 'Demasiados intentos. Espera unos minutos.';
    if (codigo === 'auth/network-request-failed') return 'Sin conexión. Revisa tu red.';
    return 'Correo o contraseña incorrectos.';
  }

  $('form-login').addEventListener('submit', function (e) {
    e.preventDefault();
    $('login-error').textContent = '';
    $('btn-entrar').disabled = true;
    auth.signInWithEmailAndPassword($('login-correo').value.trim(), $('login-clave').value)
      .catch(function (err) { $('login-error').textContent = mensajeLogin(err); })
      .then(function () { $('btn-entrar').disabled = false; });
  });

  $('btn-salir').addEventListener('click', function () { auth.signOut(); });

  auth.onAuthStateChanged(function (user) {
    if (user) {
      $('vista-login').hidden = true;
      $('app').hidden = false;
      $('usuario').textContent = user.email || '';
      $('login-clave').value = '';
      cargarResultados();
    } else {
      $('app').hidden = true;
      $('vista-login').hidden = false;
      registros = [];
      $('tabla-body').textContent = '';
      $('zona-resultados').hidden = true;
      setEstado('');
    }
  });

  // ------------------------------------------------------------------
  // Llamadas al Worker (siempre con el token de la sesion)
  // ------------------------------------------------------------------
  async function api(ruta, opciones) {
    opciones = opciones || {};
    const user = auth.currentUser;
    if (!user) throw new Error('Sesión cerrada');
    const token = await user.getIdToken();
    const headers = { Authorization: 'Bearer ' + token };
    if (opciones.body) headers['Content-Type'] = 'application/json';
    return fetch(API_URL + ruta, {
      method: opciones.method || 'GET',
      headers: headers,
      body: opciones.body
    });
  }

  async function errorDeApi(resp) {
    if (resp.status === 401) return 'Tu sesión no es válida. Sal y vuelve a entrar.';
    try {
      const d = await resp.json();
      if (d && d.error) return d.error;
    } catch (e) { /* sin cuerpo JSON */ }
    return 'Error ' + resp.status;
  }

  // ------------------------------------------------------------------
  // Menu y modulos
  // ------------------------------------------------------------------
  function mostrarModulo(id) {
    document.querySelectorAll('.modulo').forEach(function (s) {
      s.hidden = s.dataset.id !== id;
    });
    document.querySelectorAll('#menu button').forEach(function (b) {
      b.setAttribute('aria-selected', String(b.dataset.id === id));
    });
  }

  function construirMenu() {
    const items = [{ id: 'busqueda', titulo: 'Búsqueda' }].concat(
      MODULOS.map(function (m) { return { id: m.id, titulo: m.titulo }; })
    );
    items.forEach(function (it) {
      const b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('role', 'tab');
      b.dataset.id = it.id;
      b.textContent = it.titulo;
      b.addEventListener('click', function () { mostrarModulo(it.id); });
      $('menu').appendChild(b);
    });
  }

  function crearSeccionModulo(m) {
    const sec = document.createElement('section');
    sec.className = 'modulo';
    sec.dataset.id = m.id;
    sec.hidden = true;

    const h = document.createElement('h2');
    h.textContent = m.titulo;
    const p = document.createElement('p');
    p.textContent = m.descripcion || '';
    sec.append(h, p);

    if (m.video) {
      const f = document.createElement('iframe');
      f.src = m.video;
      f.title = 'Video explicativo: ' + m.titulo;
      f.width = 640;
      f.height = 360;
      f.allowFullscreen = true;
      f.setAttribute('allow', 'fullscreen; picture-in-picture');
      sec.appendChild(f);
    } else {
      const v = document.createElement('p');
      v.textContent = '[Aquí irá el video explicativo]';
      sec.appendChild(v);
    }

    const lblEntrada = document.createElement('h3');
    lblEntrada.textContent = 'Entrada';
    const entrada = document.createElement('textarea');
    entrada.rows = 12;
    entrada.cols = 70;
    entrada.placeholder = m.entrada || '';
    const btnRun = document.createElement('button');
    btnRun.type = 'button';
    btnRun.textContent = 'Ejecutar';

    const lblSalida = document.createElement('h3');
    lblSalida.textContent = 'Resultado';
    const salida = document.createElement('pre');
    const btnCopiar = document.createElement('button');
    btnCopiar.type = 'button';
    btnCopiar.textContent = 'Copiar resultado';

    sec.append(lblEntrada, entrada, document.createElement('br'), btnRun,
      lblSalida, salida, btnCopiar);

    btnRun.addEventListener('click', async function () {
      try {
        const r = await m.ejecutar(entrada.value);
        salida.textContent = r === undefined || r === null ? '' : String(r);
      } catch (err) {
        salida.textContent = 'Error: ' + (err && err.message ? err.message : err);
      }
    });

    btnCopiar.addEventListener('click', async function () {
      try {
        await navigator.clipboard.writeText(salida.textContent);
        btnCopiar.textContent = 'Copiado';
      } catch (e) {
        btnCopiar.textContent = 'No se pudo copiar';
      }
      setTimeout(function () { btnCopiar.textContent = 'Copiar resultado'; }, 1500);
    });

    return sec;
  }

  construirMenu();
  MODULOS.forEach(function (m) { $('modulos-extra').appendChild(crearSeccionModulo(m)); });
  mostrarModulo('busqueda');

  // ------------------------------------------------------------------
  // Busqueda (modulo 1)
  // ------------------------------------------------------------------
  function setEstado(texto, tipo) {
    const el = $('estado');
    el.textContent = (tipo === 'err' ? '⚠ ' : '') + texto;
  }

  function formatoTiempo(ms) {
    const s = Math.floor(ms / 1000);
    return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
  }

  function bloquearBusqueda(valor) {
    buscando = valor;
    $('btn-buscar').disabled = valor;
    $('btn-ultimos').disabled = valor;
  }

  async function lanzarBusqueda() {
    if (buscando) return;
    const palabras = $('palabras').value.trim();
    if (!/^[\p{L}\p{N} ,]{0,200}$/u.test(palabras)) {
      setEstado('Solo se permiten letras, números, espacios y comas.', 'err');
      return;
    }

    bloquearBusqueda(true);
    setEstado('Enviando la solicitud a DevOps…');
    try {
      const resp = await api('/run', {
        method: 'POST',
        body: JSON.stringify({ palabrasClave: palabras })
      });
      if (!resp.ok) throw new Error(await errorDeApi(resp));
      const datos = await resp.json();
      await seguirCorrida(datos.id);
    } catch (err) {
      setEstado(err.message || String(err), 'err');
    } finally {
      bloquearBusqueda(false);
    }
  }

  async function seguirCorrida(id) {
    const inicio = Date.now();
    let fallosSeguidos = 0;

    while (Date.now() - inicio < MAX_ESPERA_MS) {
      setEstado('Búsqueda en curso… ' + formatoTiempo(Date.now() - inicio) +
        ' (puede tardar varios minutos)');
      await sleep(POLL_MS);

      let estado;
      try {
        const resp = await api('/status?id=' + encodeURIComponent(id));
        if (!resp.ok) throw new Error(await errorDeApi(resp));
        estado = await resp.json();
        fallosSeguidos = 0;
      } catch (err) {
        fallosSeguidos++;
        if (fallosSeguidos >= 5) throw new Error('No se pudo consultar el estado: ' + err.message);
        continue;
      }

      if (estado.state === 'completed') {
        if (estado.result === 'succeeded') {
          await cargarResultados('Búsqueda terminada. ');
          return;
        }
        throw new Error('La búsqueda terminó con error (' + (estado.result || 'sin detalle') +
          '). Revisa el pipeline en DevOps.');
      }
    }
    throw new Error('La búsqueda tarda demasiado. Revisa el pipeline en DevOps.');
  }

  // ------------------------------------------------------------------
  // Resultados
  // ------------------------------------------------------------------
  function parseCSV(texto) {
    const filas = [];
    let fila = [];
    let campo = '';
    let dentroComillas = false;

    for (let i = 0; i < texto.length; i++) {
      const c = texto[i];
      if (dentroComillas) {
        if (c === '"') {
          if (texto[i + 1] === '"') { campo += '"'; i++; }
          else { dentroComillas = false; }
        } else {
          campo += c;
        }
      } else if (c === '"') {
        dentroComillas = true;
      } else if (c === ',') {
        fila.push(campo);
        campo = '';
      } else if (c === '\n' || c === '\r') {
        if (c === '\r' && texto[i + 1] === '\n') i++;
        fila.push(campo);
        filas.push(fila);
        fila = [];
        campo = '';
      } else {
        campo += c;
      }
    }
    if (campo.length > 0 || fila.length > 0) {
      fila.push(campo);
      filas.push(fila);
    }
    return filas;
  }

  // Los ids de Firestore no pueden llevar "/": se deriva uno de la URL.
  function idDesdeUrl(url) {
    let hash = 0;
    for (let i = 0; i < url.length; i++) {
      hash = ((hash << 5) - hash + url.charCodeAt(i)) | 0;
    }
    return 'd' + Math.abs(hash);
  }

  async function cargarEstados() {
    const snap = await db.collection('detecciones').get();
    const estados = {};
    snap.forEach(function (doc) {
      const d = doc.data();
      if (d.enlace) estados[d.enlace] = d;
    });
    return estados;
  }

  function guardarEstado(enlace, campo, valor) {
    const cambio = { enlace: enlace };
    cambio[campo] = valor;
    db.collection('detecciones').doc(idDesdeUrl(enlace)).set(cambio, { merge: true })
      .catch(function (err) { alert('No se pudo guardar: ' + err.message); });
  }

  function crearSelect(opciones, actual, onCambio) {
    const sel = document.createElement('select');
    opciones.forEach(function (o) {
      const opt = document.createElement('option');
      opt.value = o[0];
      opt.textContent = o[1];
      opt.selected = o[0] === actual;
      sel.appendChild(opt);
    });
    sel.addEventListener('change', function () { onCambio(sel.value); });
    return sel;
  }

  function enlaceSeguro(texto) {
    try {
      const u = new URL(texto);
      return u.protocol === 'https:' ? u.href : null;
    } catch (e) {
      return null;
    }
  }

  function pintarTabla(filas, estados) {
    const cuerpo = $('tabla-body');
    cuerpo.textContent = '';

    filas.forEach(function (campos) {
      const enlace = campos[0] || '';
      const estado = estados[enlace] || {};
      const tr = document.createElement('tr');
      tr.dataset.enlace = enlace;

      const tdEnlace = document.createElement('td');
      const href = enlaceSeguro(enlace);
      if (href) {
        const a = document.createElement('a');
        a.href = href;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.textContent = 'Abrir ↗';
        tdEnlace.appendChild(a);
      } else {
        tdEnlace.textContent = '(enlace no válido)';
      }

      const tdPub = document.createElement('td');
      tdPub.className = 'publicacion';
      tdPub.textContent = campos[1] || '';
      const tdFecha = document.createElement('td');
      tdFecha.textContent = campos[2] || '';
      const tdLugar = document.createElement('td');
      tdLugar.textContent = campos[3] || '';

      const tdClas = document.createElement('td');
      tdClas.appendChild(crearSelect(
        [['', 'Sin clasificar'], ['TP', 'TP'], ['FP', 'FP']],
        estado.clasificacion || '',
        function (v) { guardarEstado(enlace, 'clasificacion', v); filtrar(); }
      ));

      const tdLista = document.createElement('td');
      tdLista.appendChild(crearSelect(
        [['', 'Ninguna'], ['negra', 'Lista negra'], ['blanca', 'Lista blanca']],
        estado.lista || '',
        function (v) { guardarEstado(enlace, 'lista', v); }
      ));

      const tdNotas = document.createElement('td');
      const inp = document.createElement('input');
      inp.type = 'text';
      inp.value = estado.notas || '';
      inp.setAttribute('aria-label', 'Notas');
      inp.addEventListener('change', function () { guardarEstado(enlace, 'notas', inp.value); });
      tdNotas.appendChild(inp);

      tr.append(tdEnlace, tdPub, tdFecha, tdLugar, tdClas, tdLista, tdNotas);
      cuerpo.appendChild(tr);
    });
  }

  async function cargarResultados(prefijo) {
    prefijo = typeof prefijo === 'string' ? prefijo : '';
    setEstado('Cargando resultados…');
    try {
      const resultados = await Promise.all([api('/results'), cargarEstados()]);
      const resp = resultados[0];
      if (!resp.ok) throw new Error(await errorDeApi(resp));

      const filas = parseCSV(await resp.text()).slice(1)
        .filter(function (f) { return f.length > 1; });
      registros = filas;
      pintarTabla(filas, resultados[1]);
      $('zona-resultados').hidden = false;
      filtrar();
      setEstado(prefijo + 'Resultados cargados: ' + filas.length + ' detecciones.', 'ok');
    } catch (err) {
      setEstado('No se pudieron cargar los resultados: ' + (err.message || err), 'err');
    }
  }

  function filtrar() {
    const lugar = $('filtro-lugar').value.toLowerCase();
    const texto = $('filtro-texto').value.toLowerCase();
    const clas = $('filtro-clasificacion').value;

    document.querySelectorAll('#tabla-body tr').forEach(function (tr) {
      const c = tr.children;
      const valorClas = c[4].querySelector('select').value;
      const okLugar = c[3].textContent.toLowerCase().includes(lugar);
      const okTexto = c[1].textContent.toLowerCase().includes(texto);
      let okClas = true;
      if (clas === 'sin-clasificar') okClas = valorClas === '';
      else if (clas) okClas = valorClas === clas;
      tr.hidden = !(okLugar && okTexto && okClas);
    });
  }

  function csvCampo(v) {
    v = String(v === undefined || v === null ? '' : v);
    return /[",\n\r]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
  }

  function descargarCSV() {
    const lineas = [['Enlace', 'Publicacion', 'Fecha', 'Lugar', 'Clasificacion', 'Lista', 'Notas']];
    document.querySelectorAll('#tabla-body tr').forEach(function (tr) {
      if (tr.hidden) return;
      const c = tr.children;
      lineas.push([
        tr.dataset.enlace,
        c[1].textContent,
        c[2].textContent,
        c[3].textContent,
        c[4].querySelector('select').value,
        c[5].querySelector('select').value,
        c[6].querySelector('input').value
      ]);
    });
    const csv = '﻿' + lineas.map(function (l) { return l.map(csvCampo).join(','); }).join('\r\n');
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    a.download = 'detecciones_filtradas.csv';
    a.click();
    URL.revokeObjectURL(a.href);
  }

  $('btn-buscar').addEventListener('click', lanzarBusqueda);
  $('btn-ultimos').addEventListener('click', function () { cargarResultados(); });
  $('btn-descargar').addEventListener('click', descargarCSV);
  $('filtro-lugar').addEventListener('input', filtrar);
  $('filtro-texto').addEventListener('input', filtrar);
  $('filtro-clasificacion').addEventListener('change', filtrar);
})();
