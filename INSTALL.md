# Payload Carrier — Installation Guide

คู่มือสำหรับติดตั้ง Environment และรันโปรแกรม **Payload Carrier**

## 1. Requirements

เวอร์ชันที่ใช้ทดสอบ:

```text
Python      3.12.0
pyhula      1.1.8
PySide6     6.11.2
```

ระบบปฏิบัติการ:

```text
Windows
```

---

# 2. Install Python

เปิดไฟล์:

```text
python-3.12.0-amd64.exe
```

ที่หน้าแรกของ Installer:

1. ติ๊ก `Add python.exe to PATH`
2. กด `Install Now`
3. รอจนติดตั้งเสร็จ
4. กด `Close`

ตรวจสอบ:

```powershell
python --version
```

ควรได้:

```text
Python 3.12.0
```

---

# 3. Open Project Folder

เปิด Command Prompt หรือ PowerShell ใน Folder:

```text
payload carrier
```

ตัวอย่าง:

```text
C:\...\payload carrier>
```

---

# 4. Create Virtual Environment

สร้าง `.venv`:

```powershell
py -3.12 -m venv .venv
```

---

# 5. Activate Virtual Environment

```powershell
.venv\Scripts\activate
```

เมื่อสำเร็จจะเห็น:

```text
(.venv)
```

อยู่ด้านหน้า Command Prompt

ตัวอย่าง:

```text
(.venv) C:\...\payload carrier>
```

---

# 6. Update pip

```powershell
python -m pip install --upgrade pip
```

---

# 7. Install Required Libraries

ติดตั้ง Library ที่จำเป็น:

```powershell
python -m pip install --only-binary=:all: numpy==2.4.3 psutil==7.2.2 lxml==6.0.2 fastcrc==0.3.5 pymavlink==2.4.49 opencv-python==4.13.0.92 mediapipe==0.10.14 keyboard
```

ติดตั้ง PySide6:

```powershell
python -m pip install PySide6==6.11.2
```

---

# 8. Install pyhula

ตรวจสอบว่าไฟล์นี้อยู่ใน Folder ของโปรเจกต์:

```text
pyhula-1.1.8-cp312-cp312-win_amd64.whl
```

ติดตั้งด้วย:

```powershell
python -m pip install --no-deps pyhula-1.1.8-cp312-cp312-win_amd64.whl
```

---

# 9. Verify Installation

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

ควรเป็น:

```text
Version: 1.1.8
```

ตรวจสอบ PySide6:

```powershell
python -m pip show PySide6
```

ควรเป็น:

```text
Version: 6.11.2
```

---

# 10. Test pyhula

เปิด Python:

```powershell
python
```

จากนั้น:

```python
import pyhula

print("ติดตั้งสำเร็จ")
```

ถ้าแสดง:

```text
ติดตั้งสำเร็จ
```

แสดงว่า `pyhula` สามารถ import ได้

ออกจาก Python:

```python
exit()
```

---

# 11. Run Payload Carrier

ตรวจสอบว่า `.venv` ยังเปิดอยู่:

```text
(.venv)
```

จากนั้นรัน:

```powershell
python main.py
```

---

# 12. ครั้งถัดไปที่ต้องการเปิดโปรแกรม

ไม่ต้องสร้าง `.venv` ใหม่

เข้า Folder ของโปรเจกต์:

```text
payload carrier
```

Activate:

```powershell
.venv\Scripts\activate
```

จากนั้น:

```powershell
python main.py
```

---

# 13. Quick Install

สำหรับเครื่องที่ติดตั้ง Python 3.12.0 แล้ว สามารถทำตามลำดับนี้:

```powershell
py -3.12 -m venv .venv

.venv\Scripts\activate

python -m pip install --upgrade pip

python -m pip install --only-binary=:all: numpy==2.4.3 psutil==7.2.2 lxml==6.0.2 fastcrc==0.3.5 pymavlink==2.4.49 opencv-python==4.13.0.92 mediapipe==0.10.14 keyboard

python -m pip install PySide6==6.11.2

python -m pip install --no-deps pyhula-1.1.8-cp312-cp312-win_amd64.whl

python main.py
```

---

# 14. Troubleshooting

## Python Version ไม่ถูกต้อง

```powershell
py -3.12 --version
```

ต้องเป็น:

```text
Python 3.12.0
```

## pyhula Import ไม่ได้

ตรวจสอบว่า `.venv` ถูก Activate:

```powershell
.venv\Scripts\activate
```

จากนั้น:

```powershell
python -m pip show pyhula
```

ต้องเป็น:

```text
Version: 1.1.8
```

## PySide6 Version ไม่ถูกต้อง

```powershell
python -m pip show PySide6
```

ต้องเป็น:

```text
Version: 6.11.2
```

---

# 15. Important

ต้องใช้ไฟล์ `pyhula` ให้ตรงกับ Python:

```text
Python 3.12
        +
pyhula-1.1.8-cp312-cp312-win_amd64.whl
```

ไม่ควรนำ Wheel ของ Python เวอร์ชันอื่นมาใช้

---

# 16. Start Command

คำสั่งสำหรับเปิดโปรแกรม:

```powershell
.venv\Scripts\activate
python main.py
```

**Payload Carrier**
