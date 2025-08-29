
# load_test_data.py
"""
Script para cargar datos de prueba automáticamente en la base de datos
"""
import os
import subprocess
import sys
import django
from django.conf import settings

# Configurar Django
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sistema_Paquetes.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error al configurar Django:\n {e}")
    sys.exit(1)

def run_command(command):
    """Ejecuta un comando de shell y verifica si falló"""
    print(f"____ Ejecutando: {command} ____\n")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error al ejecutar: {command}")
        sys.exit(1)
        return False
    return True

def load_test_data():
    """Carga automáticamente datos de prueba en la base de datos"""
    
    try:
        from app_paquetes.models import (
            Cliente, Paquete, Planilla, Item, 
            MotivoFalloSimple
        )
        from django.contrib.auth.models import User
        
        print("=== CARGA AUTOMÁTICA DE DATOS DE PRUEBA ===\n")
        

        print("1. Creando usuario administrador...")
        try:
            admin_user = User.objects.get(username='admin')
            print("   ✓ Usuario administrador ya existe")
        except User.DoesNotExist:
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
            print("   ✓ Usuario administrador creado")
        

        print("2. Creando clientes...")
        clientes_data = [
            {"nombre": "Juan Pérez", "email": "juan@example.com", "telefono": "123456789", "direccion": "Calle Principal 123"},
            {"nombre": "María García", "email": "maria@example.com", "telefono": "987654321", "direccion": "Avenida Secundaria 456"},
            {"nombre": "Carlos López", "email": "carlos@example.com", "telefono": "456789123", "direccion": "Plaza Central 789"},
        ]
        
        clientes = []
        for cliente_data in clientes_data:
            cliente, created = Cliente.objects.get_or_create(**cliente_data)
            if created:
                print(f"   ✓ Cliente creado: {cliente.nombre}")
            else:
                print(f"   ✓ Cliente existente: {cliente.nombre}")
            clientes.append(cliente)
        

        print("3. Creando motivos de fallo simples...")
        motivos_simples_data = [
            {
                "codigo": "MP001",
                "nombre": "Paquete dañado",
                "descripcion": "El paquete presenta daños visibles en su envoltura",
                "active": True
            },
            {
                "codigo": "MP002",
                "nombre": "Dirección incorrecta",
                "descripcion": "La dirección del destinatario es incorrecta o incompleta",
                "active": True
            },
            {
                "codigo": "MP003",
                "nombre": "Peso excesivo",
                "descripcion": "El paquete excede el peso máximo permitido",
                "active": True
            },
            {
                "codigo": "MP004",
                "nombre": "Información incompleta",
                "descripcion": "Faltan datos importantes en la etiqueta del paquete",
                "active": True
            }
        ]
        
        motivos_simples = []
        for motivo_data in motivos_simples_data:
            motivo, created = MotivoFalloSimple.objects.get_or_create(**motivo_data)
            if created:
                print(f"   ✓ Motivo simple creado: {motivo.nombre}")
            else:
                print(f"   ✓ Motivo simple existente: {motivo.nombre}")
            motivos_simples.append(motivo)
        

        print("5. Creando paquetes...")
        paquetes_data = [
            {
                "tracking": "TRK001",
                "direccion_destinatario": "Calle Principal 123",
                "telefono_destinatario": "123456789",
                "nombre_destinatario": "Juan Pérez",
                "peso": 500.0,  # 500g - pequeño
                "altura": 10.0,
                "cliente": clientes[0],
                "estado": Paquete.EstadoPaquete.EN_DEPOSITO
            },
            {
                "tracking": "TRK002",
                "direccion_destinatario": "Avenida Secundaria 456",
                "telefono_destinatario": "987654321",
                "nombre_destinatario": "María García",
                "peso": 2500.0,  # 2500g - mediano
                "altura": 15.0,
                "cliente": clientes[1],
                "estado": Paquete.EstadoPaquete.EN_DEPOSITO
            },
            {
                "tracking": "TRK003",
                "direccion_destinatario": "Plaza Central 789",
                "telefono_destinatario": "456789123",
                "nombre_destinatario": "Carlos López",
                "peso": 4000.0,  # 4000g - grande
                "altura": 20.0,
                "cliente": clientes[2],
                "estado": Paquete.EstadoPaquete.EN_DEPOSITO
            },
            {
                "tracking": "TRK004",
                "direccion_destinatario": "Calle Secundaria 321",
                "telefono_destinatario": "321654987",
                "nombre_destinatario": "Ana Martínez",
                "peso": 800.0,  # 800g - pequeño
                "altura": 12.0,
                "cliente": clientes[0],
                "estado": Paquete.EstadoPaquete.EN_DEPOSITO
            },
            {
                "tracking": "TRK005",
                "direccion_destinatario": "Avenida Principal 654",
                "telefono_destinatario": "654321987",
                "nombre_destinatario": "Luis Rodríguez",
                "peso": 3500.0,  # 3500g - grande
                "altura": 18.0,
                "cliente": clientes[1],
                "estado": Paquete.EstadoPaquete.EN_DEPOSITO
            }
        ]
        
        paquetes = []
        for paquete_data in paquetes_data:
            paquete, created = Paquete.objects.get_or_create(
                tracking=paquete_data["tracking"],  # Buscar por tracking (único)
                defaults=paquete_data  # Crear con todos los datos si no existe
            )            
            if created:
                print(f"   ✓ Paquete creado: {paquete.tracking} - {paquete.nombre_destinatario}")
            else:
                print(f"   ✓ Paquete existente: {paquete.tracking} - {paquete.nombre_destinatario}")
            paquetes.append(paquete)
        

        print("6. Creando planillas...")
        planillas_data = [
            {
                "numero_planilla": "PLN001",
            },
            {
                "numero_planilla": "PLN002",
            }
        ]
        
        planillas = []
        for planilla_data in planillas_data:
            planilla, created = Planilla.objects.get_or_create(**planilla_data)
            if created:
                print(f"   ✓ Planilla creada: {planilla.numero_planilla}")
            else:
                print(f"   ✓ Planilla existente: {planilla.numero_planilla}")
            planillas.append(planilla)
        
        
        print("7. Asignando paquetes a planillas...")
        try:
            # Asignar primer paquete a primera planilla
            item1, created1 = Item.objects.get_or_create(
                planilla=planillas[0],
                paquete=paquetes[0],
                defaults={'posicion': 1} 
            )
            accion = "creado" if created1 else "existente"
            print(f"   ✓ Paquete {paquetes[0].tracking} {accion} en planilla {planillas[0].numero_planilla} (posición {item1.posicion})")
            
            # Asignar segundo y tercer paquete a segunda planilla
            item2, created2 = Item.objects.get_or_create(
                planilla=planillas[1],
                paquete=paquetes[1],
                defaults={'posicion': 1}
            )
            accion = "creado" if created2 else "existente"
            print(f"   ✓ Paquete {paquetes[1].tracking} {accion} en planilla {planillas[1].numero_planilla} (posición {item2.posicion})")
            
            item3, created3 = Item.objects.get_or_create(
                planilla=planillas[1],
                paquete=paquetes[2],
                defaults={'posicion': 2}
            )
            accion = "creado" if created3 else "existente"
            print(f"   ✓ Paquete {paquetes[2].tracking} {accion} en planilla {planillas[1].numero_planilla} (posición {item3.posicion})")
            
            # Asignar cuarto paquete a primera planilla
            item4, created4 = Item.objects.get_or_create(
                planilla=planillas[0],
                paquete=paquetes[3],
                defaults={'posicion': 2}  # ← Siguiente posición disponible
            )
            accion = "creado" if created4 else "existente"
            print(f" Paquete {paquetes[3].tracking} {accion} en planilla {planillas[0].numero_planilla} (posición {item4.posicion})")

        except Exception as e:
            print(f" --> Error asignando paquetes a planillas:\n {e}")
        
        print("8. Asignando motivos de fallo a ítems...")
        try:
            if len(paquetes) >= 2 and len(motivos_simples) >= 1:
                # Asignar motivo simple a primer ítem
                item_con_motivo = Item.objects.first()
                if item_con_motivo:
                    item_con_motivo.motivo_fallo = motivos_simples[0]
                    item_con_motivo.save()
                    print(f"   ✓ Motivo asignado al ítem {item_con_motivo.id}")
            
           
        except Exception as e:
            print(f" --> Error asignando motivos de fallo:\n {e}")
        
        print("\n____RESUMEN DE DATOS CREADOS____")
        print(f"Usuarios: 1")
        print(f"Clientes: {len(clientes)}")
        print(f"Paquetes: {len(paquetes)}")
        print(f"Planillas: {len(planillas)}")
        print(f"Motivos simples: {len(motivos_simples)}")
        print(f"Ítems: {Item.objects.count()}")
                
        return True
        
    except Exception as e:
        print(f"Error al cargar datos de prueba:\n {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n____ Paso 1: Creación de migraciones ____")
    if run_command("python manage.py makemigrations"):
        print("\n____ Paso 2: Aplicación de migraciones ____")
        run_command("python manage.py migrate")

    print("Iniciando carga automática de datos de prueba")
    success = load_test_data()
    
    if not success:
        print("\n!! error al cargar datos!!")
        sys.exit(1)
