import sys; from pathlib import Path; import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; import matplotlib.image as mpimg
P = Path(sys.argv[1]); stems = sys.argv[2:]
fig, ax = plt.subplots(4, 3, figsize=(15, 16))
for a, s in zip(ax.flat, stems): a.imshow(mpimg.imread(P / f'{s}.png')); a.set_title(s, fontsize=9); a.axis('off')
for a in list(ax.flat)[len(stems):]: a.axis('off')
fig.tight_layout(); fig.savefig(P.parent.parent / 'tools' / 'contact_sheet.png', dpi=80)
