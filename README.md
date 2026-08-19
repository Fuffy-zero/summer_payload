### การ Install Python


1.ทำการคลิปเปิดตัว Installer "python-3.12.0-amd64"

2.คลิก "Add python.exe to PATH"

3.คลิก "Install Now"

4.เมื่อ Install เสร็จให้ทำการคลิก close

### การ Install Library ต่างๆและ Pyhula

1.เปิด Command Prompt โดยการกดคลิปขวาที่ว่างใน Folder แล้วใส่คำสั่งตามนี้

2. สร้าง venv
---------------------------------
py -3.12 -m venv .venv


3. ทำการ Activate venv
---------------------------------
.venv\Scripts\activate

4.อัปเดต pip
---------------------------------
python -m pip install --upgrade pip


5.Install Library ที่จำเป็น
---------------------------------
python -m pip install --only-binary=:all: numpy==2.4.3 psutil==7.2.2 lxml==6.0.2 fastcrc==0.3.5 pymavlink==2.4.49 opencv-python==4.13.0.92 mediapipe==0.10.14 keyboard

python -m pip install --no-deps pyhula-1.1.8-cp312-cp312-win_amd64.whl


6.ทดสอบการติดตั้ง pyhula
---------------------------------
python

import pyhula
print("ติดตั้งสำเร็จ")

ถ้าติดตั้งแล้วก็จะมีข้อความขึ้นว่า "ติดตั้งสำเร็จ"


7.ทำการทดสอบโปรแกรมต่างๆโดยการเปิดเข้าไปใน Folder แล้วรัน .py ไฟล์
