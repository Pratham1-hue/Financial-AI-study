@echo off
cd /d "D:\Machine Learning Projects\Project Devi"
".venv\Scripts\python.exe" -m streamlit run "streamlit_app.py" --server.port 8501 --server.headless true