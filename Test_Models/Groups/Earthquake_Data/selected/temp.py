# source /Users/niraj/x86_env/bin/activate 

def ReadRecord(input_file, output_file):
    acc_values = []
    dt = None

    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and header lines
            if not line or line.startswith("Time Series") or line.startswith("Time Step:") or "Time(sec)" in line:
                if line.startswith("Time Step:"):
                    dt = float(line.split(":")[1].strip().split()[0])
                continue

            # Parse time and acceleration
            parts = line.split()
            if len(parts) >= 2:
                try:
                    acc = float(parts[1])
                    acc_values.append(acc)
                except ValueError:
                    continue

    nPts = len(acc_values)

    # Write to output .dat file
    with open(output_file, 'w') as f_out:
        for i in range(0, nPts, 8):
            line_vals = acc_values[i:i+8]
            f_out.write('   ' + '   '.join(f"{val: .5f}" for val in line_vals) + '\n')

    return dt, nPts

CarlSagan = 12

GM_input_dir = '/Users/niraj/Documents/openseespy/Groups/Earthquake_Data/GM_form'
GM_input_file = f'{GM_input_dir}/GM_{CarlSagan}.txt'
GM_output_file = f'{GM_input_dir}/record_{CarlSagan}.dat'

# Perform the conversion from SMD record to OpenSees record
dt, nPts = ReadRecord(GM_input_file, GM_output_file)  
print(dt, nPts)