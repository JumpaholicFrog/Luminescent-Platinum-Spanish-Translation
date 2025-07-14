import json
import sys
from typing import Dict, List, Any

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{file_path}': {e}")
        sys.exit(1)

def save_json_file(data: Dict[str, Any], file_path: str) -> None:
    """Save data to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        print(f"Successfully saved processed data to '{file_path}'")
    except Exception as e:
        print(f"Error saving file '{file_path}': {e}")
        sys.exit(1)

def split_text_by_length(text: str, max_length: int) -> List[str]:
    """
    Split text into chunks that don't exceed max_length, respecting word boundaries.
    
    Args:
        text: The text to split
        max_length: Maximum length for each chunk
        
    Returns:
        List of text chunks
    """
    if not text.strip():
        return []
    
    words = text.split()
    chunks = []
    current_chunk = ""
    
    for word in words:
        # Check if adding this word would exceed the limit
        test_chunk = current_chunk + (" " if current_chunk else "") + word
        
        if len(test_chunk) <= max_length:
            current_chunk = test_chunk
        else:
            # If current_chunk is not empty, save it and start a new chunk
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = word
            else:
                # If a single word exceeds max_length, we still need to include it
                # This shouldn't happen with normal text, but we handle it gracefully
                chunks.append(word)
                current_chunk = ""
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def extract_all_text_from_word_data_array(word_data_array: List[Dict[str, Any]]) -> str:
    """
    Extract and join all text from 'str' attributes in wordDataArray.
    
    Args:
        word_data_array: List of word data objects
        
    Returns:
        Joined text string
    """
    text_parts = []
    
    for word_data in word_data_array:
        if "str" in word_data and word_data["str"]:
            text_parts.append(word_data["str"])
    
    return " ".join(text_parts)

def create_word_data_entry(text: str, pattern_id: int, event_id: int, template_entry: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create a word data entry with the specified text and IDs, preserving other attributes.
    
    Args:
        text: The text content
        pattern_id: Pattern ID value
        event_id: Event ID value
        template_entry: Original entry to use as template for other attributes
        
    Returns:
        Word data entry dictionary
    """
    if template_entry:
        # Start with a copy of the template entry
        new_entry = template_entry.copy()
        # Override the specific fields
        new_entry["str"] = text
        new_entry["patternID"] = pattern_id
        new_entry["eventID"] = event_id
        return new_entry
    else:
        # Fallback if no template is available
        return {
            "str": text,
            "patternID": pattern_id,
            "eventID": event_id,
            "tagIndex": -1,
            "tagValue": 0.0,
            "strWidth": 0.0
        }

def process_label_data(data: Dict[str, Any], max_length: int) -> None:
    """
    Process the labelDataArray to split text entries.
    
    Args:
        data: The JSON data containing labelDataArray
        max_length: Maximum length for each text chunk
    """
    if "labelDataArray" not in data:
        print("Error: File must contain 'labelDataArray' key")
        sys.exit(1)
    
    processed_labels = 0
    
    for label in data["labelDataArray"]:
        if "wordDataArray" not in label:
            print(f"Warning: Label with labelIndex {label.get('labelIndex', 'unknown')} has no wordDataArray")
            continue
        
        word_data_array = label["wordDataArray"]
        
        # Extract all text from the current wordDataArray
        full_text = extract_all_text_from_word_data_array(word_data_array)
        
        if not full_text.strip():
            # If no text found, create empty wordDataArray
            label["wordDataArray"] = []
            continue
        
        # Use the first entry as a template for preserving attributes
        template_entry = word_data_array[0] if word_data_array else None
        
        # Split the text into chunks
        text_chunks = split_text_by_length(full_text, max_length)
        
        # Create new wordDataArray with split text
        new_word_data_array = []
        
        for i, chunk in enumerate(text_chunks):
            if i == len(text_chunks) - 1:  # Last entry
                entry = create_word_data_entry(chunk, pattern_id=0, event_id=7, template_entry=template_entry)
            else:  # All other entries
                entry = create_word_data_entry(chunk, pattern_id=7, event_id=1, template_entry=template_entry)
            
            new_word_data_array.append(entry)
        
        # Replace the original wordDataArray
        label["wordDataArray"] = new_word_data_array
        processed_labels += 1
        
        print(f"Processed labelIndex {label.get('labelIndex', 'unknown')}: "
              f"{len(text_chunks)} chunks created from {len(full_text)} characters")
    
    print(f"\nProcessing complete! {processed_labels} labels processed.")

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file> [output_file]")
        print("  input_file: JSON file to process")
        print("  output_file: Optional output file (default: overwrites input_file)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file
    
    # Define the maximum length based on the example text
    example_text = "tipo Eléctrico y los Pokémon que están en contacto con"
    max_length = len(example_text)
    
    print(f"Maximum text length per chunk: {max_length} characters")
    print(f"Example text: '{example_text}'")
    print(f"Processing file: {input_file}")
    print("-" * 50)
    
    # Load and process the data
    data = load_json_file(input_file)
    process_label_data(data, max_length)
    
    # Save the result
    save_json_file(data, output_file)

if __name__ == "__main__":
    main()