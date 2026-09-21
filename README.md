# ehMET WebApp v2 — preparada para Internet

Esta versión está preparada para desplegarse en Render desde GitHub, sin instalar Python en el ordenador del usuario.

Incluye PostgreSQL central, acceso por usuario/contraseña, FIB-4, selector SCORE2/SCORE2-OP/SCORE2-Diabetes, historial, estadísticas y exportación CSV/Excel.

## Publicación sin instalar nada

1. Cree un repositorio **privado** en GitHub, por ejemplo `ehmet-webapp`.
2. Entre en el repositorio y use **Add file > Upload files**.
3. Suba **todo el contenido de esta carpeta**: `main.py`, `clinical.py`, `database.py`, `render.yaml`, `requirements.txt` y las carpetas `templates`, `static`, `tests`.
4. Confirme con **Commit changes**.
5. Entre en Render y conecte GitHub.
6. Cree un **Blueprint** y seleccione el repositorio.
7. Render leerá `render.yaml` y creará la web y PostgreSQL.
8. Cuando se solicite, defina `APP_USERNAME` y `APP_PASSWORD`.
9. Al finalizar obtendrá una URL HTTPS pública.

## Seguridad y RGPD

No introduzca nombre, DNI, número de historia, teléfono, email, dirección ni fecha exacta de nacimiento. La ausencia de identificadores directos no garantiza por sí sola anonimización irreversible: un conjunto de datos clínicos puede seguir siendo reidentificable. Antes de uso asistencial real o investigación multicéntrica se necesita revisión de RGPD/LOPDGDD, base jurídica, minimización, política de retención, permisos y gobernanza.

## RCV

Esta versión selecciona el algoritmo de riesgo cardiovascular apropiado, pero no aproxima internamente el porcentaje. El porcentaje debe venir de una calculadora/implementación validada hasta integrar y validar completamente SCORE2/SCORE2-OP/SCORE2-Diabetes.
