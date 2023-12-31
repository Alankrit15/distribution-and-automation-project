import csv
import math


with open("file.csv", 'r') as file:
    csvreader = csv.reader(file)
    imp = []
    for row in csvreader:
        length = len(row)
        x = float(row[-1])
        r = float(row[-2])
        z = complex(r, x)
        imp.append(z)

with open("load.csv", "r") as file1:
    reader = csv.reader(file1)
    voltage = []
    cur = []
    cnode = []
    for i in range(0, 33):
        voltage.append(11.5)
        cnode.append(0)
    i = 0

    # To find current
    for row in reader:
        length = len(row)
        p = float(row[length - 2])
        q = float(row[length - 1])
        load = complex(p, -q)
        current = load / voltage[i]
        cur.append(current)
        i += 1
    i = 0

    # To get current in each line
    for i in reversed(range(32)):
        cnode[i] = cnode[i + 1] + cur[i]

    # For losses in line:
    loss_arr = []
    for i in range(0, 32):
        current = math.sqrt(cnode[i].real**2 + cnode[i].imag**2)
        losses = current*current*imp[i].real
        loss_arr.append(losses)
        print(loss_arr[i])

    # For node voltage
    for i in range(0, 32):
        volt = voltage[i] - cnode[i]*imp[i]/1000
        voltage[i] = volt
        print(volt)


with open("output.csv", "w") as output:
    writer = csv.writer(output)
    writer.writerow(['From bus', 'To bus','Current', 'Impedance', 'Losses', 'Node_voltage'])
    with open("file.csv", "r") as file3:
        reader = csv.reader(file3)
        i = 0
        for row in reader:
            writer.writerow([row[1], row[2], cnode[i], imp[i], loss_arr[i], voltage[i]])
            i += 1
