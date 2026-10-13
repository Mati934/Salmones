from pathlib import Path
from statistics import fmean, pstdev

# Ajusta si la ruta a la carpeta con las secuencias es diferente
DATA_DIR = Path("C:\\src\\Segundo Semestre\\IA\\lab_15\\datasets\\salmones")

# Filtrar solo carpetas seq_* que no sean temporales ni de Mac
sequences = sorted(
    [d for d in DATA_DIR.glob("seq_*") if d.is_dir() and not d.name.startswith(".")]
)

print(f"Secuencias válidas encontradas: {len(sequences)}\n")

records = []
all_widths = []
all_heights = []
all_areas = []

for seq in sequences:
    img_dir = seq / "images"
    lbl_dir = seq / "labels"

    # Filtrar solo imágenes reales (ignorando ._* de macOS)
    images = sorted(
        [
            f
            for f in img_dir.glob("*.*")
            if f.suffix.lower() in [".jpg", ".jpeg", ".png"]
            and not f.name.startswith("._")
        ]
    )

    total_frames = len(images)
    total_boxes = 0
    empty_frames = 0

    for img in images:
        lbl_file = lbl_dir / f"{img.stem}.txt"

        if lbl_file.exists():
            with open(lbl_file, "r", encoding="utf-8") as f:
                lines = [l.strip().split() for l in f.readlines() if l.strip()]

            num_boxes = len(lines)
            if num_boxes == 0:
                empty_frames += 1
            else:
                total_boxes += num_boxes
                for item in lines:
                    if len(item) >= 5:
                        w = float(item[3])
                        h = float(item[4])
                        all_widths.append(w)
                        all_heights.append(h)
                        all_areas.append(w * h)
        else:
            empty_frames += 1

    avg_boxes = (total_boxes / total_frames) if total_frames > 0 else 0.0

    records.append(
        {
            "secuencia": seq.name,
            "cuadros": total_frames,
            "cajas": total_boxes,
            "promedio": avg_boxes,
            "vacios": empty_frames,
        }
    )

# Cálculos globales
tot_frames = sum(r["cuadros"] for r in records)
tot_boxes = sum(r["cajas"] for r in records)
tot_empty = sum(r["vacios"] for r in records)
avg_global = (tot_boxes / tot_frames) if tot_frames > 0 else 0.0

# Imprimir salida lista en formato Markdown
print("### Tabla de Caracterización de Secuencias (Markdown)")
print(
    "| Secuencia | Cuadros ($N$) | Cajas Totales | Salmones / Cuadro (Media) | Cuadros Vacíos (Fondo) |"
)
print("| :--- | :---: | :---: | :---: | :---: |")

for r in records:
    print(
        f"| `{r['secuencia']}` | {r['cuadros']} | {r['cajas']} | {r['promedio']:.2f} | {r['vacios']} |"
    )

print(
    f"| **TOTAL** | **{tot_frames}** | **{tot_boxes}** | **{avg_global:.2f}** | **{tot_empty}** |\n"
)

if all_widths:
    print("### Caracterización de Tamaños de Cajas (Normalizados [0, 1])")
    print(f"- **Ancho promedio ($w$):** {fmean(all_widths):.4f} (± {pstdev(all_widths):.4f})")
    print(f"- **Alto promedio ($h$):** {fmean(all_heights):.4f} (± {pstdev(all_heights):.4f})")
    print(
        f"- **Área promedio ($w \\times h$):** {fmean(all_areas):.4f} (± {pstdev(all_areas):.4f})"
    )
