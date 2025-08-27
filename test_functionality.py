# test_functionality_simple.py
"""
Script para testear automáticamente la funcionalidad requerida (versión simplificada)
"""
import os
import random
import sys
import requests
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

RANDOM_NUM = random.randint(0, 9999);

# Configurar Django
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sistema_Paquetes.settings')

try:
    import django
    django.setup()
except Exception as e:
    logger.error(f"Error al configurar Django:\n {e}")
    sys.exit(1)


class APITestError(Exception):
    pass


class TestAPIClient:
    """Cliente para hacer llamadas HTTP a la API"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000/api/"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        
        url = urljoin(self.base_url, endpoint)
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise APITestError(f"GET {url} failed:\n {e}")
    
    def post(self, endpoint: str, data: Dict) -> requests.Response:
       
        url = urljoin(self.base_url, endpoint)
        try:
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise APITestError(f"POST {url} failed:\n {e}")
    
    def put(self, endpoint: str, data: Dict) -> requests.Response:
        
        url = urljoin(self.base_url, endpoint)
        try:
            response = self.session.put(url, json=data, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise APITestError(f"PUT {url} failed:\n {e}")


class FunctionalityTester:
    """Testeador de funcionalidades específicas"""
    
    def __init__(self, api_client: TestAPIClient):
        self.api = api_client
    
    def test_list_paquetes(self) -> bool:
        """Testea endpoint de listado de paquetes con filtros"""
        logger.info("Testeando endpoint de listado de paquetes...")
        
        try:
            # Testear listado básico
            response = self.api.get("paquetes/")
            if response.status_code == 200:
                paquetes = response.json()
                logger.info(f"+ Endpoint listado funciona - {len(paquetes)} paquetes obtenidos")
                
                # Testear filtro por estado
                response = self.api.get("paquetes/", params={"estado": "en_deposito"})
                if response.status_code == 200:
                    paquetes_filtrados = response.json()
                    logger.info(f"+ Filtro por estado funciona - {len(paquetes_filtrados)} paquetes en depósito")
                
                # Testear filtro por cliente
                try:
                    from app_paquetes.models import Cliente
                    primer_cliente = Cliente.objects.first()
                    if primer_cliente:
                        response = self.api.get("paquetes/", params={"cliente": primer_cliente.id})
                        if response.status_code == 200:
                            paquetes_cliente = response.json()
                            logger.info(f"+ Filtro por cliente funciona - {len(paquetes_cliente)} paquetes del cliente")
                except:
                    pass
                
                return True
            else:
                logger.error(f"- Error en listado de paquetes: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"- Error en test listado de paquetes:\n {e}")
            return False
    
    def test_create_paquete(self) -> bool:
        """Testea endpoint de creación de paquete"""
        logger.info("Testeando endpoint de creación de paquete...")
        
        try:
            # Primero obtenemos un cliente existente
            from app_paquetes.models import Cliente
            cliente = Cliente.objects.first()
            if not cliente:
                logger.error("- No hay clientes disponibles para crear paquete")
                return False
            nuevo_paquete = {
                "tracking": f"TEST{RANDOM_NUM}_CREATED",
                "direccion_destinatario": "Calle de prueba 123",
                "telefono_destinatario": "999888777",
                "nombre_destinatario": "Test Usuario",
                "peso": 1500.0,  # 1500g - mediano
                "altura": 15.0,
                "cliente": cliente.id
            }
            
            logger.info(f"Enviando datos de paquete: {nuevo_paquete}")
            
            response = self.api.post("paquetes/crear/", nuevo_paquete)
            if response.status_code == 201:
                paquete_creado = response.json()
                logger.info(f"+ Paquete creado exitosamente")
                logger.info(f"+ Tipo determinado automáticamente: {paquete_creado.get('tipo', 'Desconocido')}")
                logger.info(f"+ Peso: {paquete_creado.get('peso')}g")
                logger.info(f"+ Tracking: {paquete_creado.get('tracking')}")
                return True
            else:
                logger.error(f"- Error creando paquete: {response.status_code}")
                logger.error(f"- Respuesta: {response.text}")
                # Intentamos obtener detalles del error
                try:
                    error_data = response.json()
                    logger.error(f"- Detalles del error:\n {error_data}")
                except:
                    pass
                return False
                
        except Exception as e:
            logger.error(f"- Error en test creación de paquete:\n {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_assign_paquetes_planilla(self) -> bool:
        """Testea asignación de paquetes a planilla"""
        logger.info("Testeando asignación de paquetes a la primera planilla...")
        
        try:
            # Usar planilla existente en lugar de crear una nueva
            from app_paquetes.models import Planilla
            planilla = Planilla.objects.first()
            if not planilla:
                logger.warning("! No hay planillas disponibles para testear asignación")
                return True
            
            # Intentar asignar paquete a planilla
            from app_paquetes.models import Paquete
            paquete_en_deposito = Paquete.objects.filter(estado=Paquete.EstadoPaquete.EN_DEPOSITO).first()
            
            if paquete_en_deposito:
                asignacion_data = {
                    "planilla_id": planilla.id
                }
                
                response = self.api.put(
                    f"paquetes/{paquete_en_deposito.id}/asignar-planilla/",
                    asignacion_data
                )
                
                if response.status_code == 200:
                    logger.info(f"+ Paquete asignado a planilla exitosamente")
                    return True
                else:
                    logger.error(f"- Error asignando paquete: {response.status_code}")
                    logger.error(f"- Respuesta: {response.text}")
                    return False
            else:
                logger.warning("! No hay paquetes en depósito para testear asignación")
                return True
                
        except Exception as e:
            logger.error(f"- Error en test asignación de paquetes:\n {e}")
            return False
    
    def test_planilla_resumen(self) -> bool:
        """Testea endpoint de resumen de planilla"""
        logger.info("Testeando resumen de planilla...")
        
        try:
            from app_paquetes.models import Planilla
            planilla = Planilla.objects.first()
            if planilla:
                response = self.api.get(f"planillas/{planilla.id}/")
                if response.status_code == 200:
                    resumen = response.json()
                    logger.info(f"+ Resumen de planilla obtenido")
                    logger.info(f"+ Planilla: {resumen.get('numero_planilla')}")
                    logger.info(f"+ Items: {len(resumen.get('items', []))}")
                    return True
                else:
                    logger.error(f"- Error obteniendo resumen: {response.status_code}")
                    logger.error(f"- Respuesta: {response.text}")
                    return False
            else:
                logger.warning("! No hay planillas para testear resumen")
                return True
                
        except Exception as e:
            logger.error(f"- Error en test resumen de planilla:\n {e}")
            return False
    
    def test_distribuir_paquetes(self) -> bool:
        """Testea cambio a estado 'en distribución'"""
        logger.info("Testeando cambio a estado 'en distribución'...")
        
        try:
            from app_paquetes.models import Planilla
            planilla = Planilla.objects.first()
            if planilla:
                # Corregido: ahora pasamos correctamente el diccionario de datos
                distribuir_data = {}  # Datos vacíos para PUT
                response = self.api.put(f"planillas/{planilla.id}/distribuir/", distribuir_data)
                if response.status_code == 200:
                    resultado = response.json()
                    logger.info(f"+ Paquetes cambiados a distribución")
                    logger.info(f"+ Paquetes actualizados: {resultado.get('paquetes_actualizados', 0)}")
                    return True
                else:
                    logger.error(f"- Error cambiando estado: {response.status_code}")
                    logger.error(f"- Respuesta: {response.text}")
                    return False
            else:
                logger.warning("! No hay planillas para testear distribución")
                return True
                
        except Exception as e:
            logger.error(f"- Error en test distribución:\n {e}")
            return False
    
    def test_asignar_motivo_fallo(self) -> bool:
        """Testea asignación de motivo de fallo"""
        logger.info("Testeando asignación de motivo de fallo...")
        
        try:
            from app_paquetes.models import Item, MotivoFalloSimple
            item = Item.objects.first()
            if item:
                motivo_simple = MotivoFalloSimple.objects.first()
                if motivo_simple:
                    asignacion_data = {
                        "motivo_fallo_id": motivo_simple.id
                    }
                    
                    response = self.api.put(
                        f"items/{item.id}/asignar-motivo/",
                        asignacion_data
                    )
                    
                    if response.status_code == 200:
                        resultado = response.json()
                        logger.info(f"+ Motivo de fallo asignado exitosamente")
                        logger.info(f"+ Motivo: {motivo_simple.nombre}")
                        return True
                    else:
                        logger.error(f"- Error asignando motivo: {response.status_code}")
                        logger.error(f"- Respuesta: {response.text}")
                        return False
                else:
                    logger.warning("! No hay motivos simples para testear")
                    return True
            else:
                logger.warning("! No hay ítems para testear asignación de motivos")
                return True
                
        except Exception as e:
            logger.error(f"- Error en test asignación de motivos:\n {e}")
            return False
    
    def test_bulk_assignment(self) -> bool:
        """Testea asignación bulk de paquetes"""
        logger.info("Testeando asignación bulk de paquetes...")
        
        try:
            from app_paquetes.models import Planilla, Paquete
            planilla = Planilla.objects.first()
            if planilla:
                paquetes = Paquete.objects.filter(estado=Paquete.EstadoPaquete.EN_DEPOSITO)[:2]
                if paquetes:
                    paquete_ids = [p.id for p in paquetes]
                    bulk_data = {
                        "paquete_ids": paquete_ids,
                        "planilla_id": planilla.id
                    }
                    
                    print("body:" , bulk_data)
                    response = self.api.post("paquetes/bulk-asignar-planilla/", bulk_data)
                    if response.status_code == 200:
                        resultado = response.json()
                        logger.info(f"+ Asignación bulk exitosa")
                        logger.info(f"+ Paquetes asignados: {resultado.get('items_creados', 0)}")
                        return True
                    else:
                        logger.error(f"- Error en asignación bulk: {response.status_code}")
                        logger.error(f"- Respuesta: {response.text}")
                        return False
                else:
                    logger.warning("! No hay suficientes paquetes para testear bulk assignment")
                    return True
            else:
                logger.warning("! No hay planillas para testear bulk assignment")
                return True
                
        except Exception as e:
            logger.error(f"- Error en test bulk assignment:\n {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Ejecuta todos los tests"""
        logger.info("Iniciando testeo de todas las funcionalidades...")
        
        tests = [
            ("Listado de paquetes", self.test_list_paquetes),
            ("Creación de paquetes", self.test_create_paquete),
            ("Asignación a planilla", self.test_assign_paquetes_planilla),
            ("Resumen de planilla", self.test_planilla_resumen),
            ("Distribución de paquetes", self.test_distribuir_paquetes),
            ("Asignación de motivos", self.test_asignar_motivo_fallo),
            ("Asignación bulk", self.test_bulk_assignment),
        ]
        
        results = []
        for test_name, test_func in tests:
            logger.info(f"\n--- {test_name} ---")
            try:
                result = test_func()
                results.append((test_name, result))
                if result:
                    logger.info(f"+ {test_name}: PASSED")
                else:
                    logger.error(f"- {test_name}: FAILED")
            except Exception as e:
                logger.error(f"- {test_name}: ERROR - {e}")
                import traceback
                traceback.print_exc()
                results.append((test_name, False))
        
        # Mostrar resultados finales
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        logger.info("\n=== RESULTADOS FINALES ===")
        for test_name, result in results:
            status = "PASS" if result else "FAIL"
            logger.info(f"{status}: {test_name}")
        
        logger.info(f"\nTotal: {passed}/{total} tests pasaron")


def main():
    """Función principal del script de testeo"""
    
    try:
        # Crear cliente API
        api_client = TestAPIClient()
        
        # Ejecutar tests
        tester = FunctionalityTester(api_client)
        success = tester.run_all_tests()
            
    except APITestError as e:
        logger.error(f"Error en testeo:\n {e}")
        return 1
    except Exception as e:
        logger.error(f"Error inesperado:\n {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())