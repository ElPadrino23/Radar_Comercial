// ============================================================
// CONFIGURACION - lo unico que tienes que editar para desplegar
// ============================================================

// URL del Worker de Cloudflare, SIN diagonal al final.
// Ejemplo: "https://radar-api.mi-cuenta.workers.dev"
const API_URL = "https://radar-api.REEMPLAZA-ESTO.workers.dev";

// Config publica de Firebase (la seguridad real la dan Auth y las reglas).
const FIREBASE_CONFIG = {
  apiKey: "AIzaSyA8Jkn1L_psWtWLsVZ-TnKHPwn87MuP-TY",
  authDomain: "brandprotecion.firebaseapp.com",
  projectId: "brandprotecion",
  storageBucket: "brandprotecion.firebasestorage.app",
  messagingSenderId: "1097997938894",
  appId: "1:1097997938894:web:21f40336657b65cf3d209f"
};

// Cada cuantos milisegundos se pregunta a DevOps si la busqueda ya termino.
const POLL_INTERVAL_MS = 10000;
