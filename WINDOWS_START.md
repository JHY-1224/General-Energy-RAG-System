# Windows 启动说明

当前项目已经整理为 Windows 友好的本地运行结构：

- 后端：Python FastAPI，默认端口 `8000`
- 前端：Vue 3 + Vite，默认端口 `8080`
- 前端通过 Vite proxy 访问后端 `/api/*`

## 1. 进入项目根目录

```powershell
cd "C:\Users\Administrator\Desktop\江翰宇\Vernova-RAG"
```

## 2. 安装后端依赖

```powershell
python -m pip install -r backend/requirements.txt
```

## 3. 启动后端

```powershell
python backend/main.py
```

后端地址：

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```

## 4. 安装前端依赖

另开一个 PowerShell 窗口：

```powershell
cd "C:\Users\Administrator\Desktop\江翰宇\Vernova-RAG"
npm install
```

## 5. 启动前端

```powershell
npm run dev
```

前端地址：

```text
http://127.0.0.1:8080
```

## 常见问题

### 打开前端看到后端不可用

说明 Vite 已启动，但 FastAPI 没有启动。回到后端终端执行：

```powershell
python backend/main.py
```

### `npm run dev` 提示依赖缺失

在项目根目录重新执行：

```powershell
npm install
```

### 端口被占用

关闭占用 `8000` 或 `8080` 的终端窗口，或者分别修改 `backend/main.py` 和 `vite.config.ts` 中的端口。

## 构建检查

```powershell
npm run build
python -m py_compile backend/main.py
```
