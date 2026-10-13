import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Ajusta la ruta a tu carpeta principal donde están las carpetas seq_XXXX
DATA_DIR = Path(".")

sequences = sorted([d for d in DATA_DIR.glob("seq_*") if d.is_dir()])

records = []
box_records = []

print(f"Encontradas {len(sequences)} secuencias.\n")

for seq_path in sequences:
    seq_name = seq_path.name
    img_dir = seq_path / "images"
    lbl_dir = seq_path / "labels"

    # Obtener todas las imagenes y etiquetas
    images = sorted(
        list(img_dir.glob("*.jpg"))
        + list(img_dir.glob("*.jpeg"))
        + list(img_dir.glob("*.png"))
    )
    labels = sorted(list(lbl_dir.glob("*.txt")))

    total_imgs = len(images)
    total_boxes = 0
    empty_frames = 0

    for img_file in images:
        lbl_file = lbl_dir / f"{img_file.stem}.txt"
        if lbl_file.exists():
            with open(lbl_file, "r") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]

            num_boxes = len(lines)
            total_boxes += num_boxes
            if num_boxes == 0:
                empty_frames += 1

            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    cls, x, y, w, h = map(float, parts[:5])
                    box_records.append(
                        {
                            "sequence": seq_name,
                            "class": int(cls),
                            "width": w,
                            "height": h,
                            "area": w * h,
                        }
                    )
        else:
            empty_frames += 1

    records.append(
        {
            "Secuencia": seq_name,
            "Total Cuadros": total_imgs,
            "Total Cajas": total_boxes,
            "Cajas/Cuadro": round(total_boxes / total_imgs, 2) if total_imgs > 0 else 0,
            "Cuadros sin Peces": empty_frames,
        }
    )

df_summary = pd.DataFrame(records)
df_boxes = pd.DataFrame(box_records)

print("=== RESUMEN POR SECUENCIA ===")
print(df_summary.to_string(index=False))

# Generar gráficos para la presentación
plt.figure(figsize=(12, 5))

# Histograma de áreas relativas
plt.subplot(1, 2, 1)
plt.hist(df_boxes["area"], bins=30, color="teal", edgecolor="black")
plt.title("Distribución del Área Normalizada de las Cajas")
plt.xlabel("Área (w * h normalizado)")
plt.ylabel("Frecuencia")

# Scatter de Ancho vs Alto
plt.subplot(1, 2, 2)
plt.scatter(df_boxes["width"], df_boxes["height"], alpha=0.3, color="navy")
plt.title("Relación de Aspecto de Salmones (Width vs Height)")
plt.xlabel("Ancho normalizado")
plt.ylabel("Alto normalizado")

plt.tight_layout()
plt.savefig("analisis_cajas_salmones.png", dpi=300)
print("\nGráfico guardado como 'analisis_cajas_salmones.png'")
