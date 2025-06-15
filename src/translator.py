import time
from deep_translator import GoogleTranslator

def chunk_text(text, max_len=4000):
    """
    Splits text into chunks of max_len characters to avoid API limits.
    """
    return [text[i:i+max_len] for i in range(0, len(text), max_len)]

def translate_text(text, translator):
    """
    Translates given text using the provided translator instance.
    Retries once after a short delay if translation fails.
    Returns a placeholder on failure.
    """
    if not text.strip():
        return ""
    try:
        return translator.translate(text)
    except Exception:
        time.sleep(5)  # Wait before retrying
        try:
            return translator.translate(text)
        except Exception:
            return "[TRANSLATION ERROR]"

def is_number(text):
    """
    Checks if text represents a number (int or float).
    """
    try:
        float(text.replace(',', ''))  # handle numbers with commas
        return True
    except ValueError:
        return False

def translate_dataframe(df, translator):
    """
    Translates DataFrame headers and cells (except numbers and empty strings).
    Returns a new DataFrame with translated content.
    """
    translated_df = df.copy()
    # Translate column headers
    translated_df.columns = [
        translate_text(col.strip(), translator) if col.strip() else col for col in df.columns
    ]
    # Translate each cell, skipping numbers or empty cells
    for col in translated_df.columns:
        translated_df[col] = [
            cell if not cell.strip() or is_number(cell.strip()) else translate_text(cell.strip(), translator)
            for cell in translated_df[col].astype(str)
        ]
    return translated_df
