# Cómo una IA aprendió a hacer Dark Psytrance (y por qué todavía no puede)

## La idea

Todo empezó con una pregunta simple: **¿puede una IA crear música de verdad?**

No hablo de esas apps que te generan "un lo-fi chill para estudiar" en 3 segundos. Hablo de Dark Psytrance — uno de los géneros más extremos, experimentales y difíciles de producir que existe en la música electrónica. Música que se toca en festivales a las 4 de la mañana, donde el DJ te lleva en un viaje de 2 horas entre el orden y el caos, entre bailar con los ojos cerrados y perder la noción de dónde estás.

Música de artistas como Psykovsky, Kindzadza, Glosolalia, Frantic Noise, Will O Wisp — gente que lleva décadas refinando un arte que combina ingeniería de sonido con algo que solo se puede describir como alquimia.

¿Puede una IA hacer eso? La respuesta corta es: no. Todavía no. Pero lo que descubrimos en el camino es mucho más interesante que un sí o un no.

---

## El punto de partida

Le pedí a Claude (la IA de Anthropic) que generara dark psytrance. No desde una app de música, no desde un plugin mágico. Desde **Python puro** — código, matemática, ondas sonoras generadas número por número.

La primera versión fue exactamente lo que esperarías de una máquina haciendo música: técnicamente correcta y absolutamente sin alma. Un metrónomo disfrazado de canción. El tempo estaba bien, las notas estaban en escala, la estructura tenía sentido. Pero si se lo ponías a alguien que escucha psy, se iba a reír (o a llorar).

Y ahí empezó lo interesante.

---

## El método: enseñarle a una IA qué es "buena música"

### Paso 1 — Mostrarle la referencia

Le di 4 tracks de **Glosolalia**, un artista experimental argentino que admiro profundamente. La IA no puede "escuchar" como nosotros — no siente el groove, no le eriza la piel un breakdown bien puesto. Pero puede **analizar el audio como datos**: millones de números que representan la forma del sonido.

Y lo que encontró fue revelador:

- Glosolalia llena **8 de 10 bandas de frecuencia** simultáneamente. Mi track llenaba 5. Ellos crean un muro de sonido. Yo tenía una pared con agujeros.
- El **18% del tiempo** algo cambia dramáticamente en su música. En la mía, casi nada cambiaba.
- Los canales izquierdo y derecho cuentan **historias diferentes**. A veces van en direcciones opuestas. Mi track era prácticamente mono.
- Su música tiene una **entropía de 12.5 bits** — una medida de complejidad e imprevisibilidad. La mía estaba en 11.

Números. Pero números que explican por qué una cosa suena a obra maestra y la otra suena a demo de Windows.

### Paso 2 — Investigar a los maestros

Investigamos las técnicas de producción de los artistas más respetados del género:

- **Psykovsky** (Rusia) — trabaja en FL Studio con sintetizadores hardware como el Nord Rack 2 y el Access Virus. Sus sonidos son "extremadamente digitales" pero con un twist analógico que los hace orgánicos.

- **Kindzadza** (Rusia) — físico y matemático de formación, creó **su propio sintetizador** (DDZynth) que combina síntesis granular, FM y terrain. Usa Bitwig Studio y módulos eurorack. Literalmente inventó herramientas que no existían para crear los sonidos que tenía en la cabeza.

- **Frantic Noise** (Argentina) — cofundador de Dark Prisma Records, el sello de Glosolalia. Usa Vital y Serum, publicó más de 500 presets. Demuestra que no necesitás hardware caro — necesitás entender el sonido.

- **Will O Wisp** (Buenos Aires) — pionero en llevar la síntesis modular al psytrance. Sus patches en eurorack y VCV Rack se auto-generan y evolucionan solos. La máquina crea, el artista guía.

De esta investigación salieron técnicas concretas que fuimos aplicando versión a versión: el corte en 300Hz del kick (la firma del dark psy), el rolling bass diseñado para encajar en fase con el kick, la síntesis FM para texturas alienígenas, el Filter FM para ese sonido "eléctrico" que define al género.

### Paso 3 — Iterar, iterar, iterar

Hicimos **8 versiones**. Cada una mejor que la anterior. Cada una enseñándome algo sobre lo que la IA puede y no puede hacer.

---

## Las lecciones (o: cómo un humano le enseñó música a una máquina)

### "Los patrones son muy predecibles"

La versión 3 era técnicamente más avanzada — humanización, swing, micro-timing. Pero seguía sonando a máquina. Le dije a Claude: **"lo que vos me das es matemáticamente bien hecho, pero carece de todo lo que yo apreciaría en la música"**.

Ese fue un momento clave. La IA puede aleatorizar cosas, puede agregar variación estadística, pero no entiende la **intención** detrás de la imperfección humana. Un baterista no toca fuera de tiempo por error — toca fuera de tiempo porque eso crea tensión, groove, swing. Es una decisión artística disfrazada de imperfección.

### "No tienen groove, son monstruosos, y ahí está su belleza"

Cuando la IA intentó extraer el "groove" de Glosolalia para imitarlo, le dije que estaba buscando en el lugar equivocado. Glosolalia no tiene groove en el sentido convencional. Son **experimentales, caóticos, monstruosos** — y esa es su belleza.

La IA estaba tratando de encontrar patrones donde el artista deliberadamente los destruye. Es como pedirle a un algoritmo que entienda por qué un cuadro de Picasso es bello analizando la geometría.

### "El silencio es el golpe más fuerte"

Este fue el descubrimiento más importante. Le expliqué a Claude cómo funciona un live set de dark psy:

> Imaginate que el ritmo viene siendo "pan pan pan pan pan" y de repente, en ese beat, silencio. Un instante. Y cuando vuelve, no vuelve igual — vuelve con "PANAPANAPAPANANPAN".

La primera vez que la IA intentó implementar esto, metió 32 kicks en un compás. Me maté de risa. Le dije que eso era "un asesinato auditivo". Entendió el concepto pero lo ejecutó con lógica pura — si "más rápido = más energía", entonces "el doble de notas = el doble de energía", ¿no?

No. La euforia no viene de la velocidad. Viene de la **anticipación y la resolución**. El silencio crea una pregunta. El drop es la respuesta. Pero la respuesta no es un grito — es un "acá estoy de vuelta, y vine con más fuerza". Un kick solo, casi tímido. Después otro. El bass se suma. Y en 4 beats estás de vuelta en el groove, pero diferente. Cambiado. Más intenso.

La versión 7, cuando finalmente entendió esto, fue un salto enorme.

---

## Lo que la IA puede hacer (y es impresionante)

- **Analizar música como datos** — extraer el "ADN sonoro" de un artista: espectro de frecuencias, dinámica, entropía, imagen estéreo, irregularidad rítmica.
- **Generar estructura musical** — la arquitectura del track: intro, builds, drops, breakdowns, caos, orden.
- **Sintetizar audio desde cero** — ondas, filtros, FM synthesis, granular, todo en código.
- **Procesar audio a través de plugins profesionales** — usamos KranchDD, el plugin de distorsión de Kindzadza, cargado desde Python.
- **Iterar a velocidad imposible** — 8 versiones completas en una sesión. Un productor humano tardaría semanas.
- **Calibrar objetivamente** — comparar spectrum, loudness, entropía contra una referencia y ajustar.

## Lo que la IA no puede hacer (todavía)

- **Escuchar** — puede analizar frecuencias pero no sabe si algo "suena bien". No tiene oído.
- **Sentir el groove** — puede aleatorizar timing pero no entiende por qué un ritmo te hace mover la cabeza.
- **Elegir sonidos** — puede generar una onda de sierra pero no sabe si esa onda de sierra suena a dark psy o a un ringtone de Nokia.
- **Tomar decisiones estéticas** — "más oscuro", "más visceral", "más cósmico" son conceptos que necesitan un humano para traducirlos a parámetros.
- **Entender el silencio** — puede generar silencio, pero no entiende por qué ese silencio en ESE momento cambia todo.

---

## La verdad sobre "hacer música con IA"

Hay una diferencia enorme entre lo que ves en las redes y lo que hicimos acá.

Las apps de música con IA te dan un resultado en 10 segundos. Suena "bien" — genérico, pulido, olvidable. Es el equivalente musical de comida rápida: nutre pero no alimenta.

Lo que hicimos nosotros es diferente. No usamos una app. Construimos un **motor de síntesis desde cero**, lo calibramos contra artistas reales, implementamos técnicas de producción profesional, y lo iteramos 8 veces con dirección creativa humana.

Y aún así, el resultado está lejos de competir con un artista real. Pero eso es lo valioso del experimento.

**La IA es una herramienta extraordinaria y un artista pésimo.**

Puede hacer en segundos lo que a un humano le tomaría horas: analizar espectros, generar variaciones, procesar audio por múltiples plugins. Pero necesita un humano que le diga: "no, eso suena a ametralladora, lo que quiero es que suene a un corazón que vuelve a latir después de haberse detenido".

Esa frase no se puede traducir a código. Todavía.

---

## ¿Y ahora qué?

El proyecto está en GitHub, abierto, para que cualquiera pueda verlo, usarlo, mejorarlo. No es un producto terminado — es una exploración. Un documento de lo que pasa cuando un humano que ama la música y una IA que entiende matemática se sientan juntos a intentar crear algo.

Las próximas versiones van a sonar mejor. Mejores sonidos de base, mejores sintetizadores, más técnicas. Pero la lección más grande ya la aprendimos:

**La música no es matemática con ritmo. Es intención con forma de sonido.**

Y esa intención, por ahora, solo puede venir de un humano.

---

*Proyecto: [github.com/asastuai/Darkpsy-engine](https://github.com/asastuai/Darkpsy-engine)*

*"El silencio antes del drop es la parte más fuerte del track"*
