git add requirements.txt
git commit -m "Add requirements.txt for Streamlit deployment"
git push origin main
pip install openpyxl
mkdir -p fonts
cp /path/ke/DejaVuSans.ttf fonts/
git add fonts/DejaVuSans.ttf
git commit -m "Menambahkan font DejaVuSans untuk PDF Unicode"
git push origin main
