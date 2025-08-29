# 📦 Sistema de Gestión de Paquetes - Package Management System

Sistema para sistematizar el seguimiento y gestión de paquetes en depósitos, con soporte para planillas de distribución, motivos de fallo y estadísticas.

### 🛠️ Tecnologías - Technologies

- **Python 3.10+**
- **Django 5.2+** - Framework web de alto nivel
- **Django REST Framework** - API RESTful
- **SQLite** - Base de datos por defecto

## Instalación y Ejecucion del Proyecto - Project Instalation and Execution
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

## Alternative - Run the project with Docker:
```
docker-compose up --build
```
or, in background: 
```
docker-compose up -d
```

## Scripts de Carga de Datos y Testeo - Data Loading and Testing Scripts

- load_test_data.py:
  Carga automáticamente datos de prueba
  Crea usuarios, clientes, paquetes, planillas y motivos de fallo
```
python load_test_data.py
```

- test_functionality.py
  Testeo automatizado de todas las funcionalidades
  Verificación de endpoints REST
  Validación de reglas de negocio
  Validación de datos en modelos y vistas
  Log completo de los resultados

```
python test_functionality.py
```

## Endpoints

### Paquetes
GET /api/paquetes/ - Listar paquetes (filtrable por estado, cliente, tipo)
POST /api/paquetes/create/ - Crear paquete (tipo calculado automáticamente por peso)
POST paquetes/<int:pk>/assign-planilla/ - asigna un unico paquete a una planilla
POST paquetes/bulk-assign-planilla/ - asigna varios paquetes a una planilla


### Planillas
GET /api/planillas/{id}/summary/ - Resumen de planilla con paquetes
POST /api/planillas/{id}/mark-distribution/ - Marcar paquetes como "en distribución"

### Motivos de fallo
GET /api/motivos-fallo/ - Listar motivos (simples y compuestos)


## 📋 Descripción - Description

### Estructura de Modelos - Models Structure

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
MotivoFalloCompuesto (WIP): Futura combinación de motivos simples y compuestos

### Características Principales - Main Features 

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


### Próximos Pasos - Next Steps
Dockerisar el proyecto 
Centralizar toda la configuracion y constantes de la aplicacion
Traducir nombres de clases y metodos a ingles
Agregar tests unitarios mas completos con un framework
Realizar documentación completa API 
Agregar funcionalidad de reportes y estadistica
