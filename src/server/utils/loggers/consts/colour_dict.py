COLOURS = {
    'RED': "\033[31m",          
    'YELLOW': "\033[33m",       
    'BLUE': "\033[34m",         
    'GREEN': "\033[32m",        
    'CYAN': "\033[36m",         
    'BLACK': "\033[30m",        
    'WHITE': "\033[37m",        
    'PURPLE': "\033[38;5;129m", 
    'GREY': "\033[38;5;240m",   
    'MAGENTA': "\033[35m",      
    'PINK': "\033[38;5;200m",   
    'SANIC': "\033[38;2;255;13;104m", 
    # PREFIX
    'R': "\033[31m",            
    'Y': "\033[33m",            
    'B': "\033[34m",            
    'G': "\033[32m",            
    'V': "\033[31m",            
    'C': "\033[36m",            
    'M': "\033[35m",            
    'P': "\033[38;5;129m", 
    'S': "\033[38;2;255;13;104m",  
    'LR': "\033[91m",           
    'LY': "\033[93m",           
    'LB': "\033[94m",           
    'LG': "\033[92m",           
    'LC': "\033[96m",           
    'LM': "\033[95m",           
    'LW': "\033[97m",           
    'LP': "\033[38;5;177m",     
    'RESET': "\033[0m"      
}

LOG_COLOURS = {
    60: COLOURS['S'],
    50: COLOURS['LR'],
    40: COLOURS['R'],
    30: COLOURS['Y'],
    20: COLOURS['G'],
    10: COLOURS['B'],            
    0:  COLOURS['C']            
}

LOG_LEVELS = {
    "NOTSET": 0,
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "WARN": 30, 
    "ERROR": 40,
    "EXCEPTION": 40, 
    "CRITICAL": 50,
    "TRACE": 60,
    0: "NOTSET",
    10: "DEBUG",
    20: "INFO",
    30: "WARNING",
    40: "ERROR",
    50: "CRITICAL",
    60: "TRACE"
}

COLOUR_LOG_PATTERN={
	'DEBUG':    'cyan',
	'INFO':     'green',
	'WARNING':  'yellow',
	'ERROR':    'red',
	'CRITICAL': 'red,bg_white'
} 

COLOUR_LOG_LIGHT={
	'DEBUG':    'light_purple',
	'INFO':     'light_green',
	'WARNING':  'light_yellow',
	'ERROR':    'light_red',
	'CRITICAL': 'red,bg_white'
}  



