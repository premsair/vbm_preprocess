#!/usr/bin/env python
#corr_added.py

# Bunch of module imports
from nipype.interfaces.spm.utils import DicomImport, ApplyTransform 
from nipype.interfaces.spm import NewSegment, Smooth
from nipype.interfaces.io import DataSink
from nipype.interfaces.utility import Function
import nipype.pipeline.engine as pe
import glob, json, os, sys, argparse
import correlation

# Collecting arguments from nodejs module
parser = argparse.ArgumentParser(description='Script for VBM Preprocessing')
parser.add_argument('--run', type=str,  help='Args from coinstac')
args = parser.parse_args()
args.run = json.loads(args.run)

# Setting the parameters from collected arguments
username = args.run['username']
userdata = args.run['userData']
dicom_dir = userdata.get('dirs')[0]
dicom_path = dicom_dir+"/*.dcm"
transf_mat_path = userdata.get('mat_path')
spm_path = userdata.get('spm_path')
tpm_path = "/".join([spm_path, 'tpm', 'TPM.nii'])
out_path = userdata.get('out_path', None)

if out_path is None: # If no output path provided, it is defaulted to dicom's parent dir
	out_path = os.path.dirname(dicom_dir)

if 'remoteResult' in args.run and \
    'data' in args.run['remoteResult'] and \
    username in args.run['remoteResult']['data']:
    sys.exit(0); # no-op!  we already contributed our data

# Dicom Converter node and settings
converter = pe.Node(interface = DicomImport(), name = 'converter')
converter.inputs.paths = spm_path
converter.inputs.in_files = glob.glob(dicom_path)
converter.inputs.format = "nii"
converter.inputs.output_dir = out_path+"/vbm_spm12"

# Reorientation node and settings 
reorient = pe.Node(interface = ApplyTransform(), name = 'reorient')
reorient.inputs.paths = spm_path
reorient.inputs.mat = transf_mat_path
reorient.inputs.out_file = out_path+"/vbm_spm12/Re.nii"

# Segementation Node and settings
segmentation = pe.Node(interface = NewSegment(), name = 'segmentation')
segmentation.inputs.paths = spm_path
segmentation.inputs.channel_info = (0.0001, 60, (False, False))
Tis1 = ((tpm_path,1),1,(True,False),(True,True))
Tis2 = ((tpm_path,2),1,(True,False),(True,True))
Tis3 = ((tpm_path,3),2,(True,False),(True,True))
Tis4 = ((tpm_path,4),3,(True,False),(True,True))
Tis5 = ((tpm_path,5),4,(True,False),(True,True))
Tis6 = ((tpm_path,6),2,(True,False),(True,True))
segmentation.inputs.tissues = [Tis1,Tis2,Tis3,Tis4,Tis5,Tis6]

# Function & Node to transform the list of normalized class images to a compatible version for smoothing
def transform_list(normalized_class_images):
	return [each[0] for each in normalized_class_images]

list_normalized_images = pe.Node(interface = Function(input_names = 'normalized_class_images',\
	                                                  output_names = 'list_norm_images', function = transform_list),\
                                 name = 'list_normalized_images')

# Smoothing Node & Settings
smoothing = pe.Node(interface = Smooth(), name = 'smoothing')
smoothing.inputs.paths = spm_path
smoothing.inputs.fwhm = [10, 10, 10]

# Datsink Node that collects segmented, smoothed files and writes to out_path
datasink = pe.Node(interface = DataSink(), name = 'sinker')
datasink.inputs.base_directory = out_path

# Workflow and it's connections
vbm_preprocess = pe.Workflow(name = "vbm_preprocess")
vbm_preprocess.connect([(converter, reorient, [('out_files','in_file')]),\
	                    (reorient, segmentation, [('out_file', 'channel_files')]),\
	                    (segmentation, list_normalized_images, [('normalized_class_images','normalized_class_images')]),\
	                    (list_normalized_images, smoothing, [('list_norm_images','in_files')]),\
	                    (segmentation, datasink, [('modulated_class_images','vbm_spm12'),('native_class_images','vbm_spm12.@1'),\
	                                             ('normalized_class_images','vbm_spm12.@2'),('transformation_mat','vbm_spm12.@3')]),\
	                    (smoothing, datasink, [('smoothed_files','vbm_spm12.@4')])])

try:
    # Run the workflow
    sys.stderr.write("running vbm workflow")
    res = vbm_preprocess.run()

except:
    # If fails raise the excpetion and set status False
    status = False

else:
    # If succeds, set status True
    status = True
        
finally:
    # Finally , write the status to .json object and calculate correlation coefficent
    segmented_file = glob.glob(out_path+"/vbm_spm12/swc1*nii")[0]
    corr_value = correlation.get_corr(tpm_path,segmented_file)
    sys.stdout.write(json.dumps({"vbm_preprocess" : status}, sort_keys=True, indent=4, separators=(',', ': ')))