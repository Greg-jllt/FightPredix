import logging
import json

def configure_logger(name: str) -> logging.Logger:
    
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.INFO) 

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler(f"logs\\{name}.log")
    file_handler.setLevel(logging.INFO)  
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logging.captureWarnings(True)
    return logger


def lire_combattant_manqué(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception:
        return {}
    
def ecrire_combattant_manqué(file_path, cbts):
    with open(file_path, "w") as file:
        if cbts is None:
            return
        cbts_cle = {str(key): value for key, value in cbts.items()}
        json.dump(cbts_cle, file)
