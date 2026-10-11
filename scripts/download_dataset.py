from pathlib import Path
import urllib.request, lzma, shutil
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'data/raw/5G_netops_data_100K.csv'; out.parent.mkdir(parents=True,exist_ok=True)
xz=ROOT/'data/raw/5G_netops_data_100K.csv.xz'
url='https://huggingface.co/datasets/fenar/5g_netops/resolve/main/5G_netops_data_100K.csv.xz'
print('Downloading official 5G NetOps dataset from Hugging Face...')
urllib.request.urlretrieve(url,xz)
with lzma.open(xz,'rb') as src, open(out,'wb') as dst: shutil.copyfileobj(src,dst)
xz.unlink(missing_ok=True)
print(f'Created {out}')
