# 📦 Sistema de Gestión de Paquetes

Sistema para sistematizar el seguimiento y gestión de paquetes en depósitos, con soporte para planillas de distribución, motivos de fallo y estadísticas.

### 🛠️ Tecnologías

- **Python 3.10+**
- **Django 5.2+** - Framework web de alto nivel
- **Django REST Framework** - API RESTful
- **SQLite** - Base de datos por defecto

## Instalación y Ejecucion del Proyecto en máquina virtual
Crear entorno virtual:
```
python -m venv venv
source venv/bin/activate # Linux/Mac
```
 o
```
venv\Scripts\activate # Windows
```

Instalar dependencias:
```
pip install -r requirements.txt
```

Configurar base de datos:
```
python manage.py makemigrations
python manage.py migrate

python manage.py runserver
```


## Scripts de Carga de Datos y Testeo

- load_test_data.py:
  Carga automáticamente datos de prueba
  Crea usuarios, clientes, paquetes, planillas y motivos de fallo

- test_functionality.py
  Testeo automatizado de todas las funcionalidades
  Verificación de endpoints REST
  Validación de reglas de negocio
  Validación de datos en modelos y vistas
  Log completo de los resultados

## Endpoints - TODO: update

Paquetes
GET /api/paquetes/ - Listar paquetes (filtrable por estado, cliente, tipo)
POST /api/paquetes/ - Crear paquete (tipo calculado automáticamente por peso)

Planillas
POST /api/planillas/{id}/assign-packages/ - Asignar paquetes a planilla (límite 25kg)
GET /api/planillas/{id}/summary/ - Resumen de planilla con paquetes
POST /api/planillas/{id}/mark-distribution/ - Marcar paquetes como "en distribución"

Motivos de fallo
GET /api/motivos-fallo/ - Listar motivos (simples y compuestos)


## 📋 Descripción

### Estructura de Modelos

Modelo Cliente
Responsabilidad: Almacena información básica de clientes
Justificación: Separación clara de datos de contacto y dirección

Modelo Paquete
Gestiona información de paquetes con validaciones de negocio
Tipado automático basado en peso mediante método \_determinar_tipo()
Validación de peso mayor a cero en clean()
Estados controlados con EstadoPaquete (enum)

Modelo Planilla
Gestiona colecciones de paquetes para distribución
Método marcar_paquetes_en_distribucion() para batch processing
Verificación de límite de peso (25kg) con verificar_limite_peso()
Propiedad peso_total para cálculos eficientes

Modelo Item
Responsabilidad: Relación entre paquetes y planillas - Se encarga de la Validación de paquetes en estado "en depósito"
Evita asignación múltiple de paquetes

Modelo MotivoFallo (Abstracto)
Responsabilidad: Interfaz base para motivos de fallo

Facilita extensión futura con motivos compuestos
Modelos MotivoFalloSimple y MotivoFalloCompuesto - Implementación concreta de motivos de fallo

MotivoFalloSimple: Motivos individuales con estado activo
MotivoFalloCompuesto: Futura combinación de motivos simples y compuestos

### Características Principales

1. Gestión de Paquetes
   Creación automática de tipo basada en peso
   Filtrado por estado, cliente y tipo
2. Gestión de Planillas
   Asignación de múltiples paquetes
   Límite de peso de 25kg por planilla
   Cambio masivo de estado a "en distribución"
3. Gestión de Motivos de Fallo
   Asignación de motivos a ítems
   Validación de motivos activos
   Soporte para motivos simples y compuestos
4. Endpoints 
   Listado de paquetes con filtros
   Creación de paquetes con tipo automático
   Asignación de paquetes a planillas
   Resumen de planillas
   Distribución de paquetes
   Asignación de motivos de fallo
   Asignación bulk de paquetes


### Posibles Próximos Pasos
Dockerisar el proyecto y sus requerimientos
Agregar tests unitarios completos
Realizar documentación API con Swagger
Implementar cacheo para consultas frecuentes
Agregar funcionalidad de reportes

### 📄 `requirements.txt`

```txt

```
