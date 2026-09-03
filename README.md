# Payload Carrier

ระบบควบคุมโดรนสำหรับเกม **Payload Carrier**

โปรแกรมหลักประกอบด้วยระบบตรวจจับ QR Code, ระบบควบคุมโดรนผ่าน Hula และ GUI สำหรับควบคุมและแสดงสถานะการทำงาน

---

# Requirements

Environment ที่ทดสอบกับโปรเจกต์:

```text
Python      3.12.0
pyhula      1.1.8
PySide6     6.11.2
```

Library หลักที่ใช้:

```text
numpy
psutil
lxml
fastcrc
pymavlink
opencv-python
mediapipe
keyboard
PySide6
pyhula
```

---

# การ Install Python

## 1. เปิด Installer Python

เปิดไฟล์:

```text
python-3.12.0-amd64.exe
```

## 2. เพิ่ม Python เข้า PATH

ที่หน้าแรกของ Installer ให้ติ๊ก:

```text
Add python.exe to PATH
```

## 3. ติดตั้ง Python

กด:

```text
Install Now
```

## 4. ติดตั้งเสร็จ

เมื่อ Installation เสร็จแล้ว ให้กด:

```text
Close
```

---

# การตรวจสอบ Python

เปิด Command Prompt แล้วตรวจสอบ:

```powershell
python --version
```

ควรแสดง:

```text
Python 3.12.0
```

สามารถตรวจสอบเพิ่มเติมได้:

```powershell
py -3.12 --version
```

ควรแสดง:

```text
Python 3.12.0
```

---

# การ Install Library ต่าง ๆ และ pyhula

## 1. เปิด Command Prompt ใน Folder ของโปรเจกต์

เข้าไปยัง Folder:

```text
payload carrier
```

จากนั้นเปิด Command Prompt / PowerShell ใน Folder นี้

ตัวอย่าง:

```text
C:\...\payload carrier>
```

---

## 2. สร้าง Virtual Environment

ใช้คำสั่ง:

```powershell
py -3.12 -m venv .venv
```

หลังจากนั้นจะได้ Folder:

```text
.venv
```

---

## 3. Activate Virtual Environment

ใช้คำสั่ง:

```powershell
.venv\Scripts\activate
```

เมื่อ Activate สำเร็จ จะเห็น:

```text
(.venv)
```

อยู่ด้านหน้า Command Prompt เช่น:

```text
(.venv) C:\...\payload carrier>
```

---

## 4. อัปเดต pip

ใช้คำสั่ง:

```powershell
python -m pip install --upgrade pip
```

---

# 5. Install Library ที่จำเป็น

ติดตั้ง Library ที่ต้องใช้ด้วยคำสั่ง:

```powershell
python -m pip install --only-binary=:all: numpy==2.4.3 psutil==7.2.2 lxml==6.0.2 fastcrc==0.3.5 pymavlink==2.4.49 opencv-python==4.13.0.92 mediapipe==0.10.14 keyboard
```

จากนั้นติดตั้ง PySide6:

```powershell
python -m pip install PySide6==6.11.2
```

---

# 6. Install pyhula

ไฟล์ pyhula ที่ใช้กับโปรเจกต์:

```text
pyhula-1.1.8-cp312-cp312-win_amd64.whl
```

ตรวจสอบก่อนว่าไฟล์ `.whl` อยู่ใน Folder ปัจจุบัน

จากนั้นใช้คำสั่ง:

```powershell
python -m pip install --no-deps pyhula-1.1.8-cp312-cp312-win_amd64.whl
```

### ทำไมใช้ `--no-deps`

เนื่องจาก Dependency ของ `pyhula` ถูกติดตั้งแยกไว้แล้วในขั้นตอนก่อนหน้า จึงไม่ให้ pip ดาวน์โหลด Dependency เวอร์ชันอื่นมาทับ Environment ที่ทดสอบไว้

---

# 7. ทดสอบการติดตั้ง pyhula

เปิด Python:

```powershell
python
```

จากนั้นพิมพ์:

```python
import pyhula

print("ติดตั้งสำเร็จ")
```

ถ้าติดตั้งถูกต้อง จะได้:

```text
ติดตั้งสำเร็จ
```

ออกมา

ออกจาก Python ด้วย:

```python
exit()
```

---

# 8. ตรวจสอบ Version ทั้งหมด

ตรวจสอบ Python:

```powershell
python --version
```

ควรได้:

```text
Python 3.12.0
```

ตรวจสอบ pyhula:

```powershell
python -m pip show pyhula
```

ควรได้:

```text
Name: pyhula
Version: 1.1.8
```

ตรวจสอบ PySide6:

```powershell
python -m pip show PySide6
```

ควรได้:

```text
Name: PySide6
Version: 6.11.2
```

สามารถตรวจสอบพร้อมกันได้:

```powershell
python -m pip list | findstr /I "pyhula PySide6 numpy opencv"
```

---

# Project Structure

ตัวอย่างโครงสร้างโปรเจกต์:

```text
payload carrier/
│
├── main.py
├── config.py
├── requirements.txt
├── pyhula-1.1.8-cp312-cp312-win_amd64.whl
│
├── core/
│   ├── bridge/
│   │   └── hula_bridge.py
│   │
│   ├──camera
│   │   ├── camera_controller.py
│   │   └── camera.py
│   │
│   ├── mission/
│   │   └── mission_controller.py
│   │
│   ├── tracking/
│   │   └── qr_tracker.py
│   │
│   └── ui/
│       └──main_window.py
│
└── .venv/
```

---

# การ Run โปรแกรม

ก่อน Run โปรแกรมต้อง Activate `.venv` ก่อน:

```powershell
.venv\Scripts\activate
```

จากนั้น:

```powershell
python main.py
```

---

# QR System

ระบบสามารถตรวจจับ QR หลายตัวพร้อมกันในภาพเดียว

เมื่อกล้องเห็น QR หลายตัว ระบบจะ:

```text
Detect QR ทั้งหมด
        ↓
ตรวจสอบ QR ที่ระบบอนุญาต
        ↓
เลือก QR ที่เหมาะสม
        ↓
ส่ง QR ที่เลือกให้ MissionController
```

QR ใช้ชื่อในรูปแบบ:

```text
qr1
qr2
qr3
...
```

ตัวอย่างการกำหนดคำสั่ง:

```python
QR_ACTIONS = {

    "qr1": "take_off",
    "qr2": "left",
    "qr3": "forward",
    "qr4": "backward",
    "qr5": "left",
    "qr6": "right",

}
```

สามารถเพิ่ม QR ได้จาก `config.py` โดยเพิ่มชื่อ QR และคำสั่งที่ต้องการ เช่น:

```python
QR_ACTIONS = {

    "qr1": "take_off",
    "qr2": "left",
    "qr3": "forward",
    "qr4": "backward",
    "qr5": "left",
    "qr6": "right",

    "qr7": "forward",
    "qr8": "landing",
    "qr9": "right",

}
```

สามารถเพิ่มต่อได้เรื่อย ๆ เช่น `qr10`, `qr11`, `qr12` ตามจำนวน QR ที่ต้องการใช้งาน โดยระบบไม่ได้กำหนดว่าต้องมีเพียง 6 ตัว

คำสั่งที่สามารถกำหนดให้ QR ได้ในปัจจุบัน ได้แก่:

```text
take_off
landing
forward
backward
left
right
```

ตัวอย่าง:

```python
QR_ACTIONS = {

    "qr7": "take_off",
    "qr8": "landing",
    "qr9": "forward",
    "qr10": "backward",
    "qr11": "left",
    "qr12": "right",

}
```

ชื่อ QR ที่อยู่บน QR Code ต้องตรงกับชื่อที่กำหนดใน `QR_ACTIONS` เช่น QR Code ที่บรรจุข้อความ:

```text
qr7
```

จะถูกจับคู่กับ:

```python
"qr7": "forward"
```

และระบบจะสั่ง:

```text
FORWARD
```

ตามคำสั่งที่กำหนดไว้

### การเพิ่ม QR ใหม่

โดยทั่วไปไม่จำเป็นต้องแก้ `QRTracker` หรือ `MissionController` เพียงเพิ่มรายการใน `QR_ACTIONS`:

```python
QR_ACTIONS = {

    "qr1": "take_off",
    "qr2": "left",
    "qr3": "forward",
    "qr4": "backward",
    "qr5": "left",
    "qr6": "right",

    # เพิ่ม QR ใหม่ตรงนี้
    "qr7": "forward",
    "qr8": "landing",
    "qr9": "right",
    "qr10": "left",

}
```

ดังนั้นการกำหนด QR และคำสั่งจึงสามารถจัดการจาก `config.py` ได้เป็นหลัก

---

# QR Focus Point

QR ทุกตัวสามารถใช้ Focus Point เดียวกันได้

กำหนดใน `config.py`:

```python
QR_FOCUS_POINT = (640, 360)
```

ทุก QR จะอ้างอิง Focus Point เดียวกัน ไม่จำเป็นต้องกำหนด:

```text
qr1 → จุดหนึ่ง
qr2 → อีกจุดหนึ่ง
qr3 → อีกจุดหนึ่ง
```

ระบบจะใช้:

```text
QR ทุกตัว
   ↓
QR_FOCUS_POINT เดียวกัน
```

กำหนดระยะที่ยอมรับได้ด้วย:

```python
FOCUS_TOLERANCE = 150
```

---

# Auto Mode

Auto Mode ใช้ QR เป็นตัวกำหนดคำสั่ง

ลำดับการทำงาน:

```text
เจอ QR
   ↓
QR Lock
   ↓
Command Countdown
   ↓
Correction ทำงาน
   ↓
เข้าสู่ช่วงท้าย Countdown
   ↓
หยุด Correction
   ↓
Countdown = 0
   ↓
ส่ง Command ที่ Lock ไว้
   ↓
Hula ทำ Block ให้จบ
   ↓
Command Finished
   ↓
QR Cooldown
   ↓
พร้อมรับ QR ใหม่
```

---

# Command Countdown

ค่า Countdown อยู่ใน `config.py`

```python
COMMAND_DELAY = 7.0
```

เวลาที่ระบบรอก่อนส่งคำสั่ง QR

กำหนดเวลาเริ่มเสียงเตือน:

```python
COMMAND_WARNING_TIME = 5.0
```

กำหนดช่วงห่างของเสียงเตือน:

```python
COMMAND_WARNING_INTERVAL = 0.5
```

กำหนดเวลาที่ต้องหยุด Correction ก่อน Command:

```python
COMMAND_CORRECTION_STOP_TIME = 3.0
```

ดังนั้นตัวอย่างปัจจุบัน:

```text
7 → 5 วินาที
    Correction ทำงาน

5 → 3 วินาที
    มีเสียงเตือน
    Correction ยังทำงาน

3 → 0 วินาที
    Correction หยุด
    QR ใหม่ไม่สามารถเปลี่ยน Command ที่ Lock ไว้

0 วินาที
    ส่ง Command ที่ Lock ไว้
```

---

# QR Cooldown

หลังจาก Countdown จบและส่ง Command แล้ว ระบบจะไม่รับ QR Command ใหม่ทันที เพื่อป้องกันการอ่าน QR เดิมซ้ำ

กำหนดใน `config.py`:

```python
QR_POST_COUNTDOWN_COOLDOWN = 2.0
```

สามารถเพิ่มหรือลดค่าได้ตามต้องการ

---

# Hula Command Priority

เมื่อ QR ถูก Lock และเริ่ม Countdown แล้ว:

```text
QR Command = Locked Command
```

Command อื่นจะไม่สามารถเข้ามาแทน Command ที่กำลังนับถอยหลังได้

เมื่อ Countdown จบ Command ที่ Lock ไว้จะถูกส่งไปยัง Hula

เนื่องจาก `pyhula` ทำงานในลักษณะ Block Command:

```text
Command Block
     ↓
Execute
     ↓
รอจน Block จบ
     ↓
ปลด Lock
     ↓
รับ Command ใหม่
```

เพื่อป้องกันการส่งคำสั่งหลาย Block ซ้อนกัน

---

# Correction System

Auto Mode มีระบบ Correction สำหรับปรับตำแหน่งโดรนให้เข้าใกล้ Focus Point

ค่าต่าง ๆ:

```python
CORRECTION_DISTANCE = 10
CORRECTION_SPEED = 20
CORRECTION_MAX_COUNT = 5
CORRECTION_INTERVAL = 2
CORRECTION_TIMEOUT = 10
```

ระบบจะหยุด Correction เมื่อ Countdown เหลือ:

```python
COMMAND_CORRECTION_STOP_TIME = 3.0
```

---

# Manual Mode

Manual Mode ใช้ควบคุมโดรนโดยผู้ใช้งาน

```text
M        AUTO / MANUAL

T        TAKE OFF
L        LAND

↑        FORWARD
↓        BACKWARD
←        LEFT
→        RIGHT

A        ROTATE LEFT
D        ROTATE RIGHT

W        UP
S        DOWN

[        CAMERA DOWN
]        CAMERA UP

R        RESET
Q        QUIT
```

---

# Reset Flight State

Reset ใช้สำหรับแก้ State ของระบบให้ตรงกับสถานะจริงของโดรน

ก่อน Reset ผู้ใช้ต้องเลือกว่าตอนนี้โดรนอยู่:

```text
FLYING
```

หรือ:

```text
LANDED
```

จากนั้นระบบจะ Reset State ภายในตามสถานะที่เลือก

**ต้องเลือกให้ตรงกับสถานะจริงของโดรนก่อนใช้งาน**

---

# Camera

การควบคุมกล้องสามารถกำหนดค่าใน `config.py`

```python
CAMERA_AUTO_ANGLE = -90
CAMERA_MANUAL_ANGLE = 0
CAMERA_MODE_CHANGE_DELAY = 3.0
CAMERA_MANUAL_STEP = 5
```

---

# Hula Connection

ระบบใช้ `HulaBridge` เป็นตัวกลางระหว่างโปรแกรมและ `pyhula`

การทำงาน:

```text
MissionController
       ↓
   HulaBridge
       ↓
     pyhula
       ↓
      Hula
       ↓
     Drone
```

Hula Command จะถูกส่งแบบทีละคำสั่ง เพื่อไม่ให้เกิด Command ซ้อนกัน

---

# Troubleshooting

## Python ไม่ตรง Version

ตรวจสอบ:

```powershell
python --version
```

ต้องเป็น:

```text
Python 3.12.0
```

ถ้าใช้หลาย Python ให้ตรวจสอบ:

```powershell
py -3.12 --version
```

---

## ตรวจสอบ pyhula

```powershell
python -m pip show pyhula
```

ต้องเป็น:

```text
Version: 1.1.8
```

---

## ตรวจสอบ PySide6

```powershell
python -m pip show PySide6
```

ต้องเป็น:

```text
Version: 6.11.2
```

---

## pyhula import ไม่ได้

ตรวจสอบว่า `.venv` ถูก Activate แล้ว:

```powershell
.venv\Scripts\activate
```

จากนั้น:

```powershell
python
```

และ:

```python
import pyhula

print("ติดตั้งสำเร็จ")
```

---

## ทดสอบโปรแกรม

สามารถเข้าไปใน Folder ของโปรเจกต์ แล้วรันไฟล์ `.py` ที่ต้องการทดสอบได้ เช่น:

```powershell
python main.py
```

---

# Tested Environment

```text
OS          Windows
Python      3.12.0
pyhula      1.1.8
PySide6     6.11.2

numpy       2.4.3
psutil      7.2.2
lxml        6.0.2
fastcrc     0.3.5
pymavlink   2.4.49
opencv      4.13.0.92
mediapipe   0.10.14
keyboard    Installed
```

---

# Installation Summary

สำหรับติดตั้งเครื่องใหม่ ลำดับโดยรวมคือ:

```text
ติดตั้ง Python 3.12.0
        ↓
สร้าง .venv
        ↓
Activate .venv
        ↓
Update pip
        ↓
Install Dependencies
        ↓
Install PySide6 6.11.2
        ↓
Install pyhula 1.1.8
        ↓
ทดสอบ import pyhula
        ↓
Run main.py
```

---

# Run

ทุกครั้งก่อนเปิดโปรแกรม:

```powershell
.venv\Scripts\activate
```

จากนั้น:

```powershell
python main.py
```

โปรเจกต์นี้พัฒนาสำหรับเกม **Payload Carrier**
