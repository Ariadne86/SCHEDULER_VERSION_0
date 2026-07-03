# Programación de Producción - Área de Prensas

Aplicación para programar órdenes de producción en prensas industriales con soporte para múltiples pisos por prensa.

## Características

- **Prensas con 2 pisos**: Cada prensa tiene dos compartimientos independientes
- **Emparejamiento inteligente**: Optimiza el uso combinando órdenes compatibles en los dos pisos
- **Restricciones de compatibilidad**:
  - Diferencia de tiempo máxima: 50% del menor tiempo
  - Diferencia de presión máxima: 20 PSI
  - Verificación de dimensiones por prensa

## Estructura del Proyecto

```
├── app.py                    # Aplicación principal Streamlit
├── requirements.txt          # Dependencias
├── ejemplo_ordenes.py        # Script para generar Excel de ejemplo
├── config/
│   └── prensas.py            # Configuración de prensas y restricciones
├── src/
│   └── scheduler.py          # Lógica de programación con pisos
└── datos/
    └── ejemplo_ordenes.xlsx  # Archivo de ejemplo
```

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
streamlit run app.py
```

Para generar el archivo de ejemplo:
```bash
python ejemplo_ordenes.py
```

## Formato del Archivo Excel

| Columna         | Descripción                    | Requerido |
|-----------------|--------------------------------|-----------|
| id              | Identificador único de orden   | Sí        |
| dim_x           | Dimensión X en mm              | Sí        |
| dim_y           | Dimensión Y en mm              | Sí        |
| cantidad        | Cantidad a producir            | Sí        |
| tiempo_unitario | Horas por unidad               | Sí        |
| presion_psi     | Presión en PSI                 | No        |
| prioridad       | Prioridad (1=alta, 5=baja)     | No        |

## Prensas Configuradas

| Prensa | Dimensiones   | Costo/hora | Pisos |
|--------|---------------|------------|-------|
| P1     | 1200x600 mm   | 50 EUR     | 2     |
| P2     | 1200x600 mm   | 50 EUR     | 2     |
| P5     | 1500x600 mm   | 60 EUR     | 2     |
| P6     | 1800x800 mm   | 75 EUR     | 2     |
| P7     | 2000x2000 mm  | 100 EUR    | 2     |

## Reglas de Emparejamiento

Dos órdenes pueden procesarse simultáneamente en los pisos de una misma prensa si:

1. **Tiempo**: La diferencia de tiempo de prensado es ≤ 50% del menor tiempo
   - Ejemplo: 2h y 2.8h son compatibles (40% diferencia)
   - Ejemplo: 2h y 1h NO son compatibles (100% diferencia)

2. **Presión**: La diferencia de presión es ≤ 20 PSI
   - Ejemplo: 100 PSI y 115 PSI son compatibles
   - Ejemplo: 100 PSI y 130 PSI NO son compatibles

3. **Dimensiones**: Ambas órdenes caben en la prensa

## Algoritmo de Asignación

Las órdenes se procesan por:
1. Prioridad (menor número primero)
2. Tiempo total (mayor primero, para maximizar emparejamiento)

Cuando se programa una orden:
1. Se busca un ciclo existente donde pueda emparejarse
2. Si no encuentra, inicia un ciclo nuevo en un piso libre
3. Verifica todas las restricciones de compatibilidad

## Funcionalidades

- Carga de órdenes desde Excel
- Validación automática de datos
- Visualización de compatibilidad de prensas
- Métricas de emparejamiento y eficiencia
- Diagrama de Gantt por piso
- Carga y utilización por prensa
- Exportación a CSV
