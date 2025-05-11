import os
from src.server.utils.miscellaneous import os_is_windows

DEBUG_MODE = os.getenv('DEBUG_MODE', str(os_is_windows())).lower() == 'true'

def main():
    import uvicorn    
    uvicorn.run(
        "app:app", 
        host= os.getenv('HOST', '127.0.0.1'),
        port=int(os.getenv('PORT', 8080)),
        app_dir='src/',
        reload=DEBUG_MODE, 
        workers=1, 
        log_level="info" if not DEBUG_MODE else "debug", 
        access_log=DEBUG_MODE,
        env_file='.env',
        timeout_keep_alive=60,
        http="httptools"
    )
    
if __name__ == "__main__":
    main()
