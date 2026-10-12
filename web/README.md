# Radar Comercial - página web (Firebase Hosting)

Página del SOC: login, búsqueda en Marketplace (lanza el pipeline de DevOps a través del Worker de Cloudflare) y módulos de texto que corren en el navegador.

## Archivos
- `public/config.js` - URL del Worker y config de Firebase (lo único que se edita para desplegar).
- `public/modulos.js` - lógica de los módulos 2 y 3 y la URL de su video.
- `public/app.js`, `index.html`, `style.css` - la página.
- `firestore.rules` - solo usuarios con sesión leen/escriben las clasificaciones.

## Desplegar
```
npm install -g firebase-tools
firebase login
cd web
firebase deploy --only firestore:rules,hosting
```

## Probar en local
```
cd web
firebase emulators:start --only hosting
```
