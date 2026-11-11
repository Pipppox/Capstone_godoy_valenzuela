# Guión de Presentación — StockIN

**Defensa de Portafolio de Título · Duoc UC**

---

&nbsp;

## Diapositiva 1 — Portada

**Quién habla:** Juan

**Qué decir:**

"Buenos días, profesores. Mi nombre es Juan Godoy y junto a mi compañero Felipe Valenzuela les presentaremos nuestro proyecto de portafolio de título: StockIN, una aplicación móvil de gestión de inventario diseñada para microemprendedores."

---

## Diapositiva 2 — Integrantes del Equipo

**Qué decir:**

"Nuestro equipo está conformado por dos integrantes. Yo, Juan Godoy, me desempeñé como Scrum Master y desarrollador principal, encargado de la arquitectura, el backend con Supabase y la lógica de negocio. Felipe Valenzuela fue nuestro Product Owner y desarrollador frontend, responsable del diseño de interfaces y la experiencia de usuario con Flet."

---

## Diapositiva 3 — Descripción del Proyecto

**Qué decir:**

“Para entender el contexto de StockIN, hay que mirar la realidad del microemprendimiento en Chile. Hay miles de personas que tienen su negocio formal — locales en el mall, tiendas fuera del metro, espacios habilitados por la municipalidad — y que a pesar de estar formalizados, siguen gestionando su inventario de forma manual: cuadernos, hojas de cálculo o simplemente de memoria. No es que no quieran ordenarse, sino que no cuentan con una herramienta simple y accesible que se adapte a su realidad.”

"Esto genera problemas concretos, tales como , pérdida de productos, quiebres de stock, ventas no registradas y desorden financiero. StockIN nace para resolver exactamente esto. Es una aplicación móvil que permite a estos emprendedores llevar el control de su inventario, registrar ventas y visualizar el estado de su negocio desde el celular, sin necesidad de conocimientos técnicos avanzados.

---

## Diapositiva 4 — Objetivos

**Qué decir:**

"Nuestro objetivo general fue desarrollar una aplicación móvil funcional que permita a microemprendedores gestionar su inventario de manera eficiente y accesible."

"Para lograrlo, definimos siete objetivos específicos que guiaron todo el desarrollo:"

*Recorrer brevemente cada uno, sin leerlos textualmente. Agruparlos así:*

"Primero, los objetivos de funcionalidad: implementamos un sistema CRUD completo para productos, un módulo de registro de ventas con descuento automático de stock, y un módulo de registro de compras que actualiza el inventario en tiempo real."

"Segundo, los objetivos técnicos: diseñamos la base de datos en Supabase con integridad referencial, implementamos autenticación segura con email y contraseña, y desarrollamos un dashboard con gráficos que muestran las métricas clave del negocio."

"Tercero, el objetivo de calidad: ejecutamos cuatro ciclos completos de pruebas para asegurar la estabilidad y usabilidad de la aplicación."

**Punto clave:** Todos los objetivos se cumplieron al 100%. Eso se demostrará en la diapositiva 14\.

---

## Diapositiva 5 — Alcance y Limitaciones

**Qué decir:**

"En cuanto al alcance, StockIN cubre las operaciones esenciales de inventario: gestión completa de productos con categorías, registro de ventas  con actualización automática del stock, un dashboard con gráficos de rendimiento"

"Es importante ser transparentes con las limitaciones. StockIN no incluye funcionalidades como facturación electrónica, integración con sistemas de punto de venta externos, ni gestión multiusuario dentro de un mismo negocio. Tampoco cuenta con un buscador de texto para productos: la navegación del inventario es manual, deslizando por la lista."

"Otra limitación relevante es el rendimiento: la aplicación funciona de manera fluida con hasta 650 productos, pero sobre esa cifra el rendimiento se degrada, especialmente en dispositivos de gama media y baja. El límite recomendado es de 550 productos."

---

## Diapositiva 6 — Metodología

**Qué decir:**

"Para gestionar el desarrollo elegimos Kanban como metodología ágil. La razón principal es que Kanban se adapta muy bien a equipos pequeños de dos personas: no requiere sprints rígidos ni ceremonias pesadas, sino que permite un flujo continuo de trabajo con visibilidad clara del estado de cada tarea."

"Utilizamos un tablero Kanban con columnas de Backlog, En Progreso, En Revisión y Completado. Esto nos permitió priorizar tareas de forma dinámica y reaccionar rápidamente ante cambios o problemas que surgieron durante el desarrollo."

"Además, complementamos Kanban con prácticas de seguimiento diario donde registramos los avances, bloqueos y decisiones tomadas."

**Punto clave:** Si preguntan por qué no Scrum, la respuesta es clara: con solo dos integrantes, los roles de Scrum (PO, SM, equipo) se solapan inevitablemente. Kanban fue la decisión pragmática correcta.

---

## Diapositiva 7 — Cronograma

**Qué decir:**

"El proyecto se desarrolló en 10 semanas, dividido en 6 etapas claramente definidas."

*Señalar el cronograma en la diapositiva sin leer cada etapa. Resaltar solo los hitos clave:*

"Las primeras semanas fueron de planificación y diseño, donde definimos la arquitectura, el modelo de datos y los requisitos. Luego entramos en dos etapas de desarrollo iterativo, implementando primero el núcleo de la aplicación y luego las funcionalidades complementarias. Finalmente, dedicamos las últimas semanas a cuatro ciclos de pruebas y a la documentación final."

"Lo importante es que cumplimos con todas las fechas establecidas, sin retrasos significativos."

---

## **Diapositiva 8 — Arquitectura de Software (juan parte desde acà).**

**Qué decir:**

"La arquitectura de la app sigue un patrón de tres capas bien definido."

"En la capa de presentación tenemos la interfaz construida con Flet, que es un framework basado en Flutter que permite crear interfaces nativas desde Python. Esto fue una decisión estratégica: nos permitió desarrollar en un solo lenguaje, Python, que es el que mejor manejamos."

"La capa de lógica de negocio contiene los controladores que manejan las reglas del inventario: validaciones de stock, cálculos de totales en ventas, actualización automática de cantidades,etc"

“La capa de datos utiliza SQLite como base de datos local en el dispositivo, lo que permite que la app funcione completamente offline. Para los respaldos en la nube, utilizamos Supabase, donde los datos se almacenan cifrados. Y para la funcionalidad de mapas y geolocalización, nos conectamos con las APIs de Google: Geocoding para convertir direcciones en coordenadas, Places para el autocompletado de direcciones, y Map Tiles para el mapa interactivo.”

"Además, implementamos Row Level Security en Supabase, lo que significa que cada usuario solo puede ver y modificar sus propios datos. Esto es crítico para una aplicación multiusuario."

**PBKDF2-HMAC-SHA256 (200K iteraciones)** es el algoritmo que usa para proteger las contraseñas. En vez de guardar la contraseña tal cual (“miClave123”), la transforma en un código irreconocible mediante un proceso matemático que se repite 200.000 veces. Así, aunque alguien acceda a la base de datos, no puede saber cuál era la contraseña original.

**Sal aleatoria de 16 bytes por contraseña** es un complemento de lo anterior. Antes de transformar cada contraseña, se le agrega un texto aleatorio único (la “sal”). Esto significa que si dos usuarios tienen la misma contraseña, el código guardado es distinto para cada uno. Los 16 bytes son el largo de esa sal — suficiente para que sea prácticamente imposible que se repita.

**Si te preguntan en la defensa**, una respuesta corta sería: “Las contraseñas se almacenan hasheadas con PBKDF2 a 200 mil iteraciones, cada una con su propia sal aleatoria, por lo que no se guardan en texto plano. Y los respaldos de datos se cifran con Fernet, donde la clave de cifrado se deriva de la contraseña del usuario, asegurando que solo él pueda restaurar su información.”

&nbsp;

---

## Diapositiva 9 — Modelo de Datos

&nbsp;

**Qué decir:**

Nuestro modelo de datos utiliza una base de datos relacional SQLite almacenada localmente en el dispositivo, en un archivo llamado stockin.db. Está compuesta por cinco tablas locales: usuarios, productos, ventas, lugares\_cache y sesion\_local.”

“La tabla central es usuarios, que almacena los datos de autenticación — incluyendo el hash de contraseña y la sal — además de información como foto de perfil, nombre de empresa y preferencias de notificaciones. Cada usuario tiene una sesión local que gestiona el inicio, cierre y restauración de sesión.”

“Luego tenemos productos, que depende del usuario y contiene código, nombre, categoría, precio, stock y un estado activo para el borrado suave. Cada producto se relaciona con ventas, que registra la cantidad, precio unitario, total, lugar y fecha de cada transacción.”

“También está lugares\_cache, que guarda las coordenadas de los lugares de venta para optimizar la integración con Google Maps sin repetir consultas a la API.”

“Además de las cinco tablas locales, el respaldo en la nube se guarda en Supabase, en la tabla respaldos, donde los datos se almacenan cifrados con Fernet. Los importes se guardan como números enteros y la integridad referencial se apoya en claves foráneas con borrado en cascada.”

Punto clave: Si preguntan por qué SQLite y no directamente Supabase para todo, es porque la app funciona offline — los datos viven en el dispositivo y el respaldo en la nube es una capa adicional de seguridad, no una dependencia.

---

## Diapositiva 10 — Tecnologías Utilizadas

&nbsp;

**Qué decir:**

"Estas son las tecnologías que componen el stack de StockIN."

"Python como lenguaje principal, porque es el que mejor dominamos y tiene un ecosistema muy completo. Flet como framework de interfaz, que nos permitió crear una app móvil nativa usando solo Python, sin necesidad de aprender Dart o Kotlin.&nbsp;

Supabase como backend, proporcionando PostgreSQL, autenticación y APIs REST. Y GitHub como plataforma de control de versiones y colaboración."

"Esta combinación nos dio una ventaja importante: todo el equipo podía trabajar en la misma base de código, en el mismo lenguaje, lo que redujo la curva de aprendizaje y los errores de integración."

---

## Diapositiva 11 — Ciclos de Pruebas

&nbsp;

**Qué decir:**

"Una de las partes que más nos enorgullece es el proceso de pruebas. Realizamos cuatro ciclos completos de testing, y estos son los resultados."

"Ejecutamos un total de 83 casos de prueba, cubriendo funcionalidad, usabilidad, seguridad y rendimiento. Durante los ciclos detectamos 22 defectos, de los cuales resolvimos todos. Eso nos da una tasa de corrección del 100%."

"Los ciclos fueron incrementales: en el primero encontramos la mayor cantidad de errores, como era esperable. En cada ciclo posterior los defectos se fueron reduciendo, lo que confirma que nuestro proceso de corrección fue efectivo."

"Probamos en tres dispositivos distintos: un Samsung Galaxy S25 Ultra como gama alta, un Xiaomi 12 Lite como gama media, y un Samsung Galaxy Tab S4 como gama baja. Esto nos permitió validar el rendimiento en diferentes niveles de hardware."

---

## Diapositiva 12 — Demostración: Pantallas principales

&nbsp;

**Qué decir:**

---

## Diapositiva 13 — Demostración: Más funcionalidades

**Qué decir:**

---

## Diapositiva 14 — Cumplimiento de Requisitos

&nbsp;

**Qué decir:**

"Esta diapositiva es quizás la más importante para la evaluación. Aquí se demuestra que cumplimos con absolutamente todos los requisitos definidos."

"30 de 30 requisitos funcionales cumplidos. Esto incluye desde las operaciones CRUD básicas hasta funcionalidades más complejas como el dashboard con gráficos, la gestión de categorías, y el historial de transacciones."

"20 de 20 requisitos no funcionales cumplidos. Esto abarca rendimiento, seguridad, usabilidad, compatibilidad y portabilidad. Cada uno fue verificado con casos de prueba específicos."

“30 de 30 historias de usuarios , una por requisito funcional”

"Esto nos da un cumplimiento total del 100% en ambas categorías, lo que valida que el alcance definido al inicio del proyecto se respetó íntegramente."

---

## Diapositiva 15 — Lecciones Aprendidas

&nbsp;

**Qué decir:**

"Este proyecto nos dejó varias lecciones importantes que queremos compartir."

"La primera lección es sobre la importancia de elegir bien las herramientas. Flet y Supabase nos permitieron avanzar rápido, pero también tuvieron limitaciones que nos obligaron a ser creativos. Por ejemplo, Flet no tiene todos los widgets que tendría un framework más maduro como React Native, así que tuvimos que diseñar soluciones propias para ciertas interacciones."

"La segunda lección es que las pruebas no son opcionales. Sin los cuatro ciclos de testing, muchos de los 22 defectos que encontramos habrían llegado a la versión final. El testing sistemático nos salvó de entregar un producto con errores."

"Y la tercera: la documentación importa. Mantener todos los documentos actualizados y consistentes fue un desafío constante, pero al final es lo que permite que otra persona entienda y continúe el proyecto."

---

## Diapositiva 16 — Conclusiones y Cierre

**Qué decir:**

"Para cerrar, StockIN cumple con el objetivo que nos propusimos: es una aplicación móvil funcional, segura y accesible que permite a microemprendedores gestionar su inventario de forma eficiente."

"Creemos que la aplicación tiene potencial de crecimiento. Como trabajo futuro, se podrían agregar funcionalidades como reportes exportables, integración con medios de pago, y soporte para otros sistemas como ios.

"Agradecemos su tiempo y atención. Estamos a su disposición para cualquier pregunta."

---

## Tips para la ronda de preguntas

La comisión hará preguntas después de la presentación. Estas son las más probables y cómo responderlas:

**"¿Por qué eligieron Flet y no Flutter, React Native u otro framework?"** Respuesta: Flet permite desarrollar en Python puro, que es el lenguaje que mejor dominamos. Usar Flutter directamente habría requerido aprender Dart, y React Native requiere JavaScript/TypeScript. Flet nos permitió enfocarnos en la lógica del negocio sin la curva de aprendizaje de un nuevo lenguaje.

**"¿Por qué no implementaron un buscador de productos?"** Respuesta: Fue una decisión de alcance. Para el volumen de productos que maneja un microemprendedor típico (menos de 200), la navegación manual por la lista es suficiente. Un buscador queda como mejora futura.

**"¿Qué pasa si un usuario tiene más de 650 productos?"** Respuesta: El rendimiento se degrada significativamente, especialmente en dispositivos de gama media y baja. En nuestras pruebas, el Samsung Galaxy S25 Ultra (gama alta) no presentaba problemas, pero el Galaxy Tab S4 (gama baja) mostraba lentitud marcada. Por eso establecimos 650 como límite soportado y 550 como recomendado.

**"¿Cómo aseguran la seguridad de los datos?"** Respuesta: Usamos la autenticación de Supabase con email y contraseña, y Row Level Security (RLS) en PostgreSQL, que garantiza que cada usuario solo puede acceder a sus propios registros a nivel de base de datos. No es una validación solo en el frontend.

**"¿Qué mejoras harían si tuvieran más tiempo?"** Respuesta: Buscador de productos, notificaciones push de stock bajo, reportes exportables en PDF o Excel, integración con medios de pago, y soporte multiusuario para negocios con empleados.

**"¿Cómo manejaron los conflictos o desacuerdos en el equipo?"** Respuesta: Al ser solo dos personas, la comunicación fue directa y constante. Usamos el tablero Kanban para tener visibilidad de quién hacía qué, y el seguimiento diario nos permitía resolver bloqueos rápidamente.

---

