from django.conf import settings

class PaqueteUtils:
    """Utilidades para la lógica de paquetes"""
    
    @staticmethod
    def obtener_limites():
        """Obtiene los límites actuales de configuración"""
        return {
            'peso_pequeno_max': 1000,
            'peso_mediano_max': 3000,
            'peso_planilla_max': 25000
        }
    
    @staticmethod
    def determinar_tipo_paquete(peso):
        """Determina el tipo de paquete según los límites actuales"""
        limites = PaqueteUtils.obtener_limites()
        
        if peso < limites['peso_pequeno_max']:
            return 'P'
        elif peso < limites['peso_mediano_max']:
            return 'M'
        else:
            return 'G'
    
    @staticmethod
    def verificar_limite_planilla(planilla, peso_a_agregar):
        """Verifica si se excedería el límite de peso de la planilla"""
        limites = PaqueteUtils.obtener_limites()
        peso_actual = planilla.obtener_peso_total()
        return (peso_actual + peso_a_agregar) <= limites['peso_planilla_max']
