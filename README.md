# Description

> Version: 0.0.1
> python 2.x,3.x

Project easy Modbus.

In this package you can connect in TCP, RTU or ASC mode in modbus usign a mask to collect everything from your device

## Donate

**PIX**: +55 31 99101-8619

## Contact

**URL**: [http://estaleiroweb.com.br](http://estaleiroweb.com.br)

**GIT**: [https://github.com/estaleiroweb/emodbus](https://github.com/estaleiroweb/emodbus)

# Instalation

> pip install emodbus

# Upgrade

> pip install emodbus -upgrade

# Use

```python
import emodbus as emb

# connect to bus of devices
tcp = emb.ConnTCP('192.168.1.45')
rtu = emb.ConnRTU('COM4')

# define default MIB
# {name: (Address:int,functionCode:int,callbackFunction_modbustype:'None|str|tuple|list'),....},
addrs = {
    'Temperature': [1, 4, ('Dec', {'dec': 1})],
    'Humidy': [2, 4, ['Dec', {'dec': 1}]],
    'TemperatureRaw': [1, 4],
    'HumidyRaw': [2, 4],
}
emb.Conn.defSlave[1] = addrs

# Read MIB of any slave of the connection
print('TCP MIB Slave 1', tcp.slave(1)(), sep=':')
print()

# define MIB of connection/slave
tcp.slave(1, addrs)

# read all MIB
slaves = [1]
for slave in slaves:
    print('Read All Slave ', slave)
    print('TCP',tcp.read(slave), sep=':')
    print('RTU',rtu.read(slave), sep=':')
print()

# read only some address
addr = ['Temperature', 'xxxxxxxxxx', 'Humidy']
for slave in slaves:
    print('Read Slave '+str(slave), addr, sep=':')
    print('TCP',tcp.read(slave, addr), sep=':')
    print('RTU',rtu.read(slave, addr), sep=':')
```
