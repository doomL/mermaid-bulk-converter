import os
import subprocess
import tempfile
import argparse
import json
from pathlib import Path

def convert_mermaid_to_png(input_dir: str, output_dir: str, scale: float = 3):
    """
    Convert all Mermaid diagram files in input_dir to high-resolution PNG files in output_dir.
    
    Args:
        input_dir (str): Directory containing Mermaid diagram definition files
        output_dir (str): Directory where PNG files will be saved
        scale (float): Scale factor for the output PNG (default: 3)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all files from input directory
    input_files = Path(input_dir).glob('*.mmd')
    
    # Create a temporary config file with optimized settings
    config = {
        "puppeteerConfig": {
            "deviceScaleFactor": scale,
            "backgroundColor": "transparent"
        },
        "mermaid": {
            "fontSize": 14,
            "flowchart": {
                "htmlLabels": True,
                "padding": 8,
                "rankSpacing": 20,
                "nodeSpacing": 30,
                "diagramPadding": 8,
                "useMaxWidth": True,
                "wrap": True
            },
            "themeVariables": {
                "fontSize": "14px",
                "fontFamily": "arial",
                "lineHeight": 1
            }
        }
    }
    
    try:
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_file:
            json.dump(config, config_file, indent=2)
            config_file.flush()
            
            for input_file in input_files:
                # Create output filename
                output_file = Path(output_dir) / f"{input_file.stem}.png"
                
                try:
                    # Create a temporary file for mmdc processing
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as temp_file:
                        # Copy content to temp file
                        content = input_file.read_text()
                        # Add minimal directives to maintain layout
                        enhanced_content = f"""%%{{ init: {{ 'theme': 'default' }} }}%%
{content}"""
                        temp_file.write(enhanced_content)
                        temp_file.flush()
                        
                        # Construct mmdc command with optimized settings
                        cmd = [
                            'mmdc',
                            '-i', temp_file.name,
                            '-o', str(output_file),
                            '-b', 'transparent',
                            '-c', config_file.name,
                            '-w', str(int(1024 * (scale/3))),  # Base width scaled
                            '-H', str(int(768 * (scale/3)))    # Base height scaled
                        ]
                        
                        # Execute mmdc command
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True
                        )
                        
                        if result.returncode == 0:
                            print(f"Successfully converted {input_file.name} to high-res PNG")
                        else:
                            print(f"Error converting {input_file.name}: {result.stderr}")
                            
                except Exception as e:
                    print(f"Error processing {input_file.name}: {str(e)}")
                finally:
                    # Clean up temp file
                    if 'temp_file' in locals():
                        os.unlink(temp_file.name)
    finally:
        # Clean up config file
        if 'config_file' in locals():
            os.unlink(config_file.name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert Mermaid diagram files to high-resolution PNG')
    parser.add_argument('-i', '--input', required=True, help='Input directory containing .mmd files')
    parser.add_argument('-o', '--output', required=True, help='Output directory for PNG files')
    parser.add_argument('-s', '--scale', type=float, default=3.0, 
                        help='Scale factor for PNG resolution (default: 3.0)')
    
    args = parser.parse_args()
    
    convert_mermaid_to_png(args.input, args.output, args.scale)