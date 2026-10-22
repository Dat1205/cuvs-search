# 📦 Hướng dẫn Cài đặt Chi tiết

Hướng dẫn cài đặt từ đầu cho máy Windows mới hoàn toàn.

---

## Phần 1: Cài đặt WSL2 (Windows Subsystem for Linux)

### 1.1. Kiểm tra yêu cầu hệ thống

- Windows 10 version 2004+ (Build 19041+) hoặc Windows 11
- Chế độ Virtualization được bật trong BIOS
- Ít nhất 8GB RAM (khuyên dùng 16GB+)

### 1.2. Kiểm tra Virtualization

1. Mở **Task Manager** (`Ctrl+Shift+Esc`)
2. Vào tab **Performance**
3. Chọn **CPU**
4. Kiểm tra **Virtualization: Enabled**

Nếu **Disabled**, cần vào BIOS và bật:
- Intel: **Intel VT-x** hoặc **Intel Virtualization Technology**
- AMD: **AMD-V** hoặc **SVM Mode**

### 1.3. Cài đặt WSL2

**Cách 1: Tự động (Khuyên dùng)**

Mở **PowerShell** với quyền **Administrator** và chạy:

```powershell
wsl --install
```

Lệnh này sẽ:
- Bật WSL feature
- Bật Virtual Machine Platform
- Tải và cài Ubuntu (distro mặc định)
- Đặt WSL 2 là mặc định

**Khởi động lại máy tính** sau khi hoàn tất.

**Cách 2: Thủ công**

Nếu lệnh trên không hoạt động:

```powershell
# 1. Bật WSL
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 2. Bật Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 3. Khởi động lại máy

# 4. Tải WSL2 Linux kernel update
# Truy cập: https://aka.ms/wsl2kernel và cài đặt

# 5. Đặt WSL 2 làm mặc định
wsl --set-default-version 2

# 6. Cài Ubuntu từ Microsoft Store
# Tìm "Ubuntu" trong Microsoft Store và cài đặt
```

### 1.4. Thiết lập Ubuntu

Sau khi khởi động lại, Ubuntu sẽ tự mở:

```
Installing, this may take a few minutes...
Please create a default UNIX user account.
Enter new UNIX username: 
```

Nhập:
- **Username:** tên người dùng (chữ thường, không dấu)
- **Password:** mật khẩu (sẽ không hiển thị khi gõ)

**Ví dụ:**
```
Enter new UNIX username: john
New password: ********
Retype new password: ********
```

### 1.5. Cập nhật Ubuntu

```bash
sudo apt update && sudo apt upgrade -y
```

---

## Phần 2: Cài đặt NVIDIA CUDA Driver (cho GPU)

### 2.1. Kiểm tra GPU

Mở **Device Manager** → **Display adapters** → Xác nhận có NVIDIA GPU.

### 2.2. Cài đặt NVIDIA Driver trên Windows

1. Truy cập: https://www.nvidia.com/Download/index.aspx
2. Chọn GPU model của bạn
3. Tải và cài driver mới nhất
4. **Khởi động lại máy**

### 2.3. Kiểm tra CUDA trong WSL2

```bash
# Mở Ubuntu (WSL2)
wsl

# Kiểm tra GPU
nvidia-smi
```

**Output mong đợi:**
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.xx.xx    Driver Version: 535.xx.xx    CUDA Version: 12.2  |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  NVIDIA GeForce ...  Off  | 00000000:01:00.0 Off |                  N/A |
|  N/A   45C    P8    N/A /  N/A |      0MiB /  8192MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
```

> **Lưu ý:** Không cần cài CUDA toolkit riêng trong WSL2. Driver trên Windows đã cung cấp CUDA.

---

## Phần 3: Cài đặt Visual Studio Code với WSL

### 3.1. Cài đặt VSCode

1. Tải từ: https://code.visualstudio.com/
2. Cài đặt (mặc định)
3. Mở VSCode

### 3.2. Cài extension WSL

1. Nhấn `Ctrl+Shift+X` (Extensions)
2. Tìm **"WSL"** (của Microsoft)
3. Click **Install**

### 3.3. Kết nối VSCode với WSL

1. Nhấn `F1` hoặc `Ctrl+Shift+P`
2. Gõ: `WSL: Connect to WSL`
3. VSCode sẽ mở cửa sổ mới kết nối với Linux

### 3.4. Mở terminal trong VSCode

Nhấn `` Ctrl+` `` (backtick) để mở terminal Linux.

### 3.5. Cài Python extension

Trong VSCode đã kết nối WSL:
1. Nhấn `Ctrl+Shift+X`
2. Tìm **"Python"** (của Microsoft)
3. Click **Install in WSL**

---

## Phần 4: Cài đặt Miniconda

### 4.1. Tải Miniconda

```bash
# Vào thư mục home
cd ~

# Tải Miniconda installer
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

### 4.2. Cài đặt

```bash
# Chạy installer (chế độ tự động)
bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda3

# Khởi tạo conda cho bash
~/miniconda3/bin/conda init bash

# Tải lại cấu hình bash
source ~/.bashrc
```

### 4.3. Kiểm tra cài đặt

```bash
conda --version
```

**Output:** `conda 24.x.x` hoặc tương tự

### 4.4. Cấu hình conda (tùy chọn)

```bash
# Tắt auto-activation của base environment
conda config --set auto_activate_base false

# Thêm channels
conda config --add channels conda-forge
conda config --add channels rapidsai
conda config --add channels nvidia
```

---

## Phần 5: Clone hoặc tạo dự án

### 5.1. Truy cập ổ Windows từ WSL

Ổ đĩa Windows được mount tại `/mnt/`:
- `C:\` → `/mnt/c/`
- `D:\` → `/mnt/d/`

```bash
# Ví dụ: Vào thư mục D:\New
cd /mnt/d/New
```

### 5.2. Clone dự án (nếu có Git repo)

```bash
git clone <repository-url>
cd hybrid_search_project
```

### 5.3. Hoặc tạo dự án mới

```bash
mkdir hybrid_search_project
cd hybrid_search_project

# Tạo cấu trúc
mkdir -p src artifacts
```

---

## Phần 6: Tạo môi trường conda cho dự án

### 6.1. Cách tự động (khuyên dùng)

```bash
# Di chuyển đến thư mục dự án
cd /mnt/d/New/hybrid_search_project

# Chạy script setup
bash setup_env.sh
```

Script `setup_env.sh`:
```bash
#!/bin/bash
set -e

echo "Creating conda environment: hybrid_search"
conda create -n hybrid_search -c rapidsai -c conda-forge -c nvidia \
    cuvs=24.10 cupy cuda-version=12.0 python=3.10 -y

echo "Activating environment..."
source ~/miniconda3/bin/activate hybrid_search

echo "Installing Python packages..."
pip install sentence-transformers rank-bm25 datasets

echo "✓ Setup complete!"
echo "To activate: conda activate hybrid_search"
```

### 6.2. Cách thủ công

```bash
# Tạo environment
conda create -n hybrid_search -c rapidsai -c conda-forge -c nvidia \
    cuvs=24.10 cupy cuda-version=12.0 python=3.10 -y

# Kích hoạt
conda activate hybrid_search

# Cài packages
pip install sentence-transformers rank-bm25 datasets
```

### 6.3. Verify cài đặt

```bash
# Kiểm tra Python
python --version  # Python 3.10.x

# Kiểm tra CuPy
python -c "import cupy as cp; print('CuPy OK:', cp.cuda.is_available())"

# Kiểm tra cuVS
python -c "from cuvs.neighbors import cagra; print('cuVS OK')"

# Kiểm tra các thư viện khác
python -c "import sentence_transformers, rank_bm25, datasets; print('All OK')"
```

**Output mong đợi:**
```
Python 3.10.14
CuPy OK: True
cuVS OK
All OK
```

---

## Phần 7: Cấu hình VSCode Python Interpreter

### 7.1. Chọn interpreter

1. Nhấn `F1` → gõ: `Python: Select Interpreter`
2. Chọn môi trường `hybrid_search`:
   ```
   Python 3.10.14 ('hybrid_search': conda)
   ~/miniconda3/envs/hybrid_search/bin/python
   ```

### 7.2. Verify trong VSCode

Mở terminal mới trong VSCode (`` Ctrl+` ``):
```bash
which python
# /home/<username>/miniconda3/envs/hybrid_search/bin/python

conda info --envs
# hybrid_search       *  /home/<username>/miniconda3/envs/hybrid_search
```

---

## Phần 8: Tạo files dự án

### 8.1. Tạo requirements.txt

```bash
cat > requirements.txt << 'EOF'
sentence-transformers
rank-bm25
datasets
EOF
```

### 8.2. Tạo .gitignore

```bash
cat > .gitignore << 'EOF'
# Artifacts
artifacts/

# Python
__pycache__/
*.py[cod]
*.so
.Python
*.egg-info/

# Conda
.conda/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
EOF
```

---

## Phần 9: Kiểm tra tổng thể

### 9.1. System check

```bash
# OS
uname -a

# GPU
nvidia-smi

# Python
python --version

# Conda environment
conda info --envs

# CUDA
python -c "import cupy; print('CUDA:', cupy.cuda.runtime.runtimeGetVersion())"
```

### 9.2. Import test

```python
python << 'EOF'
import sys
print(f"Python: {sys.version}")

import cupy as cp
print(f"CuPy: {cp.__version__}, CUDA: {cp.cuda.is_available()}")

from cuvs.neighbors import cagra
print(f"cuVS: OK")

import sentence_transformers
print(f"sentence-transformers: {sentence_transformers.__version__}")

import rank_bm25
print(f"rank-bm25: OK")

import datasets
print(f"datasets: {datasets.__version__}")

print("\n✅ All dependencies OK!")
EOF
```

---

## Troubleshooting cài đặt

### ❌ WSL2 không khởi động

**Nguyên nhân:** Virtualization chưa bật

**Giải pháp:**
1. Vào BIOS (thường nhấn F2/Del khi khởi động)
2. Tìm **Virtualization Technology** hoặc **Intel VT-x** / **AMD-V**
3. Đặt thành **Enabled**
4. Lưu và khởi động lại

### ❌ `nvidia-smi` không hoạt động trong WSL2

**Nguyên nhân:** Driver Windows chưa đủ mới

**Giải pháp:**
- Cập nhật NVIDIA driver lên phiên bản mới nhất (>= 470.xx)
- Tải từ: https://www.nvidia.com/Download/index.aspx

### ❌ Conda rất chậm khi resolve dependencies

**Giải pháp:** Dùng `mamba` (faster conda):
```bash
conda install mamba -n base -c conda-forge
mamba create -n hybrid_search -c rapidsai -c conda-forge -c nvidia \
    cuvs=24.10 cupy cuda-version=12.0 python=3.10 -y
```

### ❌ `pip install` bị lỗi SSL

**Giải pháp:**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package>
```

### ❌ Hết dung lượng ổ C (do WSL2)

**Giải pháp:** Di chuyển WSL distro sang ổ khác:
```powershell
# Export
wsl --export Ubuntu D:\wsl-backup\ubuntu.tar

# Unregister
wsl --unregister Ubuntu

# Import vào ổ D
wsl --import Ubuntu D:\WSL\Ubuntu D:\wsl-backup\ubuntu.tar
```

---

## Các bước tiếp theo

Sau khi cài đặt xong:

1. ✅ Đọc [QUICKSTART.md](QUICKSTART.md) để chạy dự án
2. ✅ Đọc [CODE_GUIDE.md](CODE_GUIDE.md) để hiểu code
3. ✅ Tham khảo [TROUBLESHOOTING.md](TROUBLESHOOTING.md) khi gặp lỗi

---

**Thời gian cài đặt:** 30-60 phút (tùy tốc độ internet)  
**Dung lượng yêu cầu:** ~15GB (WSL2 + Conda + Dependencies)
