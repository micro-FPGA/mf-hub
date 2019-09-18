set python=C:\python37\python.exe

@echo testing pinout generation for Intel MAX10, C10LP, 

python extract_pinout.py .\pinouts\10m08sa.txt > pinout.txt
python extract_pinout.py .\pinouts\10m50da.txt >> pinout.txt

python extract_pinout.py .\pinouts\10cl025.txt >> pinout.txt




