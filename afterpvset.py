import math
import csv
import matplotlib.pyplot as plt
import pandas as pd

#Loading pervious node voltages and line current
df=pd.read_csv('op.csv')
total_node_volatge_beforepvset=(df['Node_voltage'].values.tolist())
total_node_current_beforepvset=df['Current'].values.tolist()
for i in range(len(total_node_volatge_beforepvset)):
    total_node_volatge_beforepvset[i]=complex(total_node_volatge_beforepvset[i])
    total_node_current_beforepvset[i]=complex(total_node_current_beforepvset[i])




def get_load_imp_arr(file2, load1):
    with open(file2, 'r') as file:
        csvreader = csv.reader(file)
        imp = []
        for row in csvreader:
            x = float(row[-1])
            r = float(row[-2])
            z = complex(r, x)
            imp.append(z)

    with open(load1, "r") as file1:
        reader = csv.reader(file1)
        load = []
        for row in reader:
            r = float(row[-2])
            reactive = float(row[-1])
            reactive=reactive-reactive/2.1
            load.append(complex(r, -reactive))
    return imp, load

def get_current(load, voltage, site_no):
    current = []
    cnode = []
    for i in range(site_no):
        curr = load[i]/voltage[i]
        current.append(curr)
        cnode.append(0)
    cnode.append(0)

    for i in reversed(range(site_no)):
        cnode[i] = cnode[i+1] + current[i]
    cnode.pop()
    return cnode


def get_losses(curr, impedance, site_no):
    loss_real = []
    loss_reactive = []
    for i in range(site_no):
        current = math.sqrt(curr[i].real ** 2 + curr[i].imag ** 2)
        losses = current * current * impedance[i].real
        losses2 = current * current * impedance[i].imag
        loss_real.append(losses)
        loss_reactive.append(losses2)
    return loss_real, loss_reactive


# Node voltages
def get_node_voltages(current, impedance, prv_volt):
    n_voltage = []
    for i in range(len(current)):
        volt = prv_volt - current[i]*impedance[i]
        n_voltage.append(volt)
        prv_volt = volt
    return n_voltage


admin_imp, admin_load = get_load_imp_arr("admin_impedance.csv", "admin_load.csv")
cse_imp, cse_load = get_load_imp_arr("cse_impedance.csv", "cse_load.csv")
h3_imp, h3_load = get_load_imp_arr("h3_impedance.csv", "h3_load.csv")
h4_imp, h4_load = get_load_imp_arr("h4_impedance.csv", "h4_load.csv")
lhc_imp, lhc_load = get_load_imp_arr("lhc_impedance.csv", "lhc_load.csv")
main_imp, main_load = get_load_imp_arr("file.csv", "load.csv")

voltage = []
for i in range(32):
    voltage.append(11.5)

admin_line_current = get_current(admin_load, voltage, len(admin_load))
cse_line_current = get_current(cse_load, voltage, len(cse_load))
h3_line_current = get_current(h3_load, voltage, len(h3_load))
h4_line_current = get_current(h4_load, voltage, len(h4_load))
lhc_line_current = get_current(lhc_load, voltage, len(lhc_load))

# h4 total current
for i in range(len(h4_load)):
    h4_line_current[i] = h4_line_current[i] + h3_line_current[0] + lhc_line_current[0]

# tnp line current
tnp_load = complex(90, -40)
tnp_line_current = tnp_load/11.5 + h4_line_current[0] + cse_line_current[0]

# Nit substation line current
sub_load = complex(100, -60)
nit_substation_line_current = sub_load/11.5 + admin_line_current[0] + tnp_line_current

# total line current
total_line_current = []
total_line_current.append(nit_substation_line_current)
total_line_current.append(tnp_line_current)
total_line_current = total_line_current + h4_line_current + h3_line_current + admin_line_current + cse_line_current + lhc_line_current

# losses
real_loss, reactive_loss = get_losses(total_line_current, main_imp, 32)

# Node voltage
admin_node_voltage = get_node_voltages(admin_line_current, admin_imp, 11500)
tnp_node_voltage = 11500 - tnp_line_current*complex(0.493, 0.2511)
cse_node_voltage = get_node_voltages(cse_line_current, cse_imp, tnp_node_voltage)
h4_node_voltage = get_node_voltages(h4_line_current, h4_imp, tnp_node_voltage)
h3_node_voltage = get_node_voltages(h3_line_current, h3_imp, h4_node_voltage[-1])
lhc_node_voltage = get_node_voltages(lhc_line_current, lhc_imp, h4_node_voltage[-1])

# total node voltages combined
total_node_voltage=[]
total_node_voltage.append(11500)
total_node_voltage.append(tnp_node_voltage)
total_node_voltage=total_node_voltage+h4_node_voltage+h3_node_voltage+admin_node_voltage+cse_node_voltage+lhc_node_voltage

# output
with open("opnew.csv", "w") as output:
    writer = csv.writer(output)
    writer.writerow(['From bus', 'To bus', 'Current', 'Impedance', 'I2RLosses','I2xLosses','Node_voltage'])
    with open("file.csv", "r") as file3:
        reader = csv.reader(file3)
        i = 0
        for row in reader:
            writer.writerow([row[1], row[2], total_line_current[i], main_imp[i], real_loss[i],reactive_loss[i], total_node_voltage[i]])
            i += 1


# voltage profile
x=[]
for i in range(1,33):
    x.append(i)
plt.plot(x,total_node_voltage,color='r',label="after pvset is installed")
# plt.plot(x,total_node_volatge_beforepvset,color='g',label="before pvset is installed")
plt.xticks(x)
plt.xlabel("NODE")
plt.ylabel("VOLTAGE")
plt.title("VOLTAGE PROFILE")
plt.show()

current profile
y=[]
for i in range(1,33):
    y.append(i)
plt.plot(y,total_line_current,color='r')
plt.plot(y,total_node_current_beforepvset,color='g')
plt.xticks(y)
plt.xlabel("NODE")
plt.ylabel("CURRENT")
plt.title("CURRENT PROFILE")
plt.show()
plt.plot(x,real_loss,color='r',label='real')
plt.plot(x,reactive_loss,color='g',label='reactive')
plt.xticks(x)
plt.xlabel("NODE")
plt.ylabel("LOSSES")
plt.title("LOSSES IN THE LINE")
plt.show()
