import os
import re
import os
import shutil
from pydub import AudioSegment
from glob import glob
from pathlib import Path

def clean_out_path(fpath):
    out_path = os.path.join(fpath, 'out')

    # Check if the directory exists
    if os.path.exists(out_path):
        # Cleanup: delete all files in the directory
        for filename in os.listdir(out_path):
            file_path = os.path.join(out_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    else:
        # Directory does not exist, so create it
        os.makedirs(out_path)

def split(audio, filename):
    ten_minutes = 20 * 60 * 1000
    pos = 0
    idx = 1
    while pos < len(audio):
        print("Saving {0}".format(filename.format(idx)))
        chunk = audio[pos:min(pos + ten_minutes, len(audio) - 1)]
        chunk.export(filename.format(idx), format="mp3")
        idx += 1
        pos += ten_minutes

if __name__ == "__main__":
    for fdir in ["2017", "2018"]:
        outdir = os.path.join(os.path.curdir, fdir)
        clean_out_path(outdir)
        for fname in glob("{0}/*.mp3".format(fdir)):
            print("Splitting {0}".format(fname))
            audio = AudioSegment.from_mp3(fname)
            outname = Path(os.path.splitext(fname)[0]).stem + " part {0}.mp3"
            split(audio, os.path.join(outdir, "out", outname))
