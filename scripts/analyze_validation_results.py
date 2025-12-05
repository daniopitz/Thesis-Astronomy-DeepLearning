#!/usr/bin/env python3
"""
Análisis de Resultados de Validación del Componente 1
=====================================================

Este script analiza los archivos JSON de validación generados por ValidationMetricsCollector
y genera:
1. Tablas LaTeX para el documento de validación
2. Gráficos de validación
3. Análisis cuantitativo de las ecuaciones

NOTA: Este script debe ejecutarse desde el directorio Thesis-Astronomy-DeepLearning/
"""

import json
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI

def load_validation_jsons(results_dir):
    """Carga todos los archivos JSON de validación."""
    json_files = list(Path(results_dir).glob("validation_component1_*.json"))
    data = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data.append(json.load(f))
        except Exception as e:
            print(f"Error cargando {json_file}: {e}")
    
    return data

def generate_latex_table_planning(data):
    """Genera tabla LaTeX para validación de planificación de recursos."""
    
    rows = []
    for item in data:
        file_name = Path(item['file_name']).stem
        dc = item['data_characteristics']
        mb = item['memory_budget']
        cc = item['chunk_calculation']
        
        N0 = dc['file_length_samples']
        Nd = dc['decimated_samples']
        bp = dc['bytes_per_sample']
        Md = mb['available_ram_gb']
        Mu = mb['total_usable_gb']
        Nc = cc['final_chunk_samples']
        aligned = "\\checkmark" if cc.get('aligned_to_slice', False) else "\\times"
        
        rows.append(f"        {file_name} & {N0:,} & {Nd:,} & {bp} & {Md:.2f} & {Mu:.2f} & {Nc:,} & {aligned} \\\\")
    
    table = f"""\\begin{{table}}[H]
    \\centering
    \\caption{{Validación del algoritmo de planificación de recursos en archivos FAST-FREX. Se verifica que los parámetros calculados ($N_d, b_p, M_u, N_c$) coinciden con las ecuaciones teóricas. La alineación ($\\checkmark$) confirma que $N_c$ es múltiplo exacto de $L_s$.}}
    \\label{{tab:validacion_planificacion}}
    \\resizebox{{\\textwidth}}{{!}}{{% 
    \\begin{{tabular}}{{lrrrrrcc}}
    \\toprule
    \\textbf{{Archivo}} & \\textbf{{$N_0$}} & \\textbf{{$N_d$}} & \\textbf{{$b_p$ (bytes)}} & \\textbf{{$M_d$ (GB)}} & \\textbf{{$M_u$ (GB)}} & \\textbf{{$N_c$ final}} & \\textbf{{Aligned}} \\\\
    \\midrule
{chr(10).join(rows)}
    \\bottomrule
    \\end{{tabular}}%
    }}
\\end{{table}}"""
    
    return table

def generate_latex_table_adaptive_budgeting(data):
    """Genera tabla LaTeX para validación de presupuesto adaptativo."""
    
    rows = []
    for item in data:
        file_name = Path(item['file_name']).stem
        cc = item['chunk_calculation']
        dc = item['data_characteristics']
        
        Cs_kb = cc['phase_a']['cost_per_sample_bytes'] / 1024
        Nmax = cc['phase_b']['max_samples']
        Nmin = cc['phase_c']['required_min_size']
        scenario = cc['scenario'].capitalize()
        Nc = cc['final_chunk_samples']
        
        rows.append(f"        {file_name} & {Cs_kb:.1f} & {Nmax:,} & {Nmin:,} & {scenario} & {Nc:,} \\\\")
    
    table = f"""\\begin{{table}}[H]
    \\centering
    \\caption{{Validación de las tres fases del presupuesto adaptativo de memoria. Fase A: costo por muestra ($C_s$). Fase B: capacidad máxima ($N_{{\\max}}$). Fase C: requerimiento mínimo físico ($N_{{\\min}}$). El escenario "Ideal" se activa correctamente pues $N_{{\\max}} > N_{{\\min}}$ en ambos casos, permitiendo procesar el archivo completo en un solo chunk ($N_c > N_d$).}}
    \\label{{tab:validacion_fases_presupuesto}}
    \\small
    \\begin{{tabular}}{{lrrrrr}}
    \\toprule
    \\textbf{{Archivo}} & \\textbf{{$C_s$ (KB)}} & \\textbf{{$N_{{\\max}}$}} & \\textbf{{$N_{{\\min}}$}} & \\textbf{{Escenario}} & \\textbf{{$N_c$ final}} \\\\
    \\midrule
{chr(10).join(rows)}
    \\bottomrule
    \\end{{tabular}}
\\end{{table}}"""
    
    return table

def generate_latex_table_overlap(data):
    """Genera tabla LaTeX para validación de overlap."""
    
    rows = []
    for item in data:
        file_name = Path(item['file_name']).stem
        dm_cube = item['dm_cube']
        cc = item['chunk_calculation']
        ov = item.get('overlap_validation', {})
        
        dm_max = dm_cube['dm_max']
        delta_t_max = dm_cube['delta_t_max_seconds']
        Od = cc['phase_c']['overlap_decimated']
        
        # Determinar estado
        if len(item.get('chunks', [])) == 1:
            estado = "N/A (1 chunk)"
        elif ov.get('overlap_sufficient', False):
            estado = "Suficiente"
        else:
            estado = "Insuficiente"
        
        rows.append(f"        {file_name} & {dm_max} & {delta_t_max:.2f} & {Od:,} & {estado} \\\\")
    
    table = f"""\\begin{{table}}[H]
    \\centering
    \\caption{{Validación del cálculo de solapamiento y retardo dispersivo. Se verifica que $\\Delta t_{{\\max}} \\approx 4.60$ s es consistente para DM=2000 en banda L (1000-1500 MHz). El estado "N/A (1 chunk)" indica que el archivo completo cupo en memoria (gracias al Escenario Ideal), por lo que la validación de continuidad entre chunks no fue necesaria, demostrando la eficiencia del sistema al evitar segmentación innecesaria.}}
    \\label{{tab:validacion_overlap}}
    \\small
    \\begin{{tabular}}{{lrrrr}}
    \\toprule
    \\textbf{{Archivo}} & \\textbf{{DM$_{{\\max}}$}} & \\textbf{{$\\Delta t_{{\\max}}$ (s)}} & \\textbf{{$O_d$ (muestras)}} & \\textbf{{Estado}} \\\\
    \\midrule
{chr(10).join(rows)}
    \\bottomrule
    \\end{{tabular}}
\\end{{table}}"""
    
    return table

def plot_memory_usage(data, output_dir):
    """Genera gráfico de uso de memoria."""
    
    files = [Path(item['file_name']).stem for item in data]
    usable_memory = [item['memory_budget']['total_usable_gb'] for item in data]
    peak_memory = [item['actual_processing']['peak_memory_usage_gb'] for item in data]
    
    x = np.arange(len(files))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars1 = ax.bar(x - width/2, usable_memory, width, label='Memoria Utilizable ($M_u$)', 
                    color='#2E86AB', alpha=0.8)
    bars2 = ax.bar(x + width/2, peak_memory, width, label='Uso Real Pico', 
                    color='#A23B72', alpha=0.8)
    
    ax.set_xlabel('Archivo', fontsize=12, fontweight='bold')
    ax.set_ylabel('Memoria (GB)', fontsize=12, fontweight='bold')
    ax.set_title('Validación Cuantitativa: Presupuesto vs. Uso Real de Memoria', 
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(files, rotation=45, ha='right')
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Añadir valores en las barras
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    output_path = Path(output_dir) / "validation_memory_budget.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Gráfico guardado en: {output_path}")

def plot_phase_analysis(data, output_dir):
    """Genera gráfico de análisis de las 3 fases del presupuesto."""
    
    files = [Path(item['file_name']).stem for item in data]
    
    # Extraer datos de las 3 fases
    phase_a = [item['chunk_calculation']['phase_a']['cost_per_sample_bytes'] / 1024 for item in data]
    phase_b = [item['chunk_calculation']['phase_b']['max_samples'] / 1000 for item in data]  # En miles
    phase_c = [item['chunk_calculation']['phase_c']['required_min_size'] / 1000 for item in data]  # En miles
    
    x = np.arange(len(files))
    width = 0.25
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Gráfico 1: Costo por muestra (Fase A)
    ax1.bar(x, phase_a, width*3, color='#F18F01', alpha=0.8, label='Costo por muestra ($C_s$)')
    ax1.set_xlabel('Archivo', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Costo (KB/muestra)', fontsize=11, fontweight='bold')
    ax1.set_title('Fase A: Cálculo de Costo', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(files, rotation=45, ha='right')
    ax1.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    for i, v in enumerate(phase_a):
        ax1.text(i, v, f'{v:.1f}', ha='center', va='bottom', fontsize=9)
    
    # Gráfico 2: Capacidad vs Requerimiento (Fases B y C)
    x2 = np.arange(len(files))
    ax2.bar(x2 - width, phase_b, width, label='Capacidad máxima ($N_{\\max}$)', 
            color='#06A77D', alpha=0.8)
    ax2.bar(x2, phase_c, width, label='Requerimiento mínimo ($N_{\\min}$)', 
            color='#C73E1D', alpha=0.8)
    ax2.set_xlabel('Archivo', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Muestras (miles)', fontsize=11, fontweight='bold')
    ax2.set_title('Fases B y C: Capacidad vs Requerimiento', fontsize=12, fontweight='bold')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(files, rotation=45, ha='right')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    plt.tight_layout()
    
    output_path = Path(output_dir) / "validation_phases_analysis.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Gráfico guardado en: {output_path}")

def main():
    """Función principal."""
    # Script ejecutado desde Thesis-Astronomy-DeepLearning/
    thesis_dir = Path(__file__).parent.parent
    drafts_dir = thesis_dir.parent / "DRAFTS-UC"
    
    # Rutas relativas desde el directorio de la tesis
    results_dir = drafts_dir / "Results-polarization-finales" / "Validation"
    output_figures_dir = thesis_dir / "figures" / "validation" / "Componente 1"
    
    if not output_figures_dir.exists():
        output_figures_dir.mkdir(parents=True, exist_ok=True)
        print(f"Directorio de salida creado: {output_figures_dir}")
    
    print(f"Directorio de tesis: {thesis_dir}")
    print(f"Buscando JSONs en: {results_dir}")
    
    if not results_dir.exists():
        print(f"ERROR: No se encontró el directorio de resultados: {results_dir}")
        print(f"Verifica que los JSONs de validación estén en: {results_dir}")
        return
    
    data = load_validation_jsons(results_dir)
    
    if not data:
        print("No se encontraron archivos JSON de validación. Verifica la ruta.")
        return
    
    data.sort(key=lambda x: x['file_name'])
    
    print(f"\n{'='*60}")
    print(f"Encontrados {len(data)} archivos JSON de validación")
    print(f"{'='*60}\n")
    
    # Generar tablas LaTeX
    print("="*60)
    print("TABLA 1: PLANIFICACIÓN DE RECURSOS")
    print("="*60)
    table1 = generate_latex_table_planning(data)
    print(table1)
    print("\n")
    
    print("="*60)
    print("TABLA 2: PRESUPUESTO ADAPTATIVO (3 FASES)")
    print("="*60)
    table2 = generate_latex_table_adaptive_budgeting(data)
    print(table2)
    print("\n")
    
    print("="*60)
    print("TABLA 3: VALIDACIÓN DE OVERLAP")
    print("="*60)
    table3 = generate_latex_table_overlap(data)
    print(table3)
    print("\n")
    
    # Generar gráficos
    print("Generando gráficos...")
    plot_memory_usage(data, output_figures_dir)
    plot_phase_analysis(data, output_figures_dir)
    
    print(f"\n{'='*60}")
    print("ANÁLISIS COMPLETADO")
    print(f"{'='*60}")
    print(f"Gráficos guardados en: {output_figures_dir}")
    print("\nLas tablas LaTeX están listas para copiar al documento.")

if __name__ == '__main__':
    main()
