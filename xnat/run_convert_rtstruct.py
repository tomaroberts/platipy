import sys
import os
from platipy.dicom.io.rtstruct_to_nifti import convert_rtstruct

print(f"Executing: run_convert_rtstruct.py {sys.argv[1]} {sys.argv[2]} {sys.argv[3]} {sys.argv[4]} {sys.argv[5]} ...")
# print(f"Current directory: {os.getcwd()}")
# print(f"Directory content: {os.listdir()}")

INPUT_DCM_DIRNAME = sys.argv[1]
INPUT_RT_FILENAME = sys.argv[2]
OUTPUT_NII_DIRNAME = sys.argv[3]
OUTPUT_NII_IMG_FILENAME = sys.argv[4]
OUTPUT_FILE_PREFIX = sys.argv[5]

convert_rtstruct(
    dcm_img=INPUT_DCM_DIRNAME,
    dcm_rt_file=INPUT_RT_FILENAME,
    output_dir=OUTPUT_NII_DIRNAME,
    output_img=OUTPUT_NII_IMG_FILENAME,
    prefix=OUTPUT_FILE_PREFIX,  # applies to contour files only, not image file
)