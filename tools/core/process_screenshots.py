#!/usr/bin/env python3
"""
Core Tool: Screenshot Processor

Processes racing screenshots by:
1. Auto-detecting and cropping black bands from top
2. Resizing to specified width (default 860px)
3. Moving originals to processed folder

Usage:
    python tools/core/process_screenshots.py <directory> [--width 860]
    
Output: Processed images in same directory, originals moved to processed/
"""

import sys
import json
from pathlib import Path
from PIL import Image, ImageEnhance
import shutil


def detect_black_band_threshold(image, threshold=10):
    """
    Detect where the black band ends at the top of the image.
    
    Args:
        image: PIL Image object
        threshold: RGB value threshold (pixels darker than this are "black")
    
    Returns:
        Row number where black band ends (0 if no black band detected)
    """
    width, height = image.size
    pixels = image.load()
    
    # Check each row from top
    for y in range(height):
        # Sample across the width
        black_pixels = 0
        sample_points = min(20, width)  # Sample 20 points across
        
        for x in range(0, width, width // sample_points):
            pixel = pixels[x, y]
            # Check if pixel is dark (all RGB values below threshold)
            if isinstance(pixel, tuple):
                r, g, b = pixel[:3]  # Handle RGBA
                if r <= threshold and g <= threshold and b <= threshold:
                    black_pixels += 1
        
        # If less than 80% of samples are black, we've found the end
        if black_pixels < (sample_points * 0.8):
            return y
    
    return 0  # No black band found


def process_screenshot(input_path, output_path, target_width=860):
    """
    Process a single screenshot: crop black band and resize.
    
    Args:
        input_path: Path to input image
        output_path: Path to save processed image
        target_width: Target width in pixels
    
    Returns:
        Dictionary with processing results
    """
    try:
        img = Image.open(input_path)
        original_size = img.size
        
        # Handle HDR/color profile - convert to sRGB for proper display
        # This prevents dark images from HDR screenshots
        has_hdr_profile = False
        if img.mode in ('RGB', 'RGBA'):
            # Check if image has embedded color profile
            if 'icc_profile' in img.info:
                has_hdr_profile = True
                # Convert to standard RGB (removes ICC profile)
                img = img.convert('RGB')
                
                # Apply brightness boost for HDR → SDR conversion
                # HDR images typically need 1.3-1.5x brightness boost
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.4)  # 40% brightness boost
        
        # Detect and crop black band
        crop_top = detect_black_band_threshold(img)
        if crop_top > 0:
            # Crop from detected line to bottom
            img = img.crop((0, crop_top, img.width, img.height))
            cropped = True
        else:
            cropped = False
        
        # Calculate new height maintaining aspect ratio
        aspect_ratio = img.height / img.width
        target_height = int(target_width * aspect_ratio)
        
        # Resize using high-quality Lanczos resampling
        img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Save without embedded color profile (standard sRGB)
        # This ensures consistent display across devices
        img_resized.save(output_path, 'PNG', optimize=True, icc_profile=None)
        
        return {
            "success": True,
            "original_size": original_size,
            "cropped_pixels": crop_top,
            "cropped": cropped,
            "hdr_corrected": has_hdr_profile,
            "final_size": (target_width, target_height),
            "file_size_reduction": f"{(1 - Path(output_path).stat().st_size / Path(input_path).stat().st_size) * 100:.1f}%"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def process_directory(directory, target_width=860, move_originals=True):
    """
    Process all PNG screenshots in a directory.
    
    Args:
        directory: Path to directory containing screenshots
        target_width: Target width for resized images
        move_originals: Whether to move originals to processed folder
    
    Returns:
        Dictionary with batch processing results
    """
    screenshot_dir = Path(directory)
    
    if not screenshot_dir.exists():
        return {
            "success": False,
            "error": f"Directory not found: {directory}"
        }
    
    # Find all PNG files
    png_files = list(screenshot_dir.glob("*.png"))
    
    if not png_files:
        return {
            "success": False,
            "error": "No PNG files found in directory"
        }
    
    # Create processed directory if moving originals
    if move_originals:
        # Get the base directory (should be project root)
        base_dir = Path(__file__).parent.parent.parent
        processed_dir = base_dir / "data" / "processed" / "screenshots"
        processed_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        "success": True,
        "total_files": len(png_files),
        "processed": 0,
        "failed": 0,
        "files": []
    }
    
    for png_file in png_files:
        # Create temp output path
        temp_output = screenshot_dir / f"temp_{png_file.name}"
        
        # Process the screenshot
        result = process_screenshot(png_file, temp_output, target_width)
        
        if result["success"]:
            # Move original to processed if requested
            if move_originals:
                shutil.move(str(png_file), str(processed_dir / png_file.name))
            else:
                # Just delete original if not moving
                png_file.unlink()
            
            # Rename temp file to original name
            temp_output.rename(png_file)
            
            results["processed"] += 1
            results["files"].append({
                "filename": png_file.name,
                "status": "success",
                **result
            })
        else:
            # Clean up temp file if it exists
            if temp_output.exists():
                temp_output.unlink()
            
            results["failed"] += 1
            results["files"].append({
                "filename": png_file.name,
                "status": "failed",
                "error": result.get("error", "Unknown error")
            })
    
    return results


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python process_screenshots.py <directory> [--width 860]"
        }, indent=2))
        sys.exit(1)
    
    directory = sys.argv[1]
    
    # Parse optional width argument
    target_width = 860
    if "--width" in sys.argv:
        width_idx = sys.argv.index("--width")
        if len(sys.argv) > width_idx + 1:
            try:
                target_width = int(sys.argv[width_idx + 1])
            except ValueError:
                print(json.dumps({
                    "success": False,
                    "error": "Invalid width value"
                }, indent=2))
                sys.exit(1)
    
    results = process_directory(directory, target_width)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

