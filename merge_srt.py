from glob import glob
import os

def adjust_timestamps(srt_filename, offset=20):
    output = []
    with open(srt_filename, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if "-->" in line:  # this line contains timestamps
            start, end = line.strip().split(" --> ")

            start_h, start_m, start_s_ms = start.split(':')
            start_s, start_ms = start_s_ms.split(',')
            end_h, end_m, end_s_ms = end.split(':')
            end_s, end_ms = end_s_ms.split(',')

            # Convert to float
            start_h, start_m, start_s, start_ms = map(float, [start_h, start_m, start_s, start_ms])
            end_h, end_m, end_s, end_ms = map(float, [end_h, end_m, end_s, end_ms])

            # Assume each part is 20 minutes long, adjust accordingly
            start_m += offset
            end_m += offset

            # Fix if minutes exceed 60
            if start_m >= 60:
                start_h += 1
                start_m -= 60
            if end_m >= 60:
                end_h += 1
                end_m -= 60

            start = f"{int(start_h):02}:{int(start_m):02}:{int(start_s):02},{int(start_ms):03}"
            end = f"{int(end_h):02}:{int(end_m):02}:{int(end_s):02},{int(end_ms):03}"
            output.append(f"{start} --> {end}\n")
        else:
            output.append(line)

    return output

if __name__ == "__main__":
    for yr in ['2017', '2018']:
        for fname in glob("./{0}/*.mp3".format(yr)):
            # parse filename and extension of mp3 file
            name, ext = os.path.splitext(os.path.basename(fname))
            i = 0
            output = ""
            print("Processing {0}".format(fname))
            while True:
                i = i + 1
                srt_filename = "./{0}/out/{1} part {2}.srt".format(yr, name, i)
                print(srt_filename)
                if os.path.exists(srt_filename):
                    output = output + "".join(adjust_timestamps(srt_filename, offset=(i-1)*20))
                else:
                    break
            if output:
                with open("./{0}/{1}.srt".format(yr, name), 'w') as f:
                    f.writelines(output)
    print("Done!")
