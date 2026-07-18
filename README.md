# 📢 Control de Beneficios y Promociones de Transporte (CABA / AMBA)

Un scraper concurrente, modular y extensible en Python diseñado para recolectar y consolidar beneficios y promociones de transporte público (colectivos, subtes y trenes) de canales oficiales en Argentina.

---

## 🚀 Características

- ⚡ **Ejecución Concurrente:** Utiliza `ThreadPoolExecutor` para analizar múltiples enlaces en paralelo, acelerando el procesamiento a menos de 8 segundos.
- 🧩 **Arquitectura Modular (Registry Pattern):** Los scrapers se registran y resuelven de manera dinámica, facilitando la adición de nuevas entidades sin modificar el flujo principal.
- 🎯 **Filtro Semántico Avanzado:** Mecanismo en dos fases (Contexto de Transporte + Indicador de Beneficio) que elimina falsos positivos en sitios bancarios generales.
- 💾 **Configuración Desacoplada:** Los datos de soporte (*fallback*) estables se gestionan en un archivo JSON externo.
- 🖥️ **CLI Robusta:** Soporte de parámetros para filtros específicos, niveles de detalle y exportación estructurada.
- 🎨 **Visualización Estética:** Diseñado en la terminal con tablas descriptivas enriquecidas mediante `rich`.

---

## 🛠️ Instalación y Requisitos

Asegúrate de tener Python 3.8 o superior instalado.

1. Clona el repositorio e ingresa al directorio del proyecto:
   ```bash
   cd promos
   ```

2. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

---

## 📖 Uso y Parámetros de CLI

Ejecuta el script principal desde la consola:

```bash
python3 main.py [OPCIONES]
```

### Opciones Disponibles:

| Parámetro | Atajo | Descripción |
| :--- | :---: | :--- |
| `--live-only` | - | Muestra únicamente las promociones obtenidas en vivo de la web (excluye fallbacks locales). |
| `--verbose` | - | Muestra descripciones y requisitos completos sin truncar en la tabla de la terminal. |
| `--entity` | - | Filtra el reporte y muestra solo la entidad especificada (ej: `macro`, `provincia`, `sube`). |
| `--output` | `-o` | Guarda los resultados obtenidos y filtrados en un archivo en formato JSON. |

### Ejemplos de uso:

- **Ejecución estándar (rápida):**
  ```bash
  python3 main.py
  ```
- **Filtrar por Banco Macro mostrando texto legal completo:**
  ```bash
  python3 main.py --entity macro --verbose
  ```
- **Obtener datos únicamente en vivo de Cuenta DNI y guardarlos en JSON:**
  ```bash
  python3 main.py --entity "Cuenta DNI" --live-only -o cuenta_dni_report.json
  ```

---

## 📁 Estructura del Proyecto

```
promos/
├── main.py                     # Punto de entrada de CLI y lógica de concurrencia
├── config.py                   # Ajustes generales (Headers de red y carga de fallbacks)
├── requirements.txt            # Dependencias del proyecto (requests, bs4, rich)
├── README.md                   # Documentación principal
│
├── bancos/
│   ├── links_scraper_transporte.txt # Lista de URLs oficiales a analizar
│   └── fallbacks.json               # Base de datos local de promociones estables
│
├── scrapers/
│   ├── __init__.py             # Inicialización y registro de scrapers
│   ├── base.py                 # Clase base BaseScraper y decorador de registro
│   ├── banco_provincia.py      # Scraper específico para Banco Provincia (Cuenta DNI)
│   ├── banco_macro.py          # Scraper específico para Banco Macro
│   └── generic.py              # Scraper general/fallback con filtro semántico de dos fases
│
└── utils/
    └── display.py              # Renderizado visual de reportes usando Rich
```

---

## 🧩 Cómo Agregar un Nuevo Scraper

Gracias al **Registry Pattern**, agregar un nuevo scraper es extremadamente simple:

1. Crea un nuevo archivo en `scrapers/` (ej: `scrapers/banco_nacion.py`).
2. Implementa una clase que herede de `BaseScraper` y decórala con `@register_scraper`.
3. Sobrescribe los métodos `matches(cls, url)` y `scrape(self)`:

```python
from scrapers.base import BaseScraper, register_scraper

@register_scraper
class BancoNacionScraper(BaseScraper):
    @classmethod
    def matches(cls, url: str) -> bool:
        # Devuelve True si este scraper puede procesar la URL
        return "bna.com.ar" in url

    def scrape(self) -> list:
        # Implementa la lógica de extracción con BeautifulSoup
        html = self.fetch()
        ...
        return promos # Retorna una lista de diccionarios de promociones
```

4. Agrégalo al archivo `scrapers/__init__.py` para que se registre automáticamente al arrancar la aplicación.
