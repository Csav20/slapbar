# Cómo subir SlapBar a GitHub

## Paso 1 — Crear el repositorio en GitHub

1. Ve a https://github.com/new
2. **Repository name:** `slapbar`
3. **Description:** `App de barra de menú macOS con packs de sonido — SlapMac + DBZ + más`
4. Marca **Public**
5. **NO** marques "Add a README file" (ya tenemos uno)
6. Clic en **Create repository**

GitHub te mostrará la página del repo vacío con instrucciones. Copia tu URL — será algo como:
`https://github.com/TU_USUARIO/slapbar.git`

---

## Paso 2 — Copiar la carpeta al Desktop

Desde Finder, copia la carpeta `slapbar/` de esta sesión a tu Desktop:
```
~/Desktop/slapbar/
```

---

## Paso 3 — Abrir Terminal en la carpeta

```bash
cd ~/Desktop/slapbar
```

---

## Paso 4 — Inicializar git y primer commit

```bash
# Inicializar repositorio git
git init

# Agregar todos los archivos
git add .

# Primer commit
git commit -m "🎵 Initial commit — SlapBar v1.0"
```

---

## Paso 5 — Conectar con GitHub y subir

Reemplaza `TU_USUARIO` con tu nombre de usuario de GitHub:

```bash
# Conectar con el repo remoto
git remote add origin https://github.com/TU_USUARIO/slapbar.git

# Renombrar rama a main
git branch -M main

# Subir al repositorio
git push -u origin main
```

GitHub te pedirá tu usuario y contraseña (o token personal).

> **Si pide token:** Ve a GitHub → Settings → Developer settings → Personal access tokens → Generate new token (classic) → Marca "repo" → Genera y copia el token. Úsalo como contraseña.

---

## Paso 6 — Verificar

Abre en el navegador:
```
https://github.com/TU_USUARIO/slapbar
```

Deberías ver el README con el logo de SlapBar. ✓

---

## Commits futuros

Para subir cambios después:

```bash
cd ~/Desktop/slapbar

# Ver qué cambió
git status

# Agregar cambios
git add .

# Commit con mensaje descriptivo
git commit -m "✨ Agregar sonidos de Vegeta al pack DBZ"

# Subir
git push
```

---

## Tags de versión (opcional)

```bash
# Marcar una versión estable
git tag -a v1.0.0 -m "SlapBar v1.0.0 — Release inicial"
git push origin v1.0.0
```
